"""
ML Prediction API Endpoints
Serves delay predictions using trained ML models
"""

from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from datetime import datetime
import joblib
import numpy as np
import os

from services.llm_service import explain_delay_prediction
from core.dependencies import get_current_user
from db.models import User

router = APIRouter()

# Model paths
MODEL_DIR = "ml/models"
BEST_MODEL_PATH = f"{MODEL_DIR}/best_model.pkl"
FEATURE_COLUMNS_PATH = f"{MODEL_DIR}/feature_columns.pkl"
LABEL_ENCODER_TYPE_PATH = f"{MODEL_DIR}/label_encoder_type.pkl"
LABEL_ENCODER_STAGE_PATH = f"{MODEL_DIR}/label_encoder_stage.pkl"

# Global model cache
_model_cache = {}


def load_models():
    """Load trained models and encoders"""
    if _model_cache:
        return _model_cache
    
    try:
        _model_cache['model'] = joblib.load(BEST_MODEL_PATH)
        _model_cache['feature_columns'] = joblib.load(FEATURE_COLUMNS_PATH)
        _model_cache['label_encoder_type'] = joblib.load(LABEL_ENCODER_TYPE_PATH)
        _model_cache['label_encoder_stage'] = joblib.load(LABEL_ENCODER_STAGE_PATH)
        _model_cache['loaded'] = True
        return _model_cache
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"ML models not loaded. Please train models first. Error: {str(e)}"
        )


# Request/Response Models

class PredictionRequest(BaseModel):
    """Request model for delay prediction"""
    request_type: str = Field(..., description="Type of request (certificate, hostel, it_support, library, exam, transcript)")
    priority: int = Field(..., ge=1, le=3, description="Priority level (1=low, 2=medium, 3=high)")
    created_hour: int = Field(..., ge=0, le=23, description="Hour of request creation (0-23)")
    created_day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Mon, 6=Sun)")
    handler_workload: int = Field(default=3, ge=0, description="Current handler workload")
    stage_created_duration: float = Field(default=2.0, ge=0, description="Expected created stage duration")
    stage_assigned_duration: float = Field(default=4.0, ge=0, description="Expected assigned stage duration")
    stage_verified_duration: float = Field(default=6.0, ge=0, description="Expected verified stage duration")
    stage_approved_duration: float = Field(default=8.0, ge=0, description="Expected approved stage duration")
    stage_processed_duration: float = Field(default=12.0, ge=0, description="Expected processed stage duration")
    final_stage: str = Field(default="completed", description="Expected final stage")

    class Config:
        json_schema_extra = {
            "example": {
                "request_type": "certificate",
                "priority": 2,
                "created_hour": 14,
                "created_day_of_week": 3,
                "handler_workload": 5,
                "stage_created_duration": 2.0,
                "stage_assigned_duration": 4.5,
                "stage_verified_duration": 6.0,
                "stage_approved_duration": 8.0,
                "stage_processed_duration": 15.0,
                "final_stage": "completed"
            }
        }


class PredictionResponse(BaseModel):
    """Response model for delay prediction"""
    prediction_score: float = Field(..., description="Probability of delay (0-1)")
    is_likely_delayed: bool = Field(..., description="Whether delay is likely (>0.5)")
    confidence: str = Field(..., description="Confidence level (low/medium/high)")
    explanation: str = Field(..., description="Human-readable explanation")
    contributing_factors: list = Field(..., description="Key factors contributing to prediction")
    recommendation: str = Field(..., description="Actionable recommendation")
    model_name: str = Field(..., description="Name of ML model used")
    timestamp: str = Field(..., description="Prediction timestamp")


class ModelInfo(BaseModel):
    """Model information response"""
    model_loaded: bool
    model_type: str
    feature_count: int
    model_file: str
    last_trained: Optional[str]


def engineer_prediction_features(request: PredictionRequest, models: Dict) -> np.ndarray:
    """
    Engineer features for prediction matching training pipeline
    
    Args:
        request: Prediction request data
        models: Dictionary containing loaded models and encoders
        
    Returns:
        Feature array ready for prediction
    """
    
    # SLA hours mapping
    sla_mapping = {
        'certificate': 72,
        'hostel': 48,
        'it_support': 24,
        'library': 48,
        'exam': 96,
        'transcript': 120
    }
    
    # Encode categorical variables
    try:
        request_type_encoded = models['label_encoder_type'].transform([request.request_type])[0]
    except:
        request_type_encoded = 0
    
    try:
        final_stage_encoded = models['label_encoder_stage'].transform([request.final_stage])[0]
    except:
        final_stage_encoded = 5  # Default to 'completed'
    
    # Derive features
    is_weekend = 1 if request.created_day_of_week >= 5 else 0
    is_peak_hour = 1 if request.created_hour in [10, 11, 14, 15, 16] else 0
    is_business_hours = 1 if 8 <= request.created_hour <= 17 else 0
    is_high_priority = 1 if request.priority == 3 else 0
    is_low_priority = 1 if request.priority == 1 else 0
    high_workload = 1 if request.handler_workload > 5 else 0
    
    sla_hours = sla_mapping.get(request.request_type, 48)
    
    total_stage_time = (
        request.stage_created_duration +
        request.stage_assigned_duration +
        request.stage_verified_duration +
        request.stage_approved_duration +
        request.stage_processed_duration
    )
    
    # Build feature array in correct order
    features = [
        request_type_encoded,
        request.priority,
        request.created_hour,
        request.created_day_of_week,
        is_weekend,
        is_peak_hour,
        is_business_hours,
        is_high_priority,
        is_low_priority,
        request.handler_workload,
        high_workload,
        sla_hours,
        request.stage_created_duration,
        request.stage_assigned_duration,
        request.stage_verified_duration,
        request.stage_approved_duration,
        request.stage_processed_duration,
        total_stage_time,
        final_stage_encoded
    ]
    
    return np.array(features).reshape(1, -1)


def analyze_contributing_factors(request: PredictionRequest, prediction_score: float) -> list:
    """Analyze key factors contributing to prediction"""
    factors = []
    
    total_duration = (
        request.stage_created_duration +
        request.stage_assigned_duration +
        request.stage_verified_duration +
        request.stage_approved_duration +
        request.stage_processed_duration
    )
    
    sla_mapping = {'certificate': 72, 'hostel': 48, 'it_support': 24, 
                   'library': 48, 'exam': 96, 'transcript': 120}
    sla = sla_mapping.get(request.request_type, 48)
    
    # For LOW delay probability - list positive factors
    if prediction_score < 0.3:
        if request.priority == 3:
            factors.append("High priority level")
        
        if request.handler_workload <= 3:
            factors.append(f"Low handler workload ({request.handler_workload} concurrent requests)")
        
        if 9 <= request.created_hour <= 16:
            factors.append("Submission during optimal business hours")
        
        if request.created_day_of_week < 5:
            factors.append("Early week submission")
        
        if total_duration < sla * 0.7:
            factors.append(f"Expected duration well below SLA ({total_duration:.1f}/{sla} hours)")
    
    # For HIGH delay probability - list negative factors
    else:
        if request.handler_workload > 5:
            factors.append(f"High handler workload ({request.handler_workload} concurrent requests)")
        
        if request.priority == 1:
            factors.append("Low priority level")
        
        if request.created_hour < 8 or request.created_hour > 17:
            factors.append("Submission outside business hours")
        
        if request.created_day_of_week >= 5:
            factors.append("Weekend submission")
        elif request.created_day_of_week == 4:
            factors.append("End-of-week submission")
        
        if total_duration > sla * 0.8:
            factors.append(f"Expected duration near SLA limit ({total_duration:.1f}/{sla} hours)")
    
    return factors if factors else ["Normal processing conditions"]


def generate_recommendation(request: PredictionRequest, prediction_score: float) -> str:
    """Generate actionable recommendation based on prediction"""
    
    if prediction_score > 0.7:
        if request.priority < 3:
            return "Consider escalating to high priority or contacting the admin office directly."
        else:
            return "Monitor closely and follow up with admin office within 24 hours."
    elif prediction_score > 0.5:
        return "Consider following up with the admin office if time-sensitive."
    else:
        return "Request should be processed within expected timeframe. No action needed."


@router.post("/delay", response_model=PredictionResponse)
async def predict_delay(
    request: PredictionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Predict delay probability for a service request
    
    Requires authentication. Uses trained ML model to predict if a request
    will be delayed beyond SLA, with explainable AI insights.
    """
    
    try:
        # Load models
        models = load_models()
        
        # Engineer features
        features = engineer_prediction_features(request, models)
        
        # Make prediction
        prediction_score = float(models['model'].predict_proba(features)[0][1])
        is_likely_delayed = prediction_score > 0.5
        
        # Determine confidence
        if abs(prediction_score - 0.5) > 0.3:
            confidence = "high"
        elif abs(prediction_score - 0.5) > 0.15:
            confidence = "medium"
        else:
            confidence = "low"
        
        # Generate explanation using LLM
        explanation = explain_delay_prediction(
            request_type=request.request_type,
            priority=request.priority,
            prediction_score=prediction_score,
            features={
                'created_hour': request.created_hour,
                'created_day_of_week': request.created_day_of_week,
                'handler_workload': request.handler_workload,
                'sla_hours': {'certificate': 72, 'hostel': 48, 'it_support': 24, 
                             'library': 48, 'exam': 96, 'transcript': 120}.get(request.request_type, 48)
            }
        )
        
        # Analyze contributing factors
        factors = analyze_contributing_factors(request, prediction_score)
        
        # Generate recommendation
        recommendation = generate_recommendation(request, prediction_score)
        
        # Get model name
        model_name = type(models['model']).__name__
        
        return PredictionResponse(
            prediction_score=round(prediction_score, 4),
            is_likely_delayed=is_likely_delayed,
            confidence=confidence,
            explanation=explanation,
            contributing_factors=factors,
            recommendation=recommendation,
            model_name=model_name,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.get("/model-info", response_model=ModelInfo)
async def get_model_info():
    """
    Get information about the loaded ML model
    
    Public endpoint that returns model metadata without requiring authentication.
    """
    
    try:
        if not os.path.exists(BEST_MODEL_PATH):
            return ModelInfo(
                model_loaded=False,
                model_type="None",
                feature_count=0,
                model_file="Not found",
                last_trained=None
            )
        
        models = load_models()
        model_name = type(models['model']).__name__
        feature_count = len(models['feature_columns'])
        
        # Get last modified time
        mod_time = os.path.getmtime(BEST_MODEL_PATH)
        last_trained = datetime.fromtimestamp(mod_time).isoformat()
        
        return ModelInfo(
            model_loaded=True,
            model_type=model_name,
            feature_count=feature_count,
            model_file=BEST_MODEL_PATH,
            last_trained=last_trained
        )
        
    except Exception as e:
        return ModelInfo(
            model_loaded=False,
            model_type="Error",
            feature_count=0,
            model_file=str(e),
            last_trained=None
        )


@router.post("/batch", response_model=list[PredictionResponse])
async def predict_delay_batch(
    requests: list[PredictionRequest],
    current_user: User = Depends(get_current_user)
):
    """
    Batch prediction for multiple requests
    
    Requires authentication. Predicts delay for multiple requests in one call.
    Limited to 50 requests per batch.
    """
    
    if len(requests) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch size limited to 50 requests"
        )
    
    results = []
    for req in requests:
        try:
            result = await predict_delay(req, current_user)
            results.append(result)
        except Exception as e:
            # Continue with other predictions even if one fails
            continue
    
    return results


@router.get("/health")
async def prediction_health_check():
    """
    Health check for prediction service

    Public endpoint to verify prediction service is operational.
    """

    model_exists = os.path.exists(BEST_MODEL_PATH)

    return {
        "status": "healthy" if model_exists else "degraded",
        "model_loaded": model_exists,
        "timestamp": datetime.now().isoformat()
    }


# ─── Option A: Retrain endpoint ───────────────────────────────────────────────

class RetrainResponse(BaseModel):
    status:        str
    message:       str
    models_trained: List[str]
    best_model:    str
    timestamp:     str


def _do_retrain() -> RetrainResponse:
    """
    Retrain all ML models on the latest CSV data.
    Saves updated .pkl files to ml/models/.
    """
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.svm import SVC
    from sklearn.neural_network import MLPClassifier
    from sklearn.metrics import f1_score
    import warnings
    warnings.filterwarnings("ignore")

    DATA_FILE    = "data/raw/synthetic_requests.csv"
    RANDOM_STATE = 42

    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"Training data not found: {DATA_FILE}")

    df = pd.read_csv(DATA_FILE)
    df = df[df["is_completed"] == 1].copy()

    # Feature engineering
    le_type  = LabelEncoder()
    le_stage = LabelEncoder()
    df["request_type_encoded"] = le_type.fit_transform(df["request_type"])
    df["final_stage_encoded"]  = le_stage.fit_transform(df["final_stage"])

    df["is_weekend"]       = (df["created_day_of_week"] >= 5).astype(int)
    df["is_peak_hour"]     = df["created_hour"].isin([10, 11, 14, 15, 16]).astype(int)
    df["is_business_hours"]= df["created_hour"].between(8, 17).astype(int)
    df["is_high_priority"] = (df["priority"] == 3).astype(int)
    df["is_low_priority"]  = (df["priority"] == 1).astype(int)
    df["high_workload"]    = (df["handler_workload"] > 5).astype(int)
    df["total_stage_time"] = (
        df["stage_created_duration"] + df["stage_assigned_duration"] +
        df["stage_verified_duration"] + df["stage_approved_duration"] +
        df["stage_processed_duration"]
    )

    feature_columns = [
        "request_type_encoded", "priority", "created_hour", "created_day_of_week",
        "is_weekend", "is_peak_hour", "is_business_hours", "is_high_priority",
        "is_low_priority", "handler_workload", "high_workload", "sla_hours",
        "stage_created_duration", "stage_assigned_duration", "stage_verified_duration",
        "stage_approved_duration", "stage_processed_duration", "total_stage_time",
        "final_stage_encoded",
    ]

    X = df[feature_columns]
    y = df["is_delayed"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    models_to_train = {
        "Logistic Regression": LogisticRegression(random_state=RANDOM_STATE, max_iter=1000),
        "Random Forest":       RandomForestClassifier(n_estimators=100, max_depth=10,
                                                      random_state=RANDOM_STATE, n_jobs=-1),
        "Gradient Boosting":   GradientBoostingClassifier(n_estimators=100, max_depth=5,
                                                          random_state=RANDOM_STATE),
        "SVM":                 SVC(kernel="rbf", probability=True, random_state=RANDOM_STATE),
        "Neural Network":      MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=300,
                                             random_state=RANDOM_STATE),
    }

    results     = {}
    best_name   = None
    best_f1     = 0.0

    for name, model in models_to_train.items():
        use_scaled = name in ("SVM", "Neural Network", "Logistic Regression")
        Xtr = X_train_s if use_scaled else X_train
        Xte = X_test_s  if use_scaled else X_test
        model.fit(Xtr, y_train)
        f1 = f1_score(y_test, model.predict(Xte))
        results[name] = {"model": model, "f1": f1}
        if f1 > best_f1:
            best_f1, best_name = f1, name

    # Save everything
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(results[best_name]["model"], BEST_MODEL_PATH)
    for name, r in results.items():
        safe = name.lower().replace(" ", "_")
        joblib.dump(r["model"], f"{MODEL_DIR}/{safe}.pkl")
    joblib.dump(feature_columns, FEATURE_COLUMNS_PATH)
    joblib.dump(scaler,          f"{MODEL_DIR}/scaler.pkl")
    joblib.dump(le_type,         LABEL_ENCODER_TYPE_PATH)
    joblib.dump(le_stage,        LABEL_ENCODER_STAGE_PATH)

    # Invalidate in-memory cache
    _model_cache.clear()

    return RetrainResponse(
        status="success",
        message=f"Retrained 5 models. Best: {best_name} (F1={best_f1:.4f})",
        models_trained=list(results.keys()),
        best_model=best_name,
        timestamp=datetime.now().isoformat(),
    )


@router.post("/retrain", response_model=RetrainResponse)
async def retrain_models(
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
):
    """
    Retrain all 5 ML models (LR, RF, GB, SVM, MLP) on the latest data.
    Saves the best model as best_model.pkl.
    Admin-accessible – returns immediately after kicking off training.
    """
    from core.dependencies import require_admin
    from db.models import UserRole
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        result = _do_retrain()
        return result
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Retraining failed: {str(exc)}")

