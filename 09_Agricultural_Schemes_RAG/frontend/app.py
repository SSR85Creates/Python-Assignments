
import streamlit as st
import requests
from collections import Counter
from datetime import datetime

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AgriScheme Intelligence",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "questions" not in st.session_state:
    st.session_state.questions = []

if "sources_used" not in st.session_state:
    st.session_state.sources_used = []

if "indexed" not in st.session_state:
    st.session_state.indexed = False

if "answer_history" not in st.session_state:
    st.session_state.answer_history = []

# --------------------------------------------------
# CUSTOM WHITE AND GREEN DESIGN
# --------------------------------------------------

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background-color: #F5F9F5;
    color: #193D2B;
}

[data-testid="stSidebar"] {
    background-color: #123D2B;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #E0EFE5 !important;
}

.hero {
    background: linear-gradient(115deg, #123D2B, #237849);
    padding: 35px;
    border-radius: 20px;
    color: white;
    margin-bottom: 25px;
}

.hero h1 {
    color: white;
    font-size: 34px;
    font-weight: 800;
    margin-bottom: 8px;
}

.hero p {
    color: #DCEFE1;
    font-size: 15px;
}

.metric-card {
    background: white;
    padding: 22px;
    border-radius: 15px;
    border: 1px solid #E1EBE2;
    box-shadow: 0 3px 12px rgba(20, 70, 40, 0.05);
    min-height: 125px;
}

.metric-label {
    color: #718477;
    font-size: 13px;
    font-weight: 600;
}

.metric-value {
    color: #174A30;
    font-size: 30px;
    font-weight: 800;
    margin-top: 8px;
}

.section-title {
    color: #174A30;
    font-size: 22px;
    font-weight: 800;
    margin-top: 18px;
    margin-bottom: 12px;
}

.answer-card {
    background: white;
    padding: 24px;
    border-radius: 15px;
    border-left: 5px solid #32965C;
    margin: 12px 0;
    box-shadow: 0 3px 12px rgba(20, 70, 40, 0.05);
}

.source-card {
    background: #EAF5EC;
    border: 1px solid #D4E8D8;
    border-radius: 10px;
    padding: 12px 15px;
    margin: 8px 0;
    color: #174A30;
}

div.stButton > button {
    background: #21834D;
    color: white;
    border: none;
    border-radius: 9px;
    padding: 10px 20px;
    font-weight: 700;
}

div.stButton > button:hover {
    background: #145F36;
    color: white;
    border: none;
}

.stTextInput input {
    border-radius: 10px;
}

div[data-testid="stMetric"] {
    background: white;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #E1EBE2;
}

.footer {
    text-align: center;
    color: #819187;
    font-size: 12px;
    padding: 25px;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def check_backend():
    try:
        response = requests.get(API_URL, timeout=3)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def metric_card(label, value, icon):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{icon} {label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def get_document_names():
    return list(dict.fromkeys(
        source["filename"]
        for source in st.session_state.sources_used
    ))


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown("# 🌿 AgriScheme")
    st.markdown("### INTELLIGENCE PLATFORM")

    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Dashboard",
            "AI Scheme Assistant",
            "Document Explorer",
            "Analytics",
            "About"
        ]
    )

    st.divider()

    backend_status = check_backend()

if backend_status:
    st.success("● BACKEND CONNECTED")
else:
    st.error("● BACKEND OFFLINE")
    st.caption("Powered by LangChain + FAISS + Ollama")
st.divider()
st.markdown("**AGRICULTURE • TECHNOLOGY • AI**")


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

if page == "Dashboard":

    st.markdown("""
    <div class="hero">
        <h1>🌾 Agricultural Schemes Intelligence</h1>
        <p>
        Discover government agricultural schemes through
        AI-powered document intelligence.
        </p>
        <p>
        Ask questions. Explore benefits. Find information
        directly from your scheme documents.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Platform Overview</div>',
                unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "PDF Documents Referenced",
            len(get_document_names()),
            "📚"
        )

    with c2:
        metric_card(
            "Questions Asked",
            len(st.session_state.questions),
            "💬"
        )

    with c3:
        metric_card(
            "Unique Pages Referenced",
            len({
                (s["filename"], s["page"])
                for s in st.session_state.sources_used
            }),
            "📄"
        )

    with c4:
        metric_card(
            "Answers Generated",
            len(st.session_state.answer_history),
            "🤖"
        )

    st.markdown('<div class="section-title">Get Started</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.subheader("🤖 AI Scheme Assistant")
            st.write(
                "Ask questions about agricultural schemes "
                "and receive answers with document references."
            )
            if st.button("Explore AI Assistant", use_container_width=True):
                st.session_state["navigation"] = "AI Scheme Assistant"
                st.rerun()

    with col2:
        with st.container(border=True):
            st.subheader("📚 Document Explorer")
            st.write(
                "Explore the government scheme documents "
                "used by the application."
            )
            if st.button("Explore Documents", use_container_width=True):
                st.session_state["navigation"] = "Document Explorer"
                st.rerun()

    st.markdown('<div class="section-title">Suggested Questions</div>',
                unsafe_allow_html=True)

    suggestions = [
        "What agricultural schemes are available?",
        "What are the eligibility criteria for farmers?",
        "What benefits are provided under loan waiver schemes?",
        "How can farmers apply for subsidies?"
    ]

    for suggestion in suggestions:
        st.markdown(f"- {suggestion}")


# --------------------------------------------------
# AI SCHEME ASSISTANT
# --------------------------------------------------

elif page == "AI Scheme Assistant":

    st.markdown("""
    <div class="hero">
        <h1>🤖 AI Agricultural Assistant</h1>
        <p>Ask your questions and explore information from government scheme PDFs.</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.indexed:

        st.warning(
            "Documents must be indexed before asking questions."
        )

        if st.button("Process Government Scheme PDFs", use_container_width=True):

            with st.spinner("Reading PDFs, creating embeddings and indexing documents..."):

                try:
                    response = requests.post(
                        f"{API_URL}/index",
                        timeout=600
                    )

                    response.raise_for_status()

                    st.session_state.indexed = True

                    st.success("Documents indexed successfully!")

                    st.rerun()

                except requests.exceptions.RequestException as e:
                    st.error(f"Indexing failed: {e}")

    else:

        st.success("Knowledge base is ready.")

    st.divider()

    st.subheader("Ask Your Question")

    question = st.text_area(
        "Your question",
        placeholder="Example: What are the eligibility requirements for agricultural loan waiver?",
        height=100
    )

    if st.button("Generate Answer 🌿", use_container_width=True):

        if not question.strip():
            st.warning("Please enter a question.")

        elif not st.session_state.indexed:
            st.warning("Please index the documents first.")

        else:

            with st.spinner("Searching government documents and generating your answer..."):

                try:

                    response = requests.post(
                        f"{API_URL}/ask",
                        json={"question": question},
                        timeout=180
                    )

                    response.raise_for_status()

                    result = response.json()

                    answer = result["answer"]
                    sources = result["sources"]

                    st.session_state.questions.append(question)
                    st.session_state.sources_used.extend(sources)

                    st.session_state.answer_history.append({
                        "question": question,
                        "answer": answer,
                        "sources": sources,
                        "time": datetime.now().strftime("%H:%M:%S")
                    })

                    st.markdown("### Answer")

                    st.markdown(
                        f'<div class="answer-card">{answer}</div>',
                        unsafe_allow_html=True
                    )

                    st.markdown("### 📚 Source References")

                    if sources:

                        for source in sources:

                            st.markdown(
                                f"""
                                <div class="source-card">
                                📄 <b>{source['filename']}</b><br>
                                Page Number: {source['page']}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                    else:
                        st.info("No source references were returned.")

                except requests.exceptions.RequestException as e:
                    st.error(f"Unable to retrieve answer: {e}")


# --------------------------------------------------
# DOCUMENT EXPLORER
# --------------------------------------------------

elif page == "Document Explorer":

    st.markdown("""
    <div class="hero">
        <h1>📚 Document Explorer</h1>
        <p>Explore the agricultural government scheme knowledge base.</p>
    </div>
    """, unsafe_allow_html=True)

    documents = [
        "Tamilnadu_Agricultural_Farmerwelfare_Schemes.pdf",
        "Tamilnadu_Agricultural_Subsidy_Schemes.pdf"
    ]

    st.subheader("Available Documents")

    for i, document in enumerate(documents, 1):

        st.markdown(
            f"""
            <div class="source-card">
            <b>Document {i}</b><br>
            📄 {document}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.caption(
        "Document names are configured for this MVP. "
        "The actual indexed page and chunk counts will be added "
        "when the backend exposes indexing statistics."
    )


# --------------------------------------------------
# ANALYTICS
# --------------------------------------------------

elif page == "Analytics":

    st.markdown("""
    <div class="hero">
        <h1>📊 Application Analytics</h1>
        <p>Monitor question activity and document references during this session.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Questions",
            len(st.session_state.questions)
        )

    with col2:
        st.metric(
            "Answers Generated",
            len(st.session_state.answer_history)
        )

    with col3:
        st.metric(
            "Source References",
            len(st.session_state.sources_used)
        )

    st.divider()

    st.subheader("Most Referenced Documents")

    document_counts = Counter(
        source["filename"]
        for source in st.session_state.sources_used
    )

    if document_counts:

        st.bar_chart(
            dict(document_counts),
            horizontal=True
        )

    else:
        st.info("Ask questions to generate analytics.")

    st.subheader("Recent Question Activity")

    if st.session_state.answer_history:

        for item in reversed(st.session_state.answer_history[-10:]):

            with st.expander(item["question"]):

                st.write(item["answer"])

                st.caption(
                    f"Asked at {item['time']}"
                )

                for source in item["sources"]:
                    st.write(
                        f"📄 {source['filename']} — Page {source['page']}"
                    )

    else:
        st.info("No questions have been asked in this session yet.")


# --------------------------------------------------
# ABOUT
# --------------------------------------------------

elif page == "About":

    st.markdown("""
    <div class="hero">
        <h1>About AgriScheme Intelligence</h1>
        <p>Making agricultural government scheme information easier to explore.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Technology Stack")

    technologies = [
        ("Python", "Application programming"),
        ("LangChain", "Document processing and RAG"),
        ("FAISS", "Vector storage and similarity search"),
        ("Sentence Transformers", "Text embeddings"),
        ("Ollama + Qwen 2.5", "Local AI language model"),
        ("FastAPI", "Backend API"),
        ("Streamlit", "Interactive user interface")
    ]

    for technology, purpose in technologies:

        st.markdown(
            f"**{technology}** — {purpose}"
        )

    st.divider()

    st.success(
        "Answers are generated using retrieved document content. "
        "Always verify important scheme eligibility and benefit details "
        "against the original government documents."
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("""
<div class="footer">
    🌿 AGRISCHEME INTELLIGENCE PLATFORM<br>
    Built with Python • LangChain • FAISS • Ollama • Streamlit
</div>
""", unsafe_allow_html=True)
