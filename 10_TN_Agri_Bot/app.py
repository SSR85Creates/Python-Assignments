
import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph

# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Tamil Nadu Agriculture AI Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()


# --------------------------------------------------
# 2. PREMIUM UI DESIGN
# --------------------------------------------------

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #f4f7fb;
}

section[data-testid="stSidebar"] {
    background-color: #102e45;
}

section[data-testid="stSidebar"] * {
    color: #ffffff;
}

section[data-testid="stSidebar"] hr {
    border-color: #52758e;
}

/* Sidebar language dropdown */

section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background-color: #16364f !important;
    color: #ffffff !important;
    border: 1px solid #52758e !important;
    border-radius: 8px !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] input {
    color: #ffffff !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] svg {
    fill: #ffffff !important;
}

div[data-baseweb="popover"] {
    background-color: #16364f !important;
}

div[data-baseweb="popover"] ul {
    background-color: #16364f !important;
}

div[data-baseweb="popover"] li {
    background-color: #16364f !important;
    color: #ffffff !important;
}

div[data-baseweb="popover"] li:hover {
    background-color: #24516e !important;
}

/* Main heading */

.hero {
    background: linear-gradient(120deg, #102e45, #176b70);
    padding: 32px;
    border-radius: 16px;
    color: white;
    margin-bottom: 25px;
}

.hero h1 {
    color: white;
    font-size: 30px;
    font-weight: 800;
    margin-bottom: 8px;
}

.hero p {
    color: #dcebed;
    font-size: 15px;
}

/* Information cards */

.info-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #e4eaf0;
    min-height: 115px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.03);
}

.info-card h3 {
    color: #176b70;
    font-size: 17px;
    margin-bottom: 8px;
}

.info-card p {
    color: #526477;
    font-size: 13px;
}

/* Buttons */

.stButton > button {
    border-radius: 8px;
    border: 1px solid #176b70;
    color: #176b70;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #176b70;
    color: white;
}

/* Chat messages */

[data-testid="stChatMessage"] {
    background-color: white;
    border-radius: 12px;
    border: 1px solid #e7edf2;
    padding: 12px;
}

/* Footer */

.footer {
    text-align: center;
    color: #8795a3;
    font-size: 12px;
    padding: 25px;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# 3. INITIALIZE NEO4J AND OPENAI
# --------------------------------------------------

@st.cache_resource
def initialize_system():

    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
        database="06388906"
    )

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )

    openai_client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    return graph, llm, openai_client


# --------------------------------------------------
# 4. VOICE TRANSCRIPTION
# --------------------------------------------------

def transcribe_audio(audio_bytes, openai_client):

    transcription = openai_client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",
        file=(
            "question.wav",
            audio_bytes,
            "audio/wav"
        )
    )

    return transcription.text


# --------------------------------------------------
# 5. KNOWLEDGE GRAPH RETRIEVAL AND ANSWERING
# --------------------------------------------------

def get_answer(question, language, graph, llm):

    # Convert the user's question into useful English search terms.

    keyword_prompt = f"""
    You are helping search a database containing information
    about Tamil Nadu Government agricultural schemes.

    The user may ask in English, Tamil or Tanglish.

    Understand the question and generate 3 to 8 important
    English search keywords or short phrases.

    Return only comma-separated keywords.
    Do not provide an explanation.

    User question: {question}
    """

    keyword_response = llm.invoke(keyword_prompt)

    keywords = [
        word.strip().lower()
        for word in keyword_response.content.split(",")
        if word.strip()
    ]

    # Search the Knowledge Graph's source documents.

    query = """
    MATCH (d:Document)
    WHERE d.text IS NOT NULL
    AND any(term IN $terms WHERE toLower(d.text) CONTAINS term)
    RETURN DISTINCT d.text AS content
    LIMIT 8
    """

    results = graph.query(
        query,
        {"terms": keywords}
    )

    if not results:

        return (
            "The available government website information "
            "does not contain a matching answer. "
            "Please try another question.",
            0
        )

    context = "\n\n".join(
        item["content"]
        for item in results
        if item.get("content")
    )

    language_instruction = {
        "English": "Answer in clear English.",
        "Tamil": "Answer in natural Tamil using Tamil script.",
        "Tanglish": "Answer in conversational Tanglish using English letters."
    }

    answer_prompt = f"""
    You are the Tamil Nadu Government Agriculture Schemes AI Assistant.

    Answer the user's question using ONLY the website information
    supplied below.

    Rules:
    1. Do not invent scheme names, subsidies or amounts.
    2. Do not assume eligibility conditions.
    3. Do not invent application procedures.
    4. If the information is unavailable, clearly say so.
    5. Keep the answer clear and useful.
    6. Use bullet points wherever appropriate.

    LANGUAGE:
    {language_instruction[language]}

    GOVERNMENT WEBSITE INFORMATION:
    {context}

    USER QUESTION:
    {question}
    """

    response = llm.invoke(answer_prompt)

    return response.content, len(results)


# --------------------------------------------------
# 6. SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown("## 🌾 Agriculture AI")

    st.markdown("---")

    st.markdown("### Language Preference")

    language = st.selectbox(
        "Choose answer language",
        ["English", "Tamil", "Tanglish"],
        index=0
    )

    st.markdown("---")

    st.markdown("### About this Assistant")

    st.write(
        "An AI-powered assistant that helps users "
        "understand Tamil Nadu Government agricultural schemes."
    )

    st.markdown("---")

    st.markdown("### Technology Stack")

    st.write("• Python")
    st.write("• Streamlit")
    st.write("• OpenAI GPT")
    st.write("• LangChain")
    st.write("• Neo4j Knowledge Graph")
    st.write("• Retrieval-Augmented Generation")

    st.markdown("---")

    if st.button("Clear Conversation", use_container_width=True):

        st.session_state.messages = []
        st.session_state.pending_question = None
        st.rerun()


# --------------------------------------------------
# 7. INITIALIZE SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# --------------------------------------------------
# 8. MAIN SCREEN
# --------------------------------------------------

st.markdown("""
<div class="hero">
    <h1>தமிழ்நாடு விவசாய AI உதவியாளர்</h1>
    <h1>Tamil Nadu Agriculture AI Assistant</h1>
    <p>
        Your intelligent assistant for understanding
        Tamil Nadu Government agricultural schemes,
        subsidies and farmer benefits.
    </p>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# 9. INFORMATION CARDS
# --------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="info-card">
        <h3>🌱 Government Schemes</h3>
        <p>Explore agricultural schemes and government initiatives.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-card">
        <h3>💰 Subsidies</h3>
        <p>Understand available subsidies and financial assistance.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="info-card">
        <h3>👨‍🌾 Farmer Eligibility</h3>
        <p>Find eligibility conditions and application procedures.</p>
    </div>
    """, unsafe_allow_html=True)


st.markdown("### Ask your question")

st.caption(
    "You can type in English, Tamil or Tanglish, "
    "or use the microphone to record your question."
)


# --------------------------------------------------
# 10. SUGGESTED QUESTIONS
# --------------------------------------------------

st.markdown("**Suggested questions**")

suggestions = [
    "What is the subsidy under Production of Certified Seeds?",
    "Who is eligible for agricultural schemes?",
    "How can farmers apply for government subsidies?"
]

suggestion_columns = st.columns(3)

for index, suggestion in enumerate(suggestions):

    with suggestion_columns[index]:

        if st.button(
            suggestion,
            key=f"suggestion_{index}",
            use_container_width=True
        ):

            st.session_state.pending_question = suggestion
            st.rerun()


# --------------------------------------------------
# 11. DISPLAY CHAT HISTORY
# --------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant":

            st.caption(
                f"Source: Tamil Nadu Government Scheme Website | "
                f"Retrieved document chunks: {message.get('chunks', 0)}"
            )


# --------------------------------------------------
# 12. VOICE INPUT
# --------------------------------------------------

st.markdown("---")

st.markdown("### 🎙️ Ask using your voice")

audio_value = st.audio_input(
    "Record your question"
)

if audio_value is not None:

    if st.button("Transcribe voice question"):

        try:

            with st.spinner("Transcribing your question..."):

                _, _, openai_client = initialize_system()

                transcribed_text = transcribe_audio(
                    audio_value.getvalue(),
                    openai_client
                )

                if transcribed_text.strip():

                    st.session_state.pending_question = transcribed_text

                    st.rerun()

                else:
                    st.warning("No speech was detected. Please try again.")

        except Exception as e:

            st.error(f"Voice transcription error: {str(e)}")


# --------------------------------------------------
# 13. TEXT INPUT
# --------------------------------------------------

user_question = st.chat_input(
    "Type your question here..."
)

if user_question:

    st.session_state.pending_question = user_question


# --------------------------------------------------
# 14. PROCESS QUESTION
# --------------------------------------------------

if st.session_state.pending_question:

    question = st.session_state.pending_question

    st.session_state.pending_question = None

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    try:

        with st.spinner("Searching government scheme information..."):

            graph, llm, _ = initialize_system()

            answer, chunks = get_answer(
                question,
                language,
                graph,
                llm
            )

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "chunks": chunks
        })

    except Exception as e:

        error_message = f"Unable to process your question: {str(e)}"

        st.session_state.messages.append({
            "role": "assistant",
            "content": error_message,
            "chunks": 0
        })

    st.rerun()


# --------------------------------------------------
# 15. FOOTER
# --------------------------------------------------

st.markdown("""
<div class="footer">
    Tamil Nadu Agriculture AI Assistant |
    Knowledge Graph RAG Project |
    Developed as part of AI Implementation Learning
</div>
""", unsafe_allow_html=True)
