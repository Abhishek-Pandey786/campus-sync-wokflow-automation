"""
LLM Service using Google Gemini 2.0 Flash
Provides intelligent explanations and text generation for ML predictions
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if Gemini is available
GEMINI_AVAILABLE = False
client = None
try:
    from google import genai
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)
        GEMINI_AVAILABLE = True
        print("✅ Gemini API initialized successfully")
except ImportError:
    print("⚠️  Warning: google-genai not installed. LLM features will use fallback mode.")
except Exception as e:
    print(f"⚠️  Warning: Could not initialize Gemini: {e}. Using fallback mode.")


def explain_delay_prediction(
    request_type: str,
    priority: int,
    prediction_score: float,
    features: Dict
) -> str:
    """
    Generate human-readable explanation for delay prediction
    
    Args:
        request_type: Type of service request
        priority: Priority level (1=low, 2=medium, 3=high)
        prediction_score: Probability of delay (0-1)
        features: Dictionary of request features
        
    Returns:
        Human-readable explanation string
    """
    
    if not GEMINI_AVAILABLE:
        return generate_fallback_explanation(request_type, prediction_score, features)
    
    priority_name = {1: "Low", 2: "Medium", 3: "High"}.get(priority, "Medium")
    delay_probability = prediction_score * 100
    
    # Day of week names
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_name = days[features.get('created_day_of_week', 0)]
    
    prompt = f"""You are an AI assistant for a university workflow automation system.

A student has submitted a {request_type} request with {priority_name} priority.
Our ML model predicts a {delay_probability:.1f}% probability of delay beyond SLA.

Request Details:
- Request Type: {request_type}
- Priority: {priority_name} (P{priority})
- Created Time: {features.get('created_hour', 'N/A')}:00 on {day_name}
- Handler Workload: {features.get('handler_workload', 'N/A')} concurrent requests
- SLA Deadline: {features.get('sla_hours', 'N/A')} hours

Provide a concise 2-3 sentence explanation:
1. State the delay probability
2. Explain the main contributing factors
3. Provide one actionable suggestion to reduce delay risk

Keep it professional, student-friendly, and under 100 words."""

    try:
        response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
        return response.text.strip()
    except Exception as e:
        print(f"⚠️  LLM generation failed: {e}")
        return generate_fallback_explanation(request_type, prediction_score, features)


def generate_status_update(
    request_type: str,
    current_stage: str,
    new_stage: str,
    student_name: str = "Student"
) -> str:
    """
    Generate personalized status update message
    
    Args:
        request_type: Type of service request
        current_stage: Current workflow stage
        new_stage: New workflow stage
        student_name: Name of the student
        
    Returns:
        Personalized status update message
    """
    
    if not GEMINI_AVAILABLE:
        return f"Your {request_type} request has been moved to {new_stage} stage. We'll update you once processing is complete."
    
    prompt = f"""Generate a friendly, professional email notification for a university student.

Context:
- Request Type: {request_type}
- Status Change: {current_stage} → {new_stage}
- Recipient: {student_name}

Requirements:
- Professional but warm tone
- 3-4 sentences maximum
- Include what happens next
- No subject line needed

Write the email body:"""

    try:
        response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
        return response.text.strip()
    except Exception as e:
        return f"Your {request_type} request has been moved to {new_stage} stage. We'll update you once processing is complete."


def classify_request_from_description(description: str) -> Dict[str, any]:
    """
    Auto-classify request type and priority from free-text description
    
    Args:
        description: Free-text request description
        
    Returns:
        Dictionary with classification results
    """
    
    if not GEMINI_AVAILABLE:
        return {
            "request_type": "certificate",
            "priority": 2,
            "confidence": "low",
            "reasoning": "LLM not available - using default"
        }
    
    prompt = f"""Analyze this university service request description and classify it.

Description: "{description}"

Extract:
1. Request Type: certificate/hostel/it_support/library/exam/transcript
2. Priority: 1 (low), 2 (medium), or 3 (high) - based on urgency indicators
3. Confidence: low/medium/high

Output ONLY valid JSON:
{{"request_type": "...", "priority": ..., "confidence": "...", "reasoning": "brief reason"}}"""

    try:
        response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
        import json
        
        # Extract JSON from response
        text = response.text.strip()
        
        # Remove markdown code blocks if present
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0].strip()
        elif '```' in text:
            text = text.split('```')[1].split('```')[0].strip()
        
        return json.loads(text)
    except Exception as e:
        return {
            "request_type": "certificate",
            "priority": 2,
            "confidence": "low",
            "reasoning": f"Classification failed: {str(e)}"
        }


def generate_rejection_reason(
    request_type: str,
    stage: str,
    admin_notes: Optional[str] = None
) -> str:
    """
    Generate professional rejection explanation
    
    Args:
        request_type: Type of service request
        stage: Stage where rejection occurred
        admin_notes: Optional admin notes
        
    Returns:
        Professional rejection message
    """
    
    if not GEMINI_AVAILABLE:
        return f"Your {request_type} request has been rejected at {stage} stage. Please review the requirements and resubmit with necessary corrections."
    
    prompt = f"""Generate a brief, professional rejection message for a {request_type} request that was rejected at {stage} stage.

{"Admin notes: " + admin_notes if admin_notes else "No specific reason provided."}

Requirements:
- Empathetic but clear
- Explain next steps (resubmit with corrections)
- 2-3 sentences
- Professional tone

Write the message:"""

    try:
        response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
        return response.text.strip()
    except Exception as e:
        return f"Your {request_type} request has been rejected at {stage} stage. Please review the requirements and resubmit with necessary corrections."


def generate_fallback_explanation(request_type: str, probability: float, features: Dict) -> str:
    """
    Template-based fallback when LLM API fails or is unavailable
    
    Args:
        request_type: Type of service request
        probability: Delay probability (0-1)
        features: Dictionary of request features
        
    Returns:
        Template-based explanation string
    """
    
    prob_percent = probability * 100
    factors = []
    
    # For LOW delay probability - explain why it's on-time (positive factors)
    if prob_percent < 30:
        if features.get('priority', 2) == 3:
            factors.append("high priority level")
        
        if features.get('handler_workload', 5) <= 3:
            factors.append(f"low handler workload ({features.get('handler_workload', 2)} concurrent requests)")
        
        created_hour = features.get('created_hour', 12)
        if 9 <= created_hour <= 16:
            factors.append("submission during optimal business hours")
        
        created_day = features.get('created_day_of_week', 0)
        if created_day < 5:  # Weekday
            factors.append("early week submission")
        
        # Check if duration is well under SLA
        total_duration = features.get('total_duration_hours', 0)
        sla_hours = features.get('sla_hours', 72)
        if total_duration > 0 and total_duration < sla_hours * 0.7:
            factors.append(f"expected duration well below SLA limit ({total_duration:.0f}/{sla_hours} hours)")
    
    # For HIGH delay probability - explain why it's delayed (negative factors)
    else:
        if features.get('handler_workload', 0) > 5:
            factors.append(f"high handler workload ({features.get('handler_workload', 10)} concurrent requests)")
        
        if features.get('priority', 2) == 1:
            factors.append("low priority level")
        
        created_hour = features.get('created_hour', 12)
        if created_hour < 8 or created_hour > 17:
            factors.append("submission outside business hours")
        
        created_day = features.get('created_day_of_week', 0)
        if created_day >= 5:  # Weekend
            factors.append("weekend submission")
        elif created_day == 4:  # Friday
            factors.append("end-of-week submission")
        
        # Check if duration exceeds SLA
        total_duration = features.get('total_duration_hours', 0)
        sla_hours = features.get('sla_hours', 72)
        if total_duration > 0 and total_duration > sla_hours:
            factors.append(f"expected duration near SLA limit ({total_duration:.0f}/{sla_hours} hours)")
    
    # Build explanation
    if factors:
        factor_text = ", ".join(factors)
        if prob_percent < 30:
            explanation = f"This {request_type} request has a {prob_percent:.0f}% delay probability due to favorable conditions: {factor_text}."
        else:
            explanation = f"This {request_type} request has a {prob_percent:.0f}% delay probability due to {factor_text}."
    else:
        explanation = f"This {request_type} request has a {prob_percent:.0f}% delay probability based on current system load."
    
    # Add recommendation
    if prob_percent > 70:
        recommendation = " Consider escalating to high priority or contacting the admin office directly."
    elif prob_percent > 50:
        recommendation = " Consider following up with the admin office if urgent."
    else:
        recommendation = " The request should be processed within the expected timeframe. No action needed."
    
    return explanation + recommendation


def test_llm_service():
    """Test LLM service functionality"""
    print("\n" + "="*70)
    print("  Testing LLM Service")
    print("="*70 + "\n")
    
    if GEMINI_AVAILABLE:
        print("✅ Gemini API Available\n")
    else:
        print("⚠️  Gemini API Not Available - Using Fallback Mode\n")
    
    # Test delay explanation
    print("1. Testing Delay Explanation:")
    print("-" * 70)
    explanation = explain_delay_prediction(
        request_type="certificate",
        priority=2,
        prediction_score=0.75,
        features={
            'created_hour': 16,
            'created_day_of_week': 4,
            'handler_workload': 7,
            'sla_hours': 72
        }
    )
    print(explanation)
    
    # Test classification
    print("\n2. Testing Request Classification:")
    print("-" * 70)
    classification = classify_request_from_description(
        "I urgently need my degree certificate for job application by next week"
    )
    print(f"Type: {classification['request_type']}")
    print(f"Priority: {classification['priority']}")
    print(f"Confidence: {classification['confidence']}")
    print(f"Reasoning: {classification['reasoning']}")
    
    print("\n" + "="*70)
    print("  LLM Service Test Complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_llm_service()
