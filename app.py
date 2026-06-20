import streamlit as st
from PIL import Image
import tempfile

from utils.llm_utils import (
    get_llm_response,
    detect_subject,
    generate_practice_problem,
    generate_quiz
)

from utils.pdf_utils import create_pdf_from_chat

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Askora AI Tutor",
    page_icon="🧠",
    layout="centered"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

.subject-badge {
    background-color: #e1f5fe;
    color: #01579b;
    padding: 6px 14px;
    border-radius: 18px;
    font-weight: bold;
    display: inline-block;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_subject" not in st.session_state:
    st.session_state.current_subject = None

if "last_uploaded" not in st.session_state:
    st.session_state.last_uploaded = None

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🧠 Askora")
st.caption("Your personal 24/7 tutor for any subject.")

# --------------------------------------------------
# FUNCTIONS
# --------------------------------------------------

def display_chat_history():

    for i, message in enumerate(st.session_state.messages):

        with st.chat_message(message["role"]):

            if message["type"] == "image":

                st.image(
                    message["content"],
                    caption="Uploaded Question",
                    use_container_width=True
                )

            elif message["type"] == "text":

                st.markdown(message["content"])

            elif message["type"] == "practice_button":

                if st.button(
                    message["content"],
                    key=f"practice_{i}"
                ):
                    handle_practice_problem_request()


def handle_image_upload(uploaded_file):

    if uploaded_file is None:
        return

    image = Image.open(uploaded_file)

    st.session_state.messages = []
    st.session_state.current_subject = None

    st.session_state.messages.append({
        "role": "user",
        "type": "image",
        "content": image
    })

    with st.spinner("🔍 Reading your question..."):

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".jpg"
        ) as tmp:

            image.save(tmp.name)

            question_text = get_llm_response(
                "",
                "extract_question",
                image_path=tmp.name
            )

        subject = detect_subject(question_text)

        st.session_state.current_subject = subject

        explanation = get_llm_response(
            question_text,
            "explain_doubt"
        )

        st.session_state.messages.append({
            "role": "assistant",
            "type": "text",
            "content": explanation
        })

        st.session_state.messages.append({
            "role": "assistant",
            "type": "practice_button",
            "content": "📝 Show me a similar practice problem"
        })

    st.rerun()


def handle_follow_up_question(prompt):

    st.session_state.messages.append({
        "role": "user",
        "type": "text",
        "content": prompt
    })

    with st.spinner("🤔 Thinking..."):

        response = get_llm_response(
            prompt,
            "follow_up",
            chat_history=st.session_state.messages
        )

        st.session_state.messages.append({
            "role": "assistant",
            "type": "text",
            "content": response
        })

    st.rerun()


def handle_practice_problem_request():

    last_explanation = ""

    for msg in reversed(st.session_state.messages):

        if (
            msg["role"] == "assistant"
            and msg["type"] == "text"
        ):
            last_explanation = msg["content"]
            break

    with st.spinner("📝 Creating a practice problem..."):

        problem = generate_practice_problem(
            last_explanation
        )

        st.session_state.messages.append({
            "role": "assistant",
            "type": "text",
            "content": f"## Practice Problem\n\n{problem}"
        })

    st.rerun()


def handle_quiz_request():

    last_explanation = ""

    for msg in reversed(st.session_state.messages):

        if (
            msg["role"] == "assistant"
            and msg["type"] == "text"
        ):
            last_explanation = msg["content"]
            break

    with st.spinner("🎯 Generating quiz..."):

        quiz = generate_quiz(last_explanation)

        st.session_state.messages.append({
            "role": "assistant",
            "type": "text",
            "content": f"## Quiz\n\n{quiz}"
        })

    st.rerun()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.header("📤 Upload Question")

    uploaded_file = st.file_uploader(
        "Take a photo or upload an image",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file:

        if st.session_state.last_uploaded != uploaded_file.name:

            st.session_state.last_uploaded = uploaded_file.name

            handle_image_upload(uploaded_file)

    st.divider()

    st.header("📓 Your Notebook")

    if st.session_state.messages:

        if st.button(
            "🎯 Generate Quiz",
            use_container_width=True
        ):
            handle_quiz_request()

        pdf_data = create_pdf_from_chat(
            st.session_state.messages
        )

        st.download_button(
            label="📥 Download Doubt Notebook",
            data=pdf_data,
            file_name="my_doubt_notebook.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    else:

        st.info(
            "Upload a question to start your notebook."
        )

# --------------------------------------------------
# SUBJECT BADGE
# --------------------------------------------------

if st.session_state.current_subject:

    st.markdown(
        f"""
        <div class="subject-badge">
        📚 {st.session_state.current_subject}
        </div>
        """,
        unsafe_allow_html=True
    )

# --------------------------------------------------
# MAIN CHAT
# --------------------------------------------------

if not st.session_state.messages:

    st.info(
        "👋 Welcome! Upload an image of a question "
        "and Askora will explain it step-by-step."
    )

else:

    display_chat_history()

# --------------------------------------------------
# FOLLOW-UP CHAT
# --------------------------------------------------

if st.session_state.messages:

    prompt = st.chat_input(
        "Ask a follow-up question..."
    )

    if prompt:

        handle_follow_up_question(prompt)