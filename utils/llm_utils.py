import os
import google.generativeai as genai
from PIL import Image

# --------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------



GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found. Please add it to your .env file."
    )

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

# --------------------------------------------------
# MAIN LLM FUNCTION
# --------------------------------------------------

def get_llm_response(
    prompt_text,
    task_type,
    image_path=None,
    chat_history=None
):

    try:

        # ------------------------------------------
        # IMAGE → QUESTION EXTRACTION
        # ------------------------------------------

        if task_type == "extract_question":

            image = Image.open(image_path)

            response = model.generate_content([
                """
                Read the academic question from this image.

                Instructions:
                - Extract the question exactly.
                - Preserve equations and symbols.
                - If a diagram exists, describe it briefly.
                - Return only the extracted question.
                """,
                image
            ])

            return response.text

        # ------------------------------------------
        # SUBJECT DETECTION
        # ------------------------------------------

        elif task_type == "detect_subject":

            response = model.generate_content(
                f"""
                Identify the academic subject of the following question.

                Examples:
                Mathematics
                Physics
                Chemistry
                Biology
                Computer Science
                History
                Geography
                Economics
                Literature

                Return ONLY the subject name.

                Question:
                {prompt_text}
                """
            )

            return response.text.strip()

        # ------------------------------------------
        # STEP-BY-STEP EXPLANATION
        # ------------------------------------------

        elif task_type == "explain_doubt":

            response = model.generate_content(
                f"""
                You are Askora, an expert AI tutor.

                Explain the following question step-by-step.

                Rules:
                - Use simple language.
                - Explain concepts before solving.
                - Break the solution into numbered steps.
                - Highlight important formulas if needed.
                - Make it easy for a school or college student.

                Question:
                {prompt_text}
                """
            )

            return response.text

        # ------------------------------------------
        # PRACTICE PROBLEM
        # ------------------------------------------

        elif task_type == "generate_practice_problem":

            response = model.generate_content(
                f"""
                Based on the explanation below:

                {prompt_text}

                Create ONE similar practice problem.

                Rules:
                - Similar difficulty
                - Similar concept
                - Do NOT provide the answer
                - Do NOT provide hints
                """
            )

            return response.text

        # ------------------------------------------
        # QUIZ GENERATOR
        # ------------------------------------------

        elif task_type == "generate_quiz":

            response = model.generate_content(
                f"""
                Create 5 multiple-choice questions based on:

                {prompt_text}

                Format:

                Q1.
                A)
                B)
                C)
                D)

                Q2.
                ...

                After all questions add:

                ANSWER KEY:
                1.
                2.
                3.
                4.
                5.

                Keep questions educational and relevant.
                """
            )

            return response.text

        # ------------------------------------------
        # FOLLOW-UP CHAT
        # ------------------------------------------

        elif task_type == "follow_up":

            context = ""

            if chat_history:

                for msg in chat_history[-10:]:

                    if msg["type"] == "text":

                        role = (
                            "Student"
                            if msg["role"] == "user"
                            else "Tutor"
                        )

                        context += (
                            f"{role}: "
                            f"{msg['content']}\n"
                        )

            response = model.generate_content(
                f"""
                You are Askora AI Tutor.

                Previous conversation:

                {context}

                Student follow-up question:

                {prompt_text}

                Answer clearly and helpfully.
                """
            )

            return response.text

        return "Unsupported task."

    except Exception as e:

        return f"⚠️ Error: {str(e)}"


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

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
