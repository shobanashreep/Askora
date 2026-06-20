import streamlit as st


# ==========================================================
# Quiz Validation
# ==========================================================

def validate_quiz(quiz_data):
    """
    Ensure quiz format is valid.

    Expected format:
    [
        {
            "question": "...",
            "options": {
                "A": "...",
                "B": "...",
                "C": "...",
                "D": "..."
            },
            "answer": "A"
        }
    ]
    """

    if not isinstance(quiz_data, list):
        return []

    validated = []

    for item in quiz_data:

        if not isinstance(item, dict):
            continue

        question = item.get("question", "").strip()
        options = item.get("options", {})
        answer = item.get("answer", "").strip().upper()

        if not question:
            continue

        if not isinstance(options, dict):
            continue

        required = ["A", "B", "C", "D"]

        if not all(key in options for key in required):
            continue

        if answer not in required:
            continue

        validated.append({
            "question": question,
            "options": options,
            "answer": answer
        })

    return validated


# ==========================================================
# Initialize Quiz State
# ==========================================================

def initialize_quiz_state():
    """
    Initialize session state variables.
    """

    defaults = {
        "quiz_submitted": False,
        "quiz_score": 0,
        "quiz_total": 0,
        "quiz_answers": {}
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ==========================================================
# Reset Quiz State
# ==========================================================

def reset_quiz_state():
    """
    Call when a new image/question is uploaded.
    """

    st.session_state.quiz_submitted = False
    st.session_state.quiz_score = 0
    st.session_state.quiz_total = 0
    st.session_state.quiz_answers = {}


# ==========================================================
# Score Calculation
# ==========================================================

def calculate_score(quiz_data):
    """
    Compare selected answers with correct answers.
    """

    score = 0

    for index, question in enumerate(quiz_data):

        selected = st.session_state.quiz_answers.get(index)

        correct = question["answer"]

        if selected == correct:
            score += 1

    return score


# ==========================================================
# Quiz Renderer
# ==========================================================

def render_quiz(quiz_data):
    """
    Render interactive MCQ quiz.

    Returns:
        score_string
    """

    initialize_quiz_state()

    quiz_data = validate_quiz(quiz_data)

    if not quiz_data:
        st.warning("No quiz available.")
        return "0/0"

    st.subheader("📝 Quiz Challenge")

    st.caption("Test your understanding with 5 MCQs")

    st.session_state.quiz_total = len(quiz_data)

    for index, item in enumerate(quiz_data):

        st.markdown(
            f"### Q{index + 1}. {item['question']}"
        )

        options = item["options"]

        labels = [
            f"A. {options['A']}",
            f"B. {options['B']}",
            f"C. {options['C']}",
            f"D. {options['D']}"
        ]

        selected = st.radio(
            "Choose one answer",
            labels,
            key=f"quiz_q_{index}",
            label_visibility="collapsed"
        )

        if selected:
            st.session_state.quiz_answers[index] = selected[0]

    st.divider()

    submit = st.button(
        "✅ Submit Quiz",
        use_container_width=True,
        type="primary"
    )

    if submit:

        score = calculate_score(quiz_data)

        st.session_state.quiz_submitted = True
        st.session_state.quiz_score = score

    if st.session_state.quiz_submitted:

        score = st.session_state.quiz_score
        total = st.session_state.quiz_total

        percentage = (
            (score / total) * 100
            if total > 0
            else 0
        )

        st.success(
            f"🎯 Score: {score}/{total}"
        )

        st.progress(int(percentage))

        # Review Answers

        with st.expander(
            "📚 Review Answers",
            expanded=False
        ):

            for idx, item in enumerate(quiz_data):

                correct = item["answer"]

                selected = (
                    st.session_state.quiz_answers
                    .get(idx, "Not Answered")
                )

                if selected == correct:

                    st.success(
                        f"Q{idx+1}: Correct "
                        f"(Your Answer: {selected})"
                    )

                else:

                    st.error(
                        f"Q{idx+1}: Incorrect "
                        f"(Your Answer: {selected}) "
                        f"| Correct: {correct}"
                    )

    return (
        f"{st.session_state.quiz_score}/"
        f"{st.session_state.quiz_total}"
    )


# ==========================================================
# Notebook Helper
# ==========================================================

def get_quiz_score_string():
    """
    Safe score string for notebook storage.
    """

    score = st.session_state.get(
        "quiz_score",
        0
    )

    total = st.session_state.get(
        "quiz_total",
        0
    )

    return f"{score}/{total}"


# ==========================================================
# Quiz Statistics
# ==========================================================

def get_quiz_statistics():
    """
    Optional analytics card.
    """

    score = st.session_state.get(
        "quiz_score",
        0
    )

    total = st.session_state.get(
        "quiz_total",
        0
    )

    if total == 0:
        return {
            "score": 0,
            "total": 0,
            "percentage": 0
        }

    percentage = round(
        (score / total) * 100,
        2
    )

    return {
        "score": score,
        "total": total,
        "percentage": percentage
    }