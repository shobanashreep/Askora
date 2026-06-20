import os
import google.generativeai as genai
from PIL import Image

# Gemini API Key from Streamlit Secrets / Environment
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-2.5-flash")


def get_llm_response(prompt_text, task_type, image_path=None, chat_history=None):

    try:

        # ---------------- OCR ----------------
        if task_type == "extract_question":
            image = Image.open(image_path)

            response = model.generate_content([
                "Extract the question exactly and describe diagram if present.",
                image
            ])

            return response.text

        # ---------------- SUBJECT DETECTION ----------------
        elif task_type == "detect_subject":
            response = model.generate_content(
                f"Identify subject. Return only one word.\n\nQuestion:\n{prompt_text}"
            )
            return response.text.strip()

        # ---------------- EXPLANATION ----------------
        elif task_type == "explain_doubt":
            response = model.generate_content(
                f"""
                Explain step by step in simple language:

                {prompt_text}
                """
            )
            return response.text

        # ---------------- PRACTICE PROBLEM ----------------
        elif task_type == "generate_practice_problem":
            response = model.generate_content(
                f"""
                Create ONE similar practice problem.
                Do NOT give answer.

                Topic:
                {prompt_text}
                """
            )
            return response.text

        # ---------------- QUIZ ----------------
        elif task_type == "generate_quiz":
            response = model.generate_content(
                f"""
                Create 5 MCQs with options A/B/C/D.
                Do NOT provide answers.

                Topic:
                {prompt_text}
                """
            )
            return response.text

        # ---------------- FOLLOW UP ----------------
        elif task_type == "follow_up":
            response = model.generate_content(prompt_text)
            return response.text

        return "Unsupported task"

    except Exception as e:
        if "429" in str(e):
            return "⚠️ Quota exceeded. Please wait and retry."
        return f"⚠️ Error: {str(e)}"


def detect_subject(question_text):
    return get_llm_response(question_text, "detect_subject")


def generate_practice_problem(explanation_text):
    return get_llm_response(explanation_text, "generate_practice_problem")


def generate_quiz(topic_text):
    return get_llm_response(topic_text, "generate_quiz")