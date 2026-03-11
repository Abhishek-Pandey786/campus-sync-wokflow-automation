"""
Week 5 + Option C - ML Model Training Script
Trains 5 ML models on synthetic data and selects the best performer:
  Logistic Regression, Random Forest, Gradient Boosting, SVM, Neural Network
"""

import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score
)
import warnings
warnings.filterwarnings('ignore')

# Configuration
DATA_FILE = "data/raw/synthetic_requests.csv"
MODEL_DIR = "backend/ml/models"
REPORT_FILE = "backend/ml/training_report.txt"
TEST_SIZE = 0.2
RANDOM_STATE = 42


def load_and_prepare_data():
    """Load dataset and prepare features for ML"""
    print("\n📂 Loading dataset...")
    df = pd.read_csv(DATA_FILE)
    print(f"✅ Loaded {len(df)} records")
    
    # Filter only completed requests for training
    df_complete = df[df['is_completed'] == 1].copy()
    print(f"✅ Using {len(df_complete)} completed requests for training")
    
    return df_complete


def engineer_features(df):
    """Feature engineering and encoding"""
    print("\n🔧 Engineering features...")
    
    # Create feature DataFrame
    features = df.copy()
    
    # Encode categorical variables
    le_type = LabelEncoder()
    le_stage = LabelEncoder()
    
    features['request_type_encoded'] = le_type.fit_transform(features['request_type'])
    features['final_stage_encoded'] = le_stage.fit_transform(features['final_stage'])
    
    # Create derived features
    features['is_weekend'] = (features['created_day_of_week'] >= 5).astype(int)
    features['is_peak_hour'] = features['created_hour'].isin([10, 11, 14, 15, 16]).astype(int)
    features['is_business_hours'] = features['created_hour'].between(8, 17).astype(int)
    
    # Priority level features
    features['is_high_priority'] = (features['priority'] == 3).astype(int)
    features['is_low_priority'] = (features['priority'] == 1).astype(int)
    
    # Workload pressure
    features['high_workload'] = (features['handler_workload'] > 5).astype(int)
    
    # Total processing time per stage
    features['total_stage_time'] = (
        features['stage_created_duration'] +
        features['stage_assigned_duration'] +
        features['stage_verified_duration'] +
        features['stage_approved_duration'] +
        features['stage_processed_duration']
    )
    
    # SLA utilization ratio
    features['sla_utilization'] = features['total_duration_hours'] / features['sla_hours']
    
    # Save encoders
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(le_type, f"{MODEL_DIR}/label_encoder_type.pkl")
    joblib.dump(le_stage, f"{MODEL_DIR}/label_encoder_stage.pkl")
    
    print(f"✅ Engineered {features.shape[1]} total features")
    
    return features, le_type, le_stage


def select_features(df):
    """Select relevant features for training"""
    feature_columns = [
        'request_type_encoded',
        'priority',
        'created_hour',
        'created_day_of_week',
        'is_weekend',
        'is_peak_hour',
        'is_business_hours',
        'is_high_priority',
        'is_low_priority',
        'handler_workload',
        'high_workload',
        'sla_hours',
        'stage_created_duration',
        'stage_assigned_duration',
        'stage_verified_duration',
        'stage_approved_duration',
        'stage_processed_duration',
        'total_stage_time',
        'final_stage_encoded'
    ]
    
    X = df[feature_columns]
    y = df['is_delayed']
    
    print(f"\n📊 Feature selection:")
    print(f"   Features: {len(feature_columns)}")
    print(f"   Samples: {len(X)}")
    print(f"   Delayed: {y.sum()} ({y.sum()/len(y)*100:.1f}%)")
    print(f"   On-time: {len(y)-y.sum()} ({(len(y)-y.sum())/len(y)*100:.1f}%)")
    
    return X, y, feature_columns


def train_models(X_train, X_test, y_train, y_test):
    """Train multiple ML models"""
    print("\n🤖 Training models...")
    
    # StandardScaler for scale-sensitive models
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)
    # Save scaler early so scale-sensitive predict also works
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(scaler, f"{MODEL_DIR}/scaler.pkl")

    models = {
        'Logistic Regression': (LogisticRegression(random_state=RANDOM_STATE, max_iter=1000), False),
        'Random Forest':       (RandomForestClassifier(
                                    n_estimators=100, max_depth=10,
                                    random_state=RANDOM_STATE, n_jobs=-1), False),
        'Gradient Boosting':   (GradientBoostingClassifier(
                                    n_estimators=100, max_depth=5,
                                    random_state=RANDOM_STATE), False),
        'SVM':                 (SVC(kernel='rbf', probability=True,
                                    random_state=RANDOM_STATE), True),   # needs scaling
        'Neural Network':      (MLPClassifier(hidden_layer_sizes=(128, 64),
                                    max_iter=300, random_state=RANDOM_STATE), True),  # needs scaling
    }
    
    results = {}
    
    for name, (model, use_scaled) in models.items():
        print(f"\n   Training {name}...")
        Xtr = X_train_s if use_scaled else X_train
        Xte = X_test_s  if use_scaled else X_test
        
        # Train model
        model.fit(Xtr, y_train)
        
        # Predictions
        y_pred       = model.predict(Xte)
        y_pred_proba = model.predict_proba(Xte)[:, 1]
        
        # Metrics
        metrics = {
            'accuracy':              accuracy_score(y_test, y_pred),
            'precision':             precision_score(y_test, y_pred),
            'recall':                recall_score(y_test, y_pred),
            'f1':                    f1_score(y_test, y_pred),
            'roc_auc':               roc_auc_score(y_test, y_pred_proba),
            'confusion_matrix':      confusion_matrix(y_test, y_pred),
            'classification_report': classification_report(y_test, y_pred),
        }
        
        results[name] = {
            'model':         model,
            'metrics':       metrics,
            'predictions':   y_pred,
            'probabilities': y_pred_proba,
            'uses_scaling':  use_scaled,
        }
        
        print(f"   ✅ {name}: Accuracy={metrics['accuracy']:.3f}, F1={metrics['f1']:.3f}")
    
    return results


def select_best_model(results):
    """Select best model based on F1 score"""
    print("\n🏆 Selecting best model...")
    
    best_model_name = None
    best_f1 = 0
    
    for name, result in results.items():
        f1 = result['metrics']['f1']
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
    
    print(f"   ✅ Best model: {best_model_name} (F1={best_f1:.3f})")
    
    return best_model_name, results[best_model_name]


def save_models_and_report(results, best_model_name, feature_columns, X_test, y_test):
    """Save trained models and generate report"""
    print("\n💾 Saving models and report...")
    
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # Save best model
    best_model = results[best_model_name]['model']
    joblib.dump(best_model, f"{MODEL_DIR}/best_model.pkl")
    print(f"   ✅ Saved best model: {best_model_name}")
    
    # Save all models
    for name, result in results.items():
        safe_name = name.lower().replace(' ', '_')
        joblib.dump(result['model'], f"{MODEL_DIR}/{safe_name}.pkl")
    
    # Save feature columns
    joblib.dump(feature_columns, f"{MODEL_DIR}/feature_columns.pkl")
    
    # Save scaler (already saved in train_models, but ensure it exists)
    if not os.path.exists(f"{MODEL_DIR}/scaler.pkl"):
        scaler = StandardScaler()
        scaler.fit(X_test)
        joblib.dump(scaler, f"{MODEL_DIR}/scaler.pkl")
    
    # Generate report
    with open(REPORT_FILE, 'w') as f:
        f.write("="*70 + "\n")
        f.write("  ML MODEL TRAINING REPORT\n")
        f.write("  Intelligent Workflow Automation System\n")
        f.write("="*70 + "\n\n")
        f.write(f"Training Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Dataset: {DATA_FILE}\n")
        f.write(f"Test Size: {TEST_SIZE*100}%\n")
        f.write(f"Random State: {RANDOM_STATE}\n\n")
        
        f.write("="*70 + "\n")
        f.write("  MODEL PERFORMANCE COMPARISON\n")
        f.write("="*70 + "\n\n")
        
        for name, result in results.items():
            metrics = result['metrics']
            f.write(f"\n{name}:\n")
            f.write("-" * 70 + "\n")
            f.write(f"  Accuracy:  {metrics['accuracy']:.4f}\n")
            f.write(f"  Precision: {metrics['precision']:.4f}\n")
            f.write(f"  Recall:    {metrics['recall']:.4f}\n")
            f.write(f"  F1 Score:  {metrics['f1']:.4f}\n")
            f.write(f"  ROC-AUC:   {metrics['roc_auc']:.4f}\n\n")
            f.write(f"  Confusion Matrix:\n")
            cm = metrics['confusion_matrix']
            f.write(f"  [[{cm[0][0]:4d} {cm[0][1]:4d}]\n")
            f.write(f"   [{cm[1][0]:4d} {cm[1][1]:4d}]]\n\n")
            f.write(f"  Classification Report:\n")
            f.write(metrics['classification_report'])
            f.write("\n")
        
        f.write("="*70 + "\n")
        f.write(f"  BEST MODEL: {best_model_name}\n")
        f.write("="*70 + "\n\n")
        
        best_metrics = results[best_model_name]['metrics']
        f.write(f"Selected based on F1 Score: {best_metrics['f1']:.4f}\n\n")
        f.write(f"Performance Summary:\n")
        f.write(f"  - Accuracy:  {best_metrics['accuracy']*100:.2f}%\n")
        f.write(f"  - Precision: {best_metrics['precision']*100:.2f}%\n")
        f.write(f"  - Recall:    {best_metrics['recall']*100:.2f}%\n")
        f.write(f"  - F1 Score:  {best_metrics['f1']*100:.2f}%\n")
        f.write(f"  - ROC-AUC:   {best_metrics['roc_auc']*100:.2f}%\n\n")
        
        f.write("="*70 + "\n")
        f.write("  FEATURE IMPORTANCE\n")
        f.write("="*70 + "\n\n")
        
        # Feature importance for tree-based models
        if hasattr(best_model, 'feature_importances_'):
            importances = best_model.feature_importances_
            indices = np.argsort(importances)[::-1][:10]  # Top 10
            
            f.write("Top 10 Most Important Features:\n\n")
            for i, idx in enumerate(indices, 1):
                f.write(f"  {i}. {feature_columns[idx]}: {importances[idx]:.4f}\n")
        else:
            f.write("Feature importance not available for this model type.\n")
        
        f.write("\n" + "="*70 + "\n")
        f.write("  DEPLOYMENT READY\n")
        f.write("="*70 + "\n\n")
        f.write(f"Model files saved to: {MODEL_DIR}/\n")
        f.write(f"  - best_model.pkl\n")
        f.write(f"  - label_encoder_type.pkl\n")
        f.write(f"  - label_encoder_stage.pkl\n")
        f.write(f"  - feature_columns.pkl\n")
        f.write(f"  - scaler.pkl\n\n")
    
    print(f"   ✅ Report saved: {REPORT_FILE}")


def print_summary(results, best_model_name):
    """Print training summary to console"""
    print("\n" + "="*70)
    print("  TRAINING COMPLETE")
    print("="*70)
    
    print("\n📊 Model Comparison:\n")
    print(f"{'Model':<25} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1':>10}")
    print("-" * 70)
    
    for name, result in results.items():
        metrics = result['metrics']
        marker = "⭐" if name == best_model_name else "  "
        print(f"{marker} {name:<23} {metrics['accuracy']:>10.3f} {metrics['precision']:>10.3f} "
              f"{metrics['recall']:>10.3f} {metrics['f1']:>10.3f}")
    
    print("\n🏆 Best Model: " + best_model_name)
    best_metrics = results[best_model_name]['metrics']
    print(f"   Accuracy: {best_metrics['accuracy']*100:.2f}%")
    print(f"   F1 Score: {best_metrics['f1']*100:.2f}%")
    
    print("\n💾 Models saved to:", MODEL_DIR)
    print("📄 Report saved to:", REPORT_FILE)
    print("\n✅ Ready for prediction API integration!")


def main():
    """Main training pipeline"""
    print("\n🤖 Week 5: ML Model Training")
    print("Training delay prediction models on synthetic data\n")
    
    try:
        # Load data
        df = load_and_prepare_data()
        
        # Feature engineering
        df_features, le_type, le_stage = engineer_features(df)
        
        # Select features and target
        X, y, feature_columns = select_features(df_features)
        
        # Train-test split
        print(f"\n✂️  Splitting data ({TEST_SIZE*100}% test)...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
        )
        print(f"   Train: {len(X_train)} samples")
        print(f"   Test:  {len(X_test)} samples")
        
        # Train models
        results = train_models(X_train, X_test, y_train, y_test)
        
        # Select best model
        best_model_name, best_result = select_best_model(results)
        
        # Save models and generate report
        save_models_and_report(results, best_model_name, feature_columns, X_test, y_test)
        
        # Print summary
        print_summary(results, best_model_name)
        
        print("\n" + "="*70)
        print("  SUCCESS - Models ready for deployment!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
