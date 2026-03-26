# ML Pipeline Documentation
## CampusSync — Intelligent Delay Prediction Engine

---

## Overview

CampusSync uses a **supervised binary classification** machine learning pipeline to predict whether a university service request will exceed its SLA (Service Level Agreement) deadline. The system was designed to move from reactive firefighting to **proactive intelligent triage**.

**Prediction Target:** `is_delayed` (1 = Will exceed SLA, 0 = Will finish on time)  
**Model Type:** Binary Classification  
**Best Model:** Logistic Regression  
**Training Dataset:** 1,201 synthetic university service request records  

---

## Pipeline Architecture

```
Raw CSV Data
    ↓
Feature Engineering (19 features)
    ↓
StandardScaler (fit on training set)
    ↓
Model Training (3 algorithms compared)
    ↓
Best Model Selection (by F1 Score)
    ↓
Serialization (.pkl files)
    ↓
FastAPI Inference Endpoint
    ↓
Prediction + Gemini LLM Explanation
```

---

## Step 1: Data Generation

**Script:** `scripts/generate_synthetic_data.py`  
**Output:** `data/raw/synthetic_requests.csv` (1,201 rows, 149 KB)

The synthetic dataset was programmatically generated to reflect real-world university request patterns:

- **Temporal Distribution:** Requests distributed across weekdays with realistic peak hours (10am, 11am, 2-4pm).
- **Priority Distribution:** Weighted to reflect real demand (Low 40%, Medium 40%, High 20%).
- **Delay Logic:** `is_delayed = 1` if the total stage duration sum exceeds the SLA limit for that request type.
- **SLA Utilization Engineering:** `sla_utilization = total_stage_time / sla_hours` is computed as a derived feature to capture the *ratio* of time used to time allowed.

---

## Step 2: Feature Engineering

**Script:** `scripts/train_models.py` → `engineer_prediction_features()` in `backend/api/predictions.py`

The model was trained on exactly **19 features**. The same 19 features must be computed identically at inference time.

| # | Feature Name | Type | Description |
|---|-------------|------|-------------|
| 1 | `request_type_encoded` | Integer | Label-encoded request type (0-5) |
| 2 | `priority` | Integer | Priority level: 1=Low, 2=Medium, 3=High |
| 3 | `created_hour` | Integer | Hour of day request was submitted (0–23) |
| 4 | `created_day_of_week` | Integer | Day: 0=Monday … 6=Sunday |
| 5 | `is_weekend` | Binary | 1 if submitted Sat/Sun |
| 6 | `is_peak_hour` | Binary | 1 if submitted at 10, 11, 14, 15, or 16 |
| 7 | `is_business_hours` | Binary | 1 if submitted between 8am–5pm |
| 8 | `is_high_priority` | Binary | 1 if priority == 3 |
| 9 | `is_low_priority` | Binary | 1 if priority == 1 |
| 10 | `handler_workload` | Integer | Number of concurrent requests the handler manages (1–10) |
| 11 | `high_workload` | Binary | 1 if handler_workload > 5 |
| 12 | `sla_hours` | Integer | SLA limit for the request type (24/48/72/96/120) |
| 13 | `stage_created_duration` | Float | Hours spent in "Created" stage |
| 14 | `stage_assigned_duration` | Float | Hours spent in "Assigned" stage |
| 15 | `stage_verified_duration` | Float | Hours spent in "Verified" stage |
| 16 | `stage_approved_duration` | Float | Hours spent in "Approved" stage |
| 17 | `stage_processed_duration` | Float | Hours spent in "Processed" stage |
| 18 | `total_stage_time` | Float | Sum of all 5 stage durations |
| 19 | `sla_utilization` | Float | `total_stage_time / sla_hours` (ratio of time used) |

> **Critical:** Features 13–19 are the strongest predictors. The model learned that when `sla_utilization` approaches or exceeds 1.0, a delay is near-certain.

---

## Step 3: Label Encoding

Two `sklearn.preprocessing.LabelEncoder` objects are used and saved:

- **`label_encoder_type.pkl`** — Encodes `request_type` strings to integers:
  ```
  certificate→0, exam→1, hostel→2, it_support→3, library→4, transcript→5
  ```
- **`label_encoder_stage.pkl`** — Encodes `final_stage` strings to integers.

These encoders are fitted during training and **must be reused** at inference to guarantee consistent integer mappings.

---

## Step 4: Scaling

A `sklearn.preprocessing.StandardScaler` is fitted on the training set and saved as `scaler.pkl`.

> **Important Design Note:** The StandardScaler is only applied at inference time for models that require feature scaling (SVM, Neural Networks). Logistic Regression and tree-based models (Random Forest, Gradient Boosting) in this project were trained on **raw, unscaled features** to maximize their predictive accuracy on the SLA-utilization signal.

The `load_models()` function auto-detects the model type and sets `needs_scaling = True` only for `SVC` and `MLPClassifier`.

---

## Step 5: Model Training & Comparison

**Script:** `scripts/train_models.py`

Three algorithms were trained and evaluated on an 80/20 train-test split (random state = 42):

| Model | Accuracy | Precision | Recall | F1 Score | ROC-AUC |
|-------|----------|-----------|--------|----------|---------|
| **Logistic Regression** ✅ | **98.68%** | 96.77% | **98.36%** | **97.56%** | **99.95%** |
| Random Forest | 98.68% | **98.33%** | 96.72% | 97.52% | 99.77% |
| Gradient Boosting | 98.25% | 98.31% | 95.08% | 96.67% | 95.73% |

**Winner Selection Criterion:** Highest **F1 Score** — which balances both precision (avoiding false alarms) and recall (not missing real delays).

**Why Logistic Regression Won:**
- Highest recall (98.36%) means it misses the fewest real delay cases — critical for a risk-management system.
- Extraordinary ROC-AUC of 99.95% means the model is almost perfectly separating "on-time" from "delayed" cases.
- Simpler model = faster inference, better explainability for the LLM layer.

**Confusion Matrix (Logistic Regression on test set):**
```
               Predicted: On-Time   Predicted: Delayed
Actual: On-Time       165                  2
Actual: Delayed         1                 60
```
Only 3 misclassifications out of 228 test samples.

---

## Step 6: Serialized Artifacts

All artifacts are saved to `backend/ml/models/`:

| File | Size | Contents |
|------|------|---------|
| `best_model.pkl` | 1.7 KB | Winning Logistic Regression model |
| `logistic_regression.pkl` | 1.7 KB | Logistic Regression (same as best) |
| `random_forest.pkl` | 851 KB | Random Forest model |
| `gradient_boosting.pkl` | 313 KB | Gradient Boosting model |
| `scaler.pkl` | ~1 KB | Fitted StandardScaler |
| `feature_columns.pkl` | ~1 KB | Ordered list of 19 feature column names |
| `label_encoder_type.pkl` | ~1 KB | LabelEncoder for request types |
| `label_encoder_stage.pkl` | ~1 KB | LabelEncoder for final stage |

---

## Step 7: Inference (FastAPI Endpoint)

**File:** `backend/api/predictions.py`

```
POST /predict/delay
    ↓
load_models()         # Load cached .pkl files from disk
    ↓
engineer_prediction_features()
    # 1. Encode request_type via label_encoder_type
    # 2. Encode final_stage via label_encoder_stage
    # 3. Map request_type → sla_hours
    # 4. Compute all 19 features (including sla_utilization)
    # 5. Build DataFrame with feature_columns.pkl ordering
    # 6. Apply scaler only if model needs_scaling
    ↓
model.predict_proba(features)
    ↓
Extract class index for label=1 (delayed) from model.classes_
    ↓
Generate LLM explanation via Gemini API
    ↓
Return PredictionResponse JSON
```

**Model caching:** Models are loaded into `_model_cache` in-memory on the first request and reused for all subsequent requests, avoiding repeated disk reads.

---

## Step 8: Explainable AI (LLM Integration)

**Service:** `backend/services/llm_service.py`  
**Model Used:** Google Gemini

After the ML model returns a probability score, the system passes key contextual information to Gemini with a structured prompt that includes:
- The request type and SLA limit
- The prediction score (e.g., 96.2%)
- Key risk factors (handler workload, submission day, duration vs SLA)

Gemini returns:
1. A human-readable **explanation** paragraph
2. An **actionable recommendation** for the admin

---

## Re-training

To retrain with new data:

```bash
# Step 1: Regenerate synthetic data (optional)
python scripts/generate_synthetic_data.py

# Step 2: Retrain all models
python scripts/train_models.py

# Step 3: Restart the backend server to clear the model cache
# The new .pkl files will be loaded on the next prediction request
```

Or use the admin API endpoint:
```
POST /predict/retrain
Authorization: Bearer <admin_token>
```
