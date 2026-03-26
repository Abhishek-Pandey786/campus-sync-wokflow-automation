# User Guide
## CampusSync — Smart Campus Workflow Management

**Version:** 1.0  
**Institution:** Christ University  
**Program:** MCA 6th Trimester

---

## Introduction

CampusSync is an intelligent university service request management portal. It digitizes the process of submitting, tracking, and fulfilling campus service requests (certificates, transcripts, IT support, hostel, library, and exam queries) and uses real-time Machine Learning to predict delays before they happen.

There are two types of users in the system:
- 🎓 **Students** — Submit and track their service requests
- 🛡️ **Admins** — Process requests through a 6-stage pipeline

---

## Getting Started

### Accessing the Application

Open your web browser and navigate to:
- **Development:** `http://localhost:5173`
- **Production:** As provided by your university IT department

---

## 🎓 Student Guide

### 1. Creating Your Account

1. On the login page, click **"Student Portal"** in the role selector at the top.
2. Click the **"Sign Up"** tab within the student card.
3. Fill in:
   - **Full Name** — Your complete name as on university records
   - **Email Address** — Your university email (`@christuniversity.in`)
   - **Password** — Minimum 8 characters, must include uppercase, lowercase, and a digit
   - **Confirm Password** — Repeat the same password
4. Click **"Create Student Account"**.
5. You will be automatically logged in and redirected to your dashboard.

---

### 2. Signing In

1. Click **"Student Portal"** on the login page.
2. The **"Sign In"** tab is selected by default.
3. Enter your email and password and click **"Sign In as Student"**.

---

### 3. Submitting a Service Request

Once logged in, you will be on the **"My Requests"** page.

1. Click the **"New Request"** button (top right of the page).
2. A form modal will appear. Fill in:
   - **Request Type** — Select the type of service you need:
     - `Certificate` — Bonafide, completion, or other certificates (SLA: 3 days)
     - `Hostel` — Accommodation-related requests (SLA: 2 days)
     - `IT Support` — Technical issues, account problems (SLA: 1 day)
     - `Library` — Book reservations, access issues (SLA: 2 days)
     - `Exam` — Exam hall tickets, re-evaluation queries (SLA: 4 days)
     - `Transcript` — Official academic transcripts (SLA: 5 days)
   - **Title** — A short, clear summary of your request
   - **Description** — Detailed description of what you need
   - **Priority** — `Low`, `Medium`, or `High`
3. Click **"Submit Request"**.
4. Your request will appear in the table with the status **"Pending"** and a unique request number (e.g., `REQ-2024-042`).

---

### 4. Tracking Your Request

The **My Requests** page shows all your submitted requests with:

| Column | Description |
|--------|-------------|
| Request # | Unique identifier (e.g., REQ-2024-042) |
| Type | The service category |
| Title | Your request title |
| Status | Current status (Pending / In Progress / Completed / Rejected) |
| Priority | Low / Medium / High |
| Stage | Current pipeline stage (Created → Assigned → Verified → ...) |
| Submitted | Date and time of submission |

Click any row to see the **full details**, including the current workflow stage and any admin notes.

---

### 5. Understanding Request Status

| Status | Meaning |
|--------|---------|
| 🟡 Pending | Submitted, waiting for an admin to pick it up |
| 🔵 In Progress | An admin is actively processing it |
| ✅ Completed | Your request has been fulfilled |
| ❌ Rejected | Your request was declined (a reason will be provided) |

---

### 6. Using the ML Delay Predictor

Navigate to **"Predictions"** in the navigation bar to access the AI prediction tool.

This tool lets you estimate whether your request is likely to face a delay before you even submit it.

1. Select a **Request Type** from the dropdown.
2. Set the **Priority Level** using the slider.
3. Set the **Submission Hour** (the time you plan to submit).
4. Select the **Day of Week**.
5. Use the **Stage Duration** inputs to estimate how long each processing step might take.
6. Click **"Predict Delay Risk"**.

The AI will show you:
- A **Delay Probability %** on a circular gauge
- A **Risk Level** (Low / Medium / High) color indicator
- A **Gemini AI Explanation** explaining the key risk factors
- A **Recommendation** on what action to take

**Quick Presets:** Use the `Low Risk`, `Medium Risk`, and `High Risk` buttons to auto-fill example scenarios.

---

## 🛡️ Admin Guide

### 1. Signing In

1. On the login page, **"Admin Portal"** is selected by default.
2. Your credentials are prefilled for demo purposes.
3. Click **"Sign In as Admin"** to access the full administrative dashboard.

---

### 2. Admin Dashboard

The **Dashboard** (home page for admins) shows:
- **Total Requests** — All requests in the system
- **Pending Requests** — Waiting for action
- **Completed Requests** — Successfully processed
- **SLA Breaches** — Requests that exceeded their deadline
- Recent activity feed

---

### 3. Managing Requests

Navigate to **"Requests"** in the navbar to see all student submissions.

**Filtering:** Use the dropdowns to filter by Status, Type, or Priority.

**Viewing Details:** Click any request row to open the **Detail Drawer** on the right side, which shows:
- Full request information
- Student details
- Current pipeline stage visualization
- Workflow action panel

---

### 4. Processing a Request (Workflow Actions)

In the request detail drawer, the **Action Panel** contains three actions:

#### ✅ Assign to Me
- Available when a request is in the `Created` stage.
- Click **"Assign to Me"** to take ownership of the request.
- The stage advances to `Assigned` and you are recorded as the handler.

#### ▶️ Advance Stage
- Available once you are assigned and the request is in progress.
- Click to move to the next stage in the pipeline:
  ```
  Assigned → Verified → Approved → Processed → Completed
  ```
- Optionally add a note before advancing.
- The system automatically records how many hours were spent in the previous stage.

#### ❌ Reject
- Available at any stage while the request is active.
- Enter a mandatory **rejection reason** in the text area.
- Click **"Reject Request"** to decline the submission.
- The student will see the rejection reason in their request details.

---

### 5. AI-Powered Alerts

Navigate to **"Alerts"** in the navbar.

The alerts page automatically surfaces requests that the ML model has flagged as **High Risk** (>70% probability of missing their SLA deadline). Use this page for daily triage — prioritise these requests first.

---

### 6. Analytics Dashboard

Navigate to **"Analytics"** in the navbar.

The analytics page provides visual insights into system performance:
- Request volume over time
- Completion rates by request type
- Average processing time per stage
- SLA compliance rates

---

### 7. Running the ML Delay Predictor

Admins also have full access to the **Predictions** page.

This is particularly useful before assigning yourself to a complex request — you can simulate the expected durations and check if the request is at risk of exceeding its SLA before you begin processing.

---

## Frequently Asked Questions

**Q: Can I edit a request after submitting it?**  
A: Yes, but only while the request is still in "Pending" status. Once an admin has assigned themselves, the request is locked.

**Q: What happens if my request is rejected?**  
A: You will see the rejection reason on your request detail page. You may submit a new request with the corrected information.

**Q: How long will my request take?**  
A: Each request type has an SLA deadline. Refer to the SLA table in the Request Type descriptions. You can also use the Predictions tool to estimate risk.

**Q: I forgot my password. Can I reset it?**  
A: Contact your university system administrator to reset your account credentials.

**Q: As an admin, can I see which requests I previously handled?**  
A: Yes — use the filter on the Requests page to filter by your email as the handler.
