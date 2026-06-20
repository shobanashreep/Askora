import os
from datetime import datetime

import streamlit as st
from PIL import Image

from utils.llm_utils import (
    analyze_question_image,
    create_notebook_entry,
    ask_followup_question
)

from utils.quiz_utils import (
    reset_quiz_state,
    render_quiz,
    get_quiz_score_string
)


from utils.pdf_utils import (
    generate_notebook_pdf,
    get_pdf_filename
)


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Askora",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown(
    """
<style>

.main {
    padding-top: 1rem;
}

.askora-title {
    font-size: 3rem;
    font-weight: 800;
    text-align: center;
    margin-bottom: 0.2rem;
}

.askora-subtitle {
    text-align: center;
    color: #888;
    margin-bottom: 2rem;
}

.badge-row {
    display: flex;
    gap: 12px;
    margin-bottom: 15px;
}

.subject-badge {
    background-color: #2563eb;
    color: white;
    padding: 8px 16px;
    border-radius: 999px;
    font-weight: 600;
    display: inline-block;
}

.difficulty-badge {
    background-color: #16a34a;
    color: white;
    padding: 8px 16px;
    border-radius: 999px;
    font-weight: 600;
    display: inline-block;
}

.card {
    background-color: #111827;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
}

.section-title {
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: 10px;
}

.concept-box {
    background: rgba(255,255,255,0.05);
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 8px;
}

.footer {
    text-align:center;
    margin-top:40px;
    color:gray;
}

</style>
""",
    unsafe_allow_html=True
)


# ==========================================================
# SESSION STATE
# ==========================================================

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "notebook" not in st.session_state:
    st.session_state.notebook = []

if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = None

if "processing_complete" not in st.session_state:
    st.session_state.processing_complete = False


# ==========================================================
# API KEY
# ==========================================================

api_key = None

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY")


# ==========================================================
# HEADER
# ==========================================================

st.markdown(
    """
<div class="askora-title">
🧠 Askora
</div>

<div class="askora-subtitle">
AI-Powered Student Doubt Solver
</div>
""",
    unsafe_allow_html=True
)


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.header("⚙️ Askora")

    st.info(
        """
Upload a question image and Askora will:

✅ Extract Question

✅ Detect Subject

✅ Detect Difficulty

✅ Explain Step-by-Step

✅ Generate Practice Problem

✅ Create Quiz
"""
    )

    st.divider()

    st.metric(
        "Notebook Entries",
        len(st.session_state.notebook)
    )

    st.divider()

    if st.button(
        "🗑️ Clear Notebook",
        use_container_width=True
    ):
        st.session_state.notebook = []
        st.success("Notebook cleared.")


# ==========================================================
# API KEY CHECK
# ==========================================================

if not api_key:

    st.error(
        """
Gemini API key not found.

Add GEMINI_API_KEY inside:

.streamlit/secrets.toml

Example:

GEMINI_API_KEY="YOUR_KEY"
"""
    )

    st.stop()


# ==========================================================
# IMAGE UPLOAD
# ==========================================================

uploaded_file = st.file_uploader(
    "📤 Upload Question Image",
    type=["png", "jpg", "jpeg"]
)


# ==========================================================
# NEW IMAGE RESET
# ==========================================================

if uploaded_file:

    # Limit upload size to 10 MB
    if uploaded_file.size > 10 * 1024 * 1024:

        st.error(
            "Image must be under 10 MB."
        )

        st.stop()

    current_name = uploaded_file.name

    if (
        st.session_state.last_uploaded_file
        != current_name
    ):

        reset_quiz_state()

        st.session_state.chat_history = []

        st.session_state.analysis_result = None

        st.session_state.processing_complete = False

        st.session_state.last_uploaded_file = (
            current_name
        )

# ==========================================================
# PROCESS BUTTON
# ==========================================================

if uploaded_file:

    image = Image.open(uploaded_file)

    col1, col2 = st.columns(
        [1, 1]
    )

    with col1:

        st.image(
            image,
            caption="Uploaded Question",
            use_container_width=True
        )

    with col2:

        if st.button(
            "🚀 Solve Doubt",
            type="primary",
            use_container_width=True
        ):

            try:

                with st.spinner(
                    "Analyzing question..."
                ):

                    result = analyze_question_image(
                        uploaded_file,
                        api_key
                    )

                st.session_state.analysis_result = (
                    result
                )

                st.session_state.processing_complete = (
                    True
                )

                st.success(
                    "Analysis completed!"
                )

                st.rerun()

            except Exception as e:

                error_text = str(e)

                if "503" in error_text:

                    st.error(
                        "🚦 Gemini servers are busy right now. Please try again in a few seconds."
                    )

                elif "429" in error_text:

                    st.error(
                        "⚠️ Gemini quota exceeded. Please try later."
                    )

                else:

                    st.error(error_text)


# ==========================================================
# DISPLAY RESULTS
# ==========================================================

if (
    st.session_state.processing_complete
    and st.session_state.analysis_result
):

    result = st.session_state.analysis_result

    subject = result.get(
        "subject",
        "General Knowledge"
    )

    difficulty = result.get(
        "difficulty",
        "Medium"
    )

    question = result.get(
        "question",
        ""
    )

    explanation = result.get(
        "explanation",
        ""
    )

    concepts = result.get(
        "key_concepts",
        []
    )

    practice_problem = result.get(
        "practice_problem",
        ""
    )

    # ======================================================
    # BADGES
    # ======================================================

    st.markdown(
        f"""
<div class="badge-row">
<span class="subject-badge">
📚 {subject}
</span>

<span class="difficulty-badge">
🎯 {difficulty}
</span>
</div>
""",
        unsafe_allow_html=True
    )

    # ======================================================
    # QUESTION
    # ======================================================

    st.markdown(
        """
### 📄 Extracted Question
"""
    )

    st.write(question)

    # ======================================================
    # EXPLANATION
    # ======================================================

    st.markdown(
        """
### 🧠 AI Explanation
"""
    )

    st.write(explanation)

    # ======================================================
    # KEY CONCEPTS
    # ======================================================

    st.markdown(
        """
### 🔑 Key Concepts
"""
    )

    if concepts:

        for concept in concepts:

            st.markdown(
                f"""
<div class="concept-box">
• {concept}
</div>
""",
                unsafe_allow_html=True
            )

    else:

        st.info(
            "No concepts generated."
        )

    # ======================================================
    # PRACTICE PROBLEM
    # ======================================================

    st.markdown(
        """
### ✍️ Practice Problem
"""
    )

    st.write(practice_problem)

    st.divider()

    # ==========================================================
    # QUIZ SECTION
    # ==========================================================

    quiz_data = result.get("quiz", [])

    quiz_score = render_quiz(quiz_data)

    st.divider()


    # ==========================================================
    # SAVE TO NOTEBOOK
    # ==========================================================

    col_save, col_space = st.columns([1, 3])

    with col_save:

        if st.button(
            "📒 Save To Notebook",
            use_container_width=True
        ):

            entry = create_notebook_entry(
                result,
                quiz_score
            )

            entry["timestamp"] = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            if entry not in st.session_state.notebook:
             st.session_state.notebook.append(entry)

            st.success(
                "Saved to notebook."
            )

    st.divider()


    # ==========================================================
    # FOLLOW-UP CHAT
    # ==========================================================

    from utils.llm_utils import (
        ask_followup_question
    )

    st.markdown(
        """
    ### 💬 Follow-Up Doubts
    Ask questions related to this doubt.
    """
    )

    # Display Chat History

    for chat in st.session_state.chat_history:

        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

    # Chat Input

    user_followup = st.chat_input(
        "Ask a follow-up question..."
    )

    if user_followup:

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": user_followup
            }
        )

        with st.chat_message("user"):
            st.markdown(user_followup)

        with st.spinner(
            "Thinking..."
        ):

            answer = ask_followup_question(
                api_key=api_key,
                original_question=question,
                explanation=explanation,
                user_question=user_followup
            )

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        with st.chat_message(
            "assistant"
        ):
            st.markdown(answer)

    st.divider()


    # ==========================================================
    # NOTEBOOK HISTORY
    # ==========================================================

    st.markdown(
        """
    ## 📚 Askora Notebook
    """
    )

    if not st.session_state.notebook:

        st.info(
            "No notebook entries saved yet."
        )

    else:

        for idx, entry in enumerate(
            reversed(
                st.session_state.notebook
            ),
            start=1
        ):

            with st.expander(
                f"📖 Entry {idx} | "
                f"{entry.get('subject', '')}"
            ):

                st.markdown(
                    f"""
    **Subject:** {entry.get('subject', '')}

    **Difficulty:** {entry.get('difficulty', '')}

    **Quiz Score:** {entry.get('quiz_score', '')}

    **Timestamp:** {entry.get('timestamp', '')}
    """
                )

                st.markdown(
                    "### Question"
                )
                st.write(
                    entry.get(
                        "question",
                        ""
                    )
                )

                st.markdown(
                    "### Explanation"
                )
                st.write(
                    entry.get(
                        "explanation",
                        ""
                    )
                )

                st.markdown(
                    "### Practice Problem"
                )
                st.write(
                    entry.get(
                        "practice_problem",
                        ""
                    )
                )

    st.divider()


    # ==========================================================
    # PDF EXPORT
    # ==========================================================

    st.markdown(
        """
    ## 📄 Export Notebook
    """
    )

    if st.session_state.notebook:

        try:

            pdf_bytes = generate_notebook_pdf(
                st.session_state.notebook
            )

            st.download_button(
                label="📥 Download PDF Notebook",
                data=pdf_bytes,
                file_name=get_pdf_filename(),
                mime="application/pdf",
                use_container_width=True
            )

        except Exception as e:

            st.error(
                f"PDF Export Error: {str(e)}"
            )

    else:

        st.info(
            "Save at least one notebook entry to export PDF."
        )


    # ==========================================================
    # ANALYTICS CARDS
    # ==========================================================

    if st.session_state.notebook:

        total_entries = len(
            st.session_state.notebook
        )

        scores = []

        for entry in st.session_state.notebook:

            score_text = entry.get(
                "quiz_score",
                "0/0"
            )

            try:

                score, total = score_text.split(
                    "/"
                )

                percentage = (
                    int(score)
                    / max(
                        int(total),
                        1
                    )
                ) * 100

                scores.append(
                    percentage
                )

            except Exception:
                pass

        avg_score = (
            round(
                sum(scores)
                / len(scores),
                1
            )
            if scores
            else 0
        )

        st.divider()

        st.markdown(
            """
    ## 📊 Learning Analytics
    """
        )

        c1, c2 = st.columns(2)

        with c1:
            st.metric(
                "Notebook Entries",
                total_entries
            )

        with c2:
            st.metric(
                "Average Quiz %",
                f"{avg_score}%"
            )


    # ==========================================================
    # FOOTER
    # ==========================================================

    st.markdown(
        """
    <div class="footer">

    <hr>

    🧠 Askora — AI Powered Student Doubt Solver

    Built with Streamlit + Gemini

    Hackathon Edition 🚀

    </div>
    """,
        unsafe_allow_html=True
    )