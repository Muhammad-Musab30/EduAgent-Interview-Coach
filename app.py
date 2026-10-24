"""
EduAgent Interview Coach — Web Application Interface
=====================================================

Streamlit web interface strictly adhering to the LOCKED UI/UX specification
("Focused Intelligence" light theme) in EduAgent_Interview_Coach_UI_UX.md.

Design Constraints:
- Light theme only (Canvas #F6F7FB, Surface #FFFFFF).
- Brand Palette: Deep Navy #172554, Cobalt Blue #315EFB, Pale Blue #E9EEFF.
- Typography: Inter with comfortable line heights.
- No dark mode, no decorative glassmorphism, no neon colors.
- Clear 4-screen state flow: Start -> Question -> Instant Feedback -> Final Report.
"""

import streamlit as st

from interview_engine import InterviewEngine, InterviewSession
from report_generator import ReportGenerator


# =============================================================================
# Page Configuration & CSS Theme Injection
# =============================================================================

st.set_page_config(
    page_title="EduAgent Interview Coach",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

CUSTOM_CSS = """
<style>
/* Import Google Font: Inter */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Canvas & Global Reset */
html, body, [data-testid="stAppViewContainer"], .main {
    background-color: #F6F7FB !important;
    font-family: 'Inter', ui-sans-serif, system-ui, sans-serif !important;
    color: #0F172A !important;
}

[data-testid="stHeader"] {
    background-color: #FFFFFF !important;
    border-bottom: 1px solid #E2E8F0 !important;
}

/* Constrain content to centered clean workspace */
.block-container {
    max-width: 880px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
}

/* Typography Overrides */
h1, h2, h3, h4, h5, h6 {
    color: #172554 !important;
    font-family: 'Inter', sans-serif !important;
    letter-spacing: -0.01em !important;
}

p, span, label, div {
    color: #0F172A;
}

/* Primary Button: Cobalt Blue */
button[kind="primary"], .stButton > button[kind="primary"], div.stButton > button:first-child {
    background-color: #315EFB !important;
    color: #FFFFFF !important;
    border: 1px solid #315EFB !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    min-height: 44px !important;
    padding: 0.5rem 1.25rem !important;
    transition: background-color 0.15s ease !important;
    box-shadow: 0 1px 2px rgba(49, 94, 251, 0.1) !important;
}

button[kind="primary"]:hover, div.stButton > button:first-child:hover {
    background-color: #2649C7 !important;
    border-color: #2649C7 !important;
    color: #FFFFFF !important;
}

/* Secondary Button */
button[kind="secondary"] {
    background-color: #FFFFFF !important;
    color: #172554 !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    min-height: 44px !important;
}

button[kind="secondary"]:hover {
    background-color: #F1F4F9 !important;
    border-color: #94A3B8 !important;
}

/* Input & Textarea */
.stTextArea textarea {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 12px !important;
    color: #0F172A !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
    line-height: 1.5 !important;
    padding: 16px !important;
    box-shadow: none !important;
}

.stTextArea textarea:focus {
    border-color: #315EFB !important;
    box-shadow: 0 0 0 3px rgba(49, 94, 251, 0.16) !important;
}

/* Custom Cards */
.edu-card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.edu-question-card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 30px;
    margin-bottom: 24px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.edu-question-text {
    font-size: 21px;
    font-weight: 600;
    color: #0F172A;
    line-height: 1.5;
    margin-top: 10px;
    margin-bottom: 8px;
}

/* Badges */
.edu-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    margin-right: 8px;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}

.badge-easy { background-color: #DCFCE7; color: #166534; }
.badge-medium { background-color: #FEF3C7; color: #92400E; }
.badge-hard { background-color: #FEE2E2; color: #991B1B; }
.badge-mode { background-color: #F1F4F9; color: #172554; border: 1px solid #E2E8F0; }
.badge-topic { background-color: #E9EEFF; color: #315EFB; }

/* Semantic Feedback Boxes */
.edu-box-success {
    background-color: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 14px;
}
.edu-box-warning {
    background-color: #FFFBEB;
    border: 1px solid #FDE68A;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 14px;
}
.edu-box-error {
    background-color: #FEF2F2;
    border: 1px solid #FECACA;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 14px;
}
.edu-box-info {
    background-color: #EFF6FF;
    border: 1px solid #BFDBFE;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 14px;
}

.edu-score-display {
    font-size: 34px;
    font-weight: 700;
    color: #172554;
}

/* Top App Header */
.edu-header-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 0 20px 0;
    margin-bottom: 20px;
    border-bottom: 1px solid #E2E8F0;
}

.edu-brand-title {
    font-size: 18px;
    font-weight: 700;
    color: #172554;
    margin: 0;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# =============================================================================
# Session State Initialization
# =============================================================================

if "engine" not in st.session_state:
    st.session_state.engine = InterviewEngine()

if "session" not in st.session_state:
    st.session_state.session = None

if "view_mode" not in st.session_state:
    st.session_state.view_mode = "start"

if "last_evaluation" not in st.session_state:
    st.session_state.last_evaluation = None

if "last_decision" not in st.session_state:
    st.session_state.last_decision = None

if "last_question_answered" not in st.session_state:
    st.session_state.last_question_answered = None

if "answer_text" not in st.session_state:
    st.session_state.answer_text = ""

if "feedback_error_msg" not in st.session_state:
    st.session_state.feedback_error_msg = None


# =============================================================================
# Helper & Render Functions
# =============================================================================

def render_top_header():
    """Renders the top persistent branding header per UI/UX Section 11."""
    mode_label = (
        st.session_state.session.evaluation_provider.upper()
        if st.session_state.session
        else "LOCAL"
    )
    st.markdown(
        f"""
        <div class="edu-header-container">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="background: #E9EEFF; color: #315EFB; padding: 6px 10px; border-radius: 8px; font-size: 16px;">🧠</span>
                <span class="edu-brand-title">EduAgent Interview Coach</span>
            </div>
            <div>
                <span class="edu-badge badge-mode">⚙️ {mode_label} EVALUATION</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Screen 1: Start Screen (UI/UX Section 12.1)
# -----------------------------------------------------------------------------

def render_start_screen():
    render_top_header()

    st.markdown(
        """
        <div class="edu-card" style="text-align: center; padding: 36px 24px;">
            <h1 style="font-size: 28px; margin-bottom: 8px;">Technical Interview Practice</h1>
            <p style="font-size: 15px; color: #475569; max-width: 600px; margin: 0 auto 24px auto; line-height: 1.6;">
                Prepare for technical software developer interviews and viva examinations with structured, adaptive feedback. 
                Answer conceptual questions on Data Structures and Algorithms, receive targeted follow-ups, and identify your blind spots.
            </p>
            <div style="margin-bottom: 28px;">
                <span class="edu-badge badge-topic">📚 DSA · Stacks & Queues</span>
                <span class="edu-badge badge-mode">💼 Junior Software Developer</span>
                <span class="edu-badge badge-easy">🛡️ 100% Offline Capable</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(
            """
            <div class="edu-card" style="height: 100%;">
                <h3 style="font-size: 16px; margin-bottom: 12px;">🎯 How it works</h3>
                <ul style="font-size: 14px; color: #475569; padding-left: 20px; line-height: 1.7; margin: 0;">
                    <li><strong>Assess:</strong> You explain a core DSA concept in your own words.</li>
                    <li><strong>Evaluate:</strong> A 10-point rubric assesses correctness, concepts, and reasoning.</li>
                    <li><strong>Adapt:</strong> Targeted follow-up questions address gaps or misconceptions.</li>
                    <li><strong>Report:</strong> Receive a comprehensive performance report with revision tips.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="edu-card" style="height: 100%;">
                <h3 style="font-size: 16px; margin-bottom: 12px;">💡 Tips for success</h3>
                <ul style="font-size: 14px; color: #475569; padding-left: 20px; line-height: 1.7; margin: 0;">
                    <li>Write complete, explanatory sentences rather than single-word answers.</li>
                    <li>Explain <em>why</em> operations work (e.g. why LIFO prevents arbitrary removal).</li>
                    <li>You can request a hint at any time if you feel stuck.</li>
                    <li>Take your time; clarity and reasoning earn top scores.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    if st.button("Start Interview", type="primary", use_container_width=True):
        st.session_state.session = st.session_state.engine.start_session(provider="local")
        st.session_state.view_mode = "question"
        st.session_state.answer_text = ""
        st.session_state.last_evaluation = None
        st.session_state.feedback_error_msg = None
        st.rerun()


# -----------------------------------------------------------------------------
# Screen 2: Interview Workspace Screen (UI/UX Section 12.2)
# -----------------------------------------------------------------------------

def render_question_screen():
    render_top_header()
    session: InterviewSession = st.session_state.session
    engine: InterviewEngine = st.session_state.engine

    current_q = engine.get_current_question(session)
    if not current_q:
        st.error("Question could not be loaded. Please restart the session.")
        if st.button("Return to Start"):
            st.session_state.view_mode = "start"
            st.rerun()
        return

    question_idx = len(session.attempts) + 1
    difficulty = current_q.get("difficulty", "medium").lower()
    topic = current_q.get("topic", "DSA")

    # Progress & Metadata Header
    diff_badge_class = f"badge-{difficulty}"
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
            <div>
                <span class="edu-badge badge-topic">{topic}</span>
                <span class="edu-badge {diff_badge_class}">{difficulty.upper()}</span>
            </div>
            <div style="font-size: 13px; font-weight: 500; color: #475569;">
                Question {question_idx} of ~5–10
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Question Display Card
    st.markdown(
        f"""
        <div class="edu-question-card">
            <div style="font-size: 13px; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;">INTERVIEW QUESTION</div>
            <div class="edu-question-text">{current_q.get("question", "")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Hint Toggle
    with st.expander("💡 Need a hint? Click here to view conceptual guidance"):
        hint_text = engine.request_hint(session)
        st.markdown(
            f"""
            <div class="edu-box-info" style="margin: 0;">
                <strong style="color: #1E40AF;">Hint:</strong> {hint_text}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Answer Input Field
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    user_answer = st.text_area(
        label="Your Explanation",
        placeholder="Explain your answer step by step. Include key principles, operation mechanics, and reasoning...",
        value=st.session_state.answer_text,
        height=180,
        key="student_response_input",
    )

    # Validation message if user previously tried submitting blank
    if st.session_state.feedback_error_msg:
        st.markdown(
            f"""
            <div class="edu-box-warning" style="margin-top: 10px;">
                ⚠️ <strong>Notice:</strong> {st.session_state.feedback_error_msg}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    btn_col1, btn_col2 = st.columns([3, 1])

    with btn_col1:
        if st.button("Submit Answer", type="primary", use_container_width=True):
            if not user_answer.strip():
                st.session_state.feedback_error_msg = "Please write an explanation before submitting."
                st.rerun()

            with st.spinner("Evaluating your response against the rubric..."):
                eval_res, decision, is_done = engine.submit_answer(
                    session,
                    user_answer.strip(),
                    question_id=current_q["id"],
                )

            st.session_state.last_evaluation = eval_res
            st.session_state.last_decision = decision
            st.session_state.last_question_answered = current_q
            st.session_state.answer_text = ""
            st.session_state.feedback_error_msg = None
            st.session_state.view_mode = "feedback"
            st.rerun()

    with btn_col2:
        if st.button("End Interview", type="secondary", use_container_width=True):
            engine.end_session(session)
            st.session_state.view_mode = "report"
            st.rerun()


# -----------------------------------------------------------------------------
# Screen 3: Instant Feedback Screen (UI/UX Section 12.3)
# -----------------------------------------------------------------------------

def render_feedback_screen():
    render_top_header()
    session: InterviewSession = st.session_state.session
    eval_res = st.session_state.last_evaluation
    decision = st.session_state.last_decision
    question_info = st.session_state.last_question_answered

    if not eval_res or not decision:
        st.session_state.view_mode = "question"
        st.rerun()
        return

    score = eval_res.get("score", 0)
    breakdown = eval_res.get("score_breakdown", {})
    correct_pts = eval_res.get("correct_points", [])
    missing_pts = eval_res.get("missing_concepts", [])
    misconceptions = eval_res.get("misconceptions", [])
    feedback_text = eval_res.get("feedback", "")
    student_explanation = decision.student_explanation

    # Score Card
    st.markdown(
        f"""
        <div class="edu-card" style="text-align: center; padding: 24px;">
            <div style="font-size: 13px; font-weight: 600; color: #64748B; text-transform: uppercase;">EVALUATION SCORE</div>
            <div class="edu-score-display">{score} / 10</div>
            <p style="font-size: 15px; color: #475569; margin: 8px 0 16px 0;">{feedback_text}</p>
            <div style="display: flex; justify-content: center; gap: 16px; font-size: 13px; color: #475569; border-top: 1px solid #E2E8F0; padding-top: 12px;">
                <span><strong>Correctness:</strong> {breakdown.get('technical_correctness', 0)}/4</span>
                <span><strong>Key Concepts:</strong> {breakdown.get('key_concepts', 0)}/3</span>
                <span><strong>Reasoning:</strong> {breakdown.get('reasoning', 0)}/2</span>
                <span><strong>Clarity:</strong> {breakdown.get('clarity', 0)}/1</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Strengths / Correct Points
    if correct_pts:
        pts_html = "".join(f"<li>{pt}</li>" for pt in correct_pts)
        st.markdown(
            f"""
            <div class="edu-box-success">
                <strong style="color: #166534; font-size: 14px;">✅ Demonstrated Correctly:</strong>
                <ul style="margin: 8px 0 0 0; padding-left: 20px; font-size: 14px; color: #166534; line-height: 1.5;">
                    {pts_html}
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Missing Concepts
    if missing_pts:
        missing_html = "".join(f"<li>{pt}</li>" for pt in missing_pts)
        st.markdown(
            f"""
            <div class="edu-box-warning">
                <strong style="color: #92400E; font-size: 14px;">⚠️ Missing Concepts to Include:</strong>
                <ul style="margin: 8px 0 0 0; padding-left: 20px; font-size: 14px; color: #92400E; line-height: 1.5;">
                    {missing_html}
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Misconceptions Detected
    if misconceptions:
        misc_html = "".join(f"<li>{m}</li>" for m in misconceptions)
        st.markdown(
            f"""
            <div class="edu-box-error">
                <strong style="color: #991B1B; font-size: 14px;">🚫 Misconception Detected:</strong>
                <ul style="margin: 8px 0 0 0; padding-left: 20px; font-size: 14px; color: #991B1B; line-height: 1.5;">
                    {misc_html}
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Adaptation Next Step Card
    st.markdown(
        f"""
        <div class="edu-box-info">
            <strong style="color: #1E40AF; font-size: 14px;">🎯 Next Learning Step:</strong>
            <p style="margin: 6px 0 0 0; font-size: 14px; color: #1E40AF; line-height: 1.5;">
                {student_explanation}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    if session.session_status == "completed":
        if st.button("View Final Report", type="primary", use_container_width=True):
            st.session_state.view_mode = "report"
            st.rerun()
    else:
        if st.button("Continue to Next Question", type="primary", use_container_width=True):
            st.session_state.view_mode = "question"
            st.rerun()


# -----------------------------------------------------------------------------
# Screen 4: Final Report Screen (UI/UX Section 12.4)
# -----------------------------------------------------------------------------

def render_report_screen():
    render_top_header()
    session: InterviewSession = st.session_state.session

    if not session:
        st.session_state.view_mode = "start"
        st.rerun()
        return

    report = ReportGenerator.generate_report(session)

    tier = report["performance_tier"]
    tier_badge_class = "badge-easy" if tier == "Proficient" else ("badge-medium" if tier == "Developing" else "badge-hard")

    # Header Card
    st.markdown(
        f"""
        <div class="edu-card" style="text-align: center; padding: 30px 20px;">
            <div style="font-size: 13px; font-weight: 600; color: #64748B; text-transform: uppercase;">SESSION COMPLETED</div>
            <h1 style="font-size: 26px; margin: 8px 0;">Interview Performance Report</h1>
            <div style="margin: 12px 0;">
                <span class="edu-badge {tier_badge_class}" style="font-size: 14px; padding: 5px 14px;">TIER: {tier.upper()}</span>
            </div>
            <div class="edu-score-display" style="margin: 14px 0 6px 0;">{report['total_score']} / {report['max_possible_score']} <span style="font-size: 20px; font-weight: 500; color: #64748B;">({report['percentage']}%)</span></div>
            <p style="font-size: 15px; color: #475569; max-width: 600px; margin: 0 auto;">{report['tier_summary']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Core Performance Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Questions", report["attempts_count"])
    with col2:
        st.metric("Avg Score", f"{report['average_score']}/10")
    with col3:
        st.metric("Hints Used", report["hints_used"])
    with col4:
        st.metric("Mode", report["evaluation_mode"].title())

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Strengths vs Gaps Columns
    col_str, col_gap = st.columns(2)

    with col_str:
        st.markdown(
            """
            <div class="edu-card" style="height: 100%;">
                <h3 style="font-size: 16px; margin-bottom: 12px; color: #166534;">✅ Demonstrated Strengths</h3>
            """,
            unsafe_allow_html=True,
        )
        if report["demonstrated_concepts"]:
            for c in report["demonstrated_concepts"]:
                st.markdown(f"- **{c}**")
        else:
            st.markdown("- *No concepts fully demonstrated in this session.*")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_gap:
        st.markdown(
            """
            <div class="edu-card" style="height: 100%;">
                <h3 style="font-size: 16px; margin-bottom: 12px; color: #92400E;">🔍 Areas to Practice</h3>
            """,
            unsafe_allow_html=True,
        )
        if report["unresolved_concepts"]:
            for c in report["unresolved_concepts"]:
                st.markdown(f"- {c}")
        else:
            st.markdown("- *No unresolved gaps detected.*")
        st.markdown("</div>", unsafe_allow_html=True)

    # Tailored Recommendations Card
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="edu-card">
            <h3 style="font-size: 16px; margin-bottom: 14px; color: #172554;">📖 Priority Study Recommendations</h3>
        """,
        unsafe_allow_html=True,
    )
    for idx, rec in enumerate(report["recommendations"], 1):
        st.markdown(f"**{idx}.** {rec}")
    st.markdown("</div>", unsafe_allow_html=True)

    # Detailed Attempt History Expander
    if report["question_summaries"]:
        with st.expander("📋 View Question-by-Question Attempt History"):
            for q_att in report["question_summaries"]:
                st.markdown(
                    f"""
                    <div style="border-bottom: 1px solid #E2E8F0; padding: 12px 0;">
                        <div style="display: flex; justify-content: space-between;">
                            <strong>Q{q_att['number']}: {q_att['topic']} ({q_att['difficulty'].upper()})</strong>
                            <span class="edu-badge badge-mode">Score: {q_att['score']} / 10</span>
                        </div>
                        <p style="font-size: 14px; color: #0F172A; margin: 4px 0;">{q_att['question_text']}</p>
                        <p style="font-size: 13px; color: #64748B; margin: 2px 0;"><em>Feedback:</em> {q_att['feedback']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # Disclaimer
    st.markdown(
        f"""
        <div style="font-size: 12px; color: #64748B; margin: 20px 0; text-align: center;">
            <em>{report['disclaimer']}</em>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Start New Interview", type="primary", use_container_width=True):
        st.session_state.session = None
        st.session_state.view_mode = "start"
        st.rerun()


# =============================================================================
# Router Main Loop
# =============================================================================

def main():
    view = st.session_state.view_mode

    if view == "start":
        render_start_screen()
    elif view == "question":
        render_question_screen()
    elif view == "feedback":
        render_feedback_screen()
    elif view == "report":
        render_report_screen()
    else:
        render_start_screen()


if __name__ == "__main__":
    main()
