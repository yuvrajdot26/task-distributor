from groq import Groq
from django.conf import settings
import json

client = Groq(api_key=settings.GROQ_API_KEY)

ALLOWED_SKILLS ={
    "BACKEND",
    "FRONTEND",
    "DEVOPS",
    "TESTING"
}

ALLOWED_PRIORITIES={
    "HIGH",
    "MEDIUM",
    "LOW"
}

def  analyze_task(title,description):
    prompt = f"""
You are a task analyzer for a software development company.

Analyze this task:

Title: {title}

Description: {description}

Choose exactly ONE required skill from:
BACKEND
FRONTEND
TESTING
DEVOPS

Choose exactly ONE priority from:
LOW
MEDIUM
HIGH

Estimate the task duration in hours.

Return ONLY JSON in this exact format:

    {{
    "required_skills": "BACKEND",
    "priority": "HIGH",
    "estimate_hours": 4
    }}
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

    except Exception as e :
        raise RuntimeError(f"Ai request failed: {str(e)}")

    content = response.choices[0].message.content
    
    content = content.strip()

    if content.startswith("```json"):
        content = content[7:]

    if content.endswith("```"):
        content = content[:-3]

    content = content.strip()

    try:
        result = json.loads(content)
    
    except json.JSONDecodeError:
            raise ValueError("AI returned invalid json")
    
    required_fields= { 
        "required_skills",
        "priority",
        "estimate_hours"
    }

    if set(result.keys()) != required_fields:
        raise ValueError(
            "Ai response is missing or extra fields"
        )

    if result["required_skills"] not in ALLOWED_SKILLS:
        raise ValueError("AI returned invalid skills")

    if result["priority"] not in ALLOWED_PRIORITIES:
        raise ValueError("AI returned invalid priorities")

    if (type(result["estimate_hours"]) is not int or result["estimate_hours"] <=0 ):
        raise ValueError("AI returned Invalid estimate hours")

    return result