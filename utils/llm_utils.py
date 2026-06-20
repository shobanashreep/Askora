import os
import google.generativeai as genai
from PIL import Image

<<<<<<< HEAD
# --------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------



GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found. Please add it to your .env file."
    )

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
=======
# Configure Gemini
genai.configure(
    api_key=os.environ["GEMINI_API_KEY"]
)

>>>>>>> fd9f27e (Fix Streamlit deployment)
model = genai.GenerativeModel("gemini-2.5-flash")


def get_llm_response(prompt_text, task_type, image_path=None, chat_history=None):

    try:

        # OCR + Question Extraction
        if task_type == "extract_question":

            image = Image.open(image_path)

            response = model.generate_content([
                """
                Read this academic question and:

                1. Extract the question exactly.
                2. If a diagram exists, describe it briefly.
                """,
                image
            ])

            return response.text

        # Subject Detection
        elif task_type == "detect_subject":

            response = model.generate_content(
                f"""
                Identify the academic subject.

                Return ONLY the subject name.

                Question:
                {prompt_text}
                """
            )

            return response.text.strip()

        # Explanation
        elif task_type == "explain_doubt":

            response = model.generate_content(
                f"""
                You are an expert tutor.

                Explain the following question step-by-step.

                Rules:
                - Use simple language.
                - Show calculations clearly.
                - Teach the concept.
                - Give the final answer.

                Question:
                {prompt_text}
                """
            )

            return response.text

        # Practice Problem
        elif task_type == "generate_practice_problem":

            response = model.generate_content(
                f"""
                Create ONE similar practice problem.

                Rules:
                - Similar difficulty.
                - Do NOT provide answer.
                - Only provide the problem.

                Topic:
                {prompt_text}
                """
            )

            return response.text

        # Quiz Generation
        elif task_type == "generate_quiz":

            response = model.generate_content(
                f"""
                Create 5 multiple-choice questions.

                Format:

                Q1. Question

                A)
                B)
                C)
                D)

                Repeat for 5 questions.

                Do NOT provide answers.

                Topic:
                {prompt_text}
                """
            )

            return response.text

        # Follow-up Chat
        elif task_type == "follow_up":

            response = model.generate_content(
                f"""
                You are a helpful tutor.

                Student Question:
                {prompt_text}

                Answer clearly and simply.
                """
            )

            return response.text

        return "Unsupported task"

    except Exception as e:

        error_msg = str(e)

        if "429" in error_msg:
            return """
⚠️ Gemini free quota reached.

Please wait a minute and try again.

Your uploaded question and previous explanation remain available.

Tip:
For hackathon demos, avoid repeatedly generating quizzes because each quiz uses an additional Gemini request.
"""

        return f"⚠️ Error: {error_msg}"


def detect_subject(question_text):
    return get_llm_response(
        question_text,
        "detect_subject"
    )


def generate_practice_problem(explanation_text):
    return get_llm_response(
        explanation_text,
        "generate_practice_problem"
    )


def generate_quiz(topic_text):
    return get_llm_response(
        topic_text,
        "generate_quiz"
    )
