import time
import json
import re
from io import BytesIO

from PIL import Image
from google import genai
from google.genai import types


# ==========================================================
# Allowed Subjects
# ==========================================================

ALLOWED_SUBJECTS = {
    "Mathematics",
    "Aptitude",
    "Physics",
    "Chemistry",
    "Biology",
    "Computer Science",
    "English",
    "General Knowledge"
}


# ==========================================================
# Gemini Client
# ==========================================================

def get_gemini_client(api_key: str):
    """
    Initialize Gemini client.
    """
    if not api_key:
        raise ValueError("Gemini API Key not found.")

    return genai.Client(api_key=api_key)


# ==========================================================
# Production OCR + Explanation Prompt
# ==========================================================

SYSTEM_PROMPT = """
You are Askora, an expert AI tutor for students.

Your task:

1. Read the uploaded image carefully.
2. Extract handwritten or printed academic questions.
3. Correct OCR mistakes if obvious.
4. Preserve:
   - numbers
   - formulas
   - equations
   - symbols
   - question structure

5. Classify subject STRICTLY as one of:

- Mathematics
- Aptitude
- Physics
- Chemistry
- Biology
- Computer Science
- English
- General Knowledge

Never create any other subject.

6. Determine difficulty:

- Easy
- Medium
- Hard

7. Generate:

- Detailed explanation
- Key concepts
- One practice problem
- Five MCQ quiz questions

IMPORTANT:

Return ONLY VALID JSON.

No markdown.
No code block.
No extra text.

JSON FORMAT:

{
  "subject": "",
  "difficulty": "",
  "question": "",
  "explanation": "",
  "key_concepts": [
    ""
  ],
  "practice_problem": "",
  "quiz": [
    {
      "question": "",
      "options": {
        "A": "",
        "B": "",
        "C": "",
        "D": ""
      },
      "answer": "A"
    }
  ]
}
"""


# ==========================================================
# JSON Cleanup
# ==========================================================

def clean_json_response(text: str) -> str:
    """
    Removes markdown wrappers if Gemini returns them.
    """

    text = text.strip()

    text = re.sub(r"^```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)

    return text.strip()


# ==========================================================
# Subject Validation
# ==========================================================

def validate_subject(subject: str) -> str:
    """
    Prevent weird subjects like Salary/Finance.
    """

    if subject in ALLOWED_SUBJECTS:
        return subject

    subject_lower = subject.lower()

    if any(
        word in subject_lower
        for word in [
            "percentage",
            "profit",
            "loss",
            "salary",
            "aptitude",
            "reasoning",
            "money",
            "finance"
        ]
    ):
        return "Aptitude"

    return "General Knowledge"


# ==========================================================
# Default Empty Response
# ==========================================================

def default_response():
    return {
        "subject": "General Knowledge",
        "difficulty": "Medium",
        "question": "Unable to extract question.",
        "explanation": "OCR could not confidently read the image.",
        "key_concepts": [],
        "practice_problem": "",
        "quiz": []
    }


# ==========================================================
# Parse Gemini JSON
# ==========================================================

def parse_gemini_json(raw_text: str):
    """
    Safely parse Gemini JSON response.
    """

    try:
        cleaned = clean_json_response(raw_text)

        data = json.loads(cleaned)

        data["subject"] = validate_subject(
            data.get("subject", "")
        )

        if data.get("difficulty") not in [
            "Easy",
            "Medium",
            "Hard"
        ]:
            data["difficulty"] = "Medium"

        return data

    except Exception:
        return default_response()


# ==========================================================
# Main Single Gemini Call
# ==========================================================

def analyze_question_image(
    image_file,
    api_key: str
):
    try:

        if image_file is None:
            raise ValueError("No image uploaded.")

        client = get_gemini_client(api_key)

        image = Image.open(image_file)

        buffer = BytesIO()
        image.save(buffer, format="PNG")

        image_bytes = buffer.getvalue()

        contents = [
            SYSTEM_PROMPT,
            types.Part.from_bytes(
                data=image_bytes,
                mime_type="image/png"
            )
        ]

        response = None

        MODELS = [
            "gemini-2.5-flash",
            "gemini-2.0-flash"
        ]

        last_error = None

        for model_name in MODELS:

            for attempt in range(3):

                try:

                    response = client.models.generate_content(
                        model=model_name,
                        contents=contents
                    )

                    if response and response.text:
                        return parse_gemini_json(
                            response.text
                        )

                except Exception as e:

                    last_error = e

                    error_text = str(e).lower()

                    if (
                        "503" in error_text
                        or "unavailable" in error_text
                    ):
                        time.sleep(
                            2 * (attempt + 1)
                        )
                        continue

                    if (
                        "429" in error_text
                        or "quota" in error_text
                    ):
                        raise RuntimeError(
                            "Gemini quota exceeded. Please try later."
                        )

                    break

        raise RuntimeError(
            f"Gemini unavailable. {last_error}"
        )

    except Exception as e:

        raise RuntimeError(
            f"Image analysis failed: {str(e)}"
        )
# ==========================================================
# Follow-Up Chat
# ==========================================================

def ask_followup_question(
    api_key: str,
    original_question: str,
    explanation: str,
    user_question: str
):
    """
    Context-aware follow-up chat.
    """

    try:

        client = get_gemini_client(api_key)

        prompt = f"""
You are Askora AI Tutor.

Original Question:
{original_question}

Explanation:
{explanation}

Student Follow-Up:
{user_question}

Answer clearly and simply.
Keep the answer focused on the original doubt.
"""

        response = client.models.generate_content(
          model="gemini-2.0-flash",
          contents=prompt
        )

        return response.text

    except Exception as e:

        error_text = str(e).lower()

        if "429" in error_text:
            return (
                "⚠️ Gemini quota limit reached.\n\n"
                "Please wait a few minutes and try again."
            )

        if "503" in error_text:
            return (
                "🚦 Gemini servers are currently busy.\n\n"
                "Please try again shortly."
            )

        return (
            "❌ Unable to answer follow-up question right now."
        )
# ==========================================================
# Notebook Entry Helper
# ==========================================================

def create_notebook_entry(
    result: dict,
    quiz_score: str
):
    """
    Standard notebook object.
    """

    return {
        "subject": result.get("subject", ""),
        "difficulty": result.get("difficulty", ""),
        "question": result.get("question", ""),
        "explanation": result.get("explanation", ""),
        "practice_problem": result.get(
            "practice_problem",
            ""
        ),
        "quiz_score": quiz_score
    }