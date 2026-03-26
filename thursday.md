# 🎯 ML-FOCUSED DEMO SCRIPT (FOR GUIDE)

**Target Audience:** Your Guide (Machine Learning Teacher)
**Focus:** Data pipeline, feature engineering, model architecture, and Explainable AI (XAI).

---

## ⏰ BEFORE THE PRESENTATION (Setup)

### Step 1: Open Terminal Windows
- **Terminal 1 (Backend + DB):**
  ```powershell
  # Ensure Docker Desktop is running!
  docker-compose up -d postgres
  
  cd backend
  ..\.venv\Scripts\activate
  python -m uvicorn main:app --reload --port 8000
  ```
- **Terminal 2 (Frontend):**
  ```powershell
  cd frontend
  npm run dev
  ```

### Step 2: Open Tools in Background
- **Browser:** Open `http://localhost:5173` and log in (Admin: `admin@university.edu`, Pass: `Admin@123`)
- **VS Code:** Have `backend/api/predictions.py` (scroll to `engineer_prediction_features`) and `scripts/train_models.py` open in separate tabs.

---

## 🎤 PRESENTATION SCRIPT (When Your Guide Arrives)

### Step 1: The Problem Statement (The "Why")
**ACTION:** Show the React Dashboard.
**SAY:** 
> "Good morning ma'am. University admin offices process hundreds of requests, and often breach SLAs (Service Level Agreements) because they cannot foresee bottlenecks. My project digitizes workflows and uses Machine Learning to predict precisely which requests are at risk of missing their SLA, *before* it happens."

### Step 2: The Data & Feature Engineering (The "Brain")
**ACTION:** Switch to VS Code and show `backend/api/predictions.py`.
**SAY:** 
> "Raw timestamps aren't enough for ML. I built a comprehensive feature engineering pipeline right into the API block via the `engineer_prediction_features` function. We dynamically extract 19 features including:
> - **Temporal constraints** (is it a weekend? is it peak hour?).
> - **System state** (what is the current workload of the handler?).
> - **Stage-duration deltas** and SLA Utilization ratios."

### Step 3: Model Selection & Training
**ACTION:** Switch to `scripts/train_models.py` in VS Code.
**SAY:** 
> "I built an automated script to train 5 different algorithms: Logistic Regression, Random Forest, Gradient Boosting, SVM, and an MLP Neural Network. 
> For our tabular workflow data, **Logistic Regression** performed exceptionally well (98.68% accuracy) while remaining highly interpretable and lightning-fast for real-time API inference."

### Step 4: Live Inference (The Core Demo)
**ACTION:** Go to the browser -> click **ML Predictions** tab.
**SAY:** 
> "Let's do a live inference. The FastAPI backend instantly engineers features from this JSON payload and runs it through the loaded `.pkl` model."

#### Demo A: Low Risk (Green)
**SAY:** "First, a best-case scenario."
**ACTION:** Enter these exact values:
| Field | Value | Stage Durations | Value |
|---|---|---|---|
| Request Type | `certificate` | Created | `1` |
| Priority Level | `3` (max) | Assigned | `2` |
| Submission | `10`, `Monday` | Verified/App/Proc | `3`, `4`, `5` |
| Workload | `2` |

**CLICK:** "Predict"
**SAY:** "The delay probability is very low. It's high-priority, early in the week, with low workload."

#### Demo B: High Risk (Red) & Explainable AI
**SAY:** "Now, a worst-case scenario."
**ACTION:** Enter these exact values:
| Field | Value | Stage Durations | Value |
|---|---|---|---|
| Request Type | `hostel` | Created | `8` |
| Priority Level | `1` (min) | Assigned | `16` |
| Submission | `17`, `Friday` | Verified/App/Proc | `20`, `18`, `25` |
| Workload | `10` (max) | 

**CLICK:** "Predict"
**POINT:** Point to the red 100% percentage circle.
**SAY:** 
> "The model correctly predicts a near 100% delay probability. But a probability score isn't enough for end-users; they need actionable insights."

**ACTION:** Point to the generated AI Explanation text box below the prediction.
**SAY:** 
> "So I implemented an Explainable AI (XAI) layer. The backend analyzes the contributing heuristic features and feeds the context into the **Google Gemini LLM API**. Gemini then generates this human-readable explanation telling the admin exactly *why* this specific request is delayed and what to do about it."

---

## 🧠 CHEAT SHEET FOR ML EXAMINER QUESTIONS

**Q: How do you handle categorical variables?**
> "I use a `LabelEncoder` for Request Types and Final Stages. These encoders are pickled alongside the model so the API applies the exact same transformation at inference time."

**Q: Why didn't you use Deep Learning / LSTMs?**
> "Deep Learning is overkill for structured, tabular data with only 19 features. Tree-based models or Logistic Regression are industry standards here because they are less prone to overfitting on tabular data and are much cheaper/faster to run in production."

**Q: How does the trained model connect to the React frontend?**
> "The model is decoupled. It's served via a REST API endpoint in FastAPI. The React frontend sends a JSON payload, the backend engineers and scales the features using the saved scaler, runs `model.predict_proba()`, and returns the class probability."

**Q: What is the accuracy?**
> "98.68% accuracy with a 97.56% F1-score. I optimized for F1 because in SLA breaches, False Negatives (missing a delay) are more costly than False Positives."
