
import os
import hashlib
import tempfile

import streamlit as st
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS

from langchain_core.messages import SystemMessage, HumanMessage


# ==================================================
# 1. APPLICATION CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Manufacturing Quality RAG Assistant",
    page_icon="📚",
    layout="wide"
)

load_dotenv()

st.title("Manufacturing Quality Knowledge Assistant")

st.write(
    "Upload multiple manufacturing quality PDFs "
    "and ask questions across all documents."
)


# ==================================================
# 2. OPENAI API KEY CONFIGURATION
# ==================================================

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error(
        "OpenAI API key not found. "
        "Please configure it in your .env file."
    )
    st.stop()


# ==================================================
# 3. INITIALIZE SESSION STATE
# ==================================================

if "store" not in st.session_state:
    st.session_state.store = None

if "indexed_chunks" not in st.session_state:
    st.session_state.indexed_chunks = 0

if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = []

if "upload_hash" not in st.session_state:
    st.session_state.upload_hash = None


# ==================================================
# 4. MULTIPLE PDF UPLOAD
# ==================================================

st.header("1. Upload PDF Documents")

files = st.file_uploader(
    "Choose PDF documents",
    type=["pdf"],
    accept_multiple_files=True
)


# ==================================================
# 5. BUILD DOCUMENT FINGERPRINT
# ==================================================

current_hash = None

if files:

    file_hash = hashlib.sha256()

    for file in files:
        file_hash.update(file.name.encode("utf-8"))
        file_hash.update(file.getvalue())

    current_hash = file_hash.hexdigest()

    st.write(f"Uploaded documents: {len(files)}")

    for file in files:
        st.caption(f"📄 {file.name}")


# ==================================================
# 6. LOAD, CHUNK, EMBED AND INDEX DOCUMENTS
# ==================================================

if files:

    if st.button("Build FAISS Knowledge Base"):

        try:

            with st.spinner(
                "Processing PDFs and creating FAISS database..."
            ):

                all_documents = []

                # Load every uploaded PDF
                for file in files:

                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".pdf"
                    ) as temp_file:

                        temp_file.write(file.getvalue())
                        temp_path = temp_file.name

                    try:

                        loader = PyPDFLoader(temp_path)

                        documents = loader.load()

                        # Preserve original filename
                        for document in documents:
                            document.metadata["source"] = file.name

                        all_documents.extend(documents)

                    finally:

                        if os.path.exists(temp_path):
                            os.remove(temp_path)

                if not all_documents:
                    st.error("No PDF pages could be loaded.")
                    st.stop()

                # Split documents into smaller chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=150
                )

                chunks = text_splitter.split_documents(
                    all_documents
                )

                if not chunks:
                    st.error(
                        "No readable text found in the PDFs. "
                        "Check whether the documents are scanned."
                    )
                    st.stop()

                # Generate OpenAI embeddings
                embeddings = OpenAIEmbeddings(
                    model="text-embedding-3-small",
                    api_key=api_key
                )

                # Create ONE FAISS database
                vector_store = FAISS.from_documents(
                    documents=chunks,
                    embedding=embeddings
                )

                # Save FAISS database in Streamlit session state
                st.session_state.store = vector_store

                st.session_state.indexed_chunks = len(chunks)

                st.session_state.indexed_files = [
                    file.name for file in files
                ]

                st.session_state.upload_hash = current_hash

            st.success("FAISS knowledge base created successfully!")

        except Exception as e:

            st.error(f"Indexing error: {str(e)}")


# ==================================================
# 7. DISPLAY INDEXING INFORMATION
# ==================================================

if st.session_state.store is not None:

    st.header("2. Knowledge Base Status")

    col1, col2 = st.columns(2)

    col1.metric(
        "PDF Documents Indexed",
        len(st.session_state.indexed_files)
    )

    col2.metric(
        "Total Chunks Indexed",
        st.session_state.indexed_chunks
    )

    with st.expander("View Indexed Documents"):

        for filename in st.session_state.indexed_files:
            st.write(f"📄 {filename}")


# ==================================================
# 8. QUESTION AND ANSWER
# ==================================================

st.header("3. Ask Your Questions")

question = st.text_input(
    "Enter your question",
    placeholder=(
        "Example: What should happen when "
        "a measuring instrument is found out of tolerance?"
    )
)

if st.button("Get Answer"):

    if st.session_state.store is None:

        st.warning("Please build the FAISS knowledge base first.")

    elif not question.strip():

        st.warning("Please enter a question.")

    else:

        try:

            with st.spinner(
                "Searching documents and generating answer..."
            ):

                # Retrieve relevant chunks from FAISS
                retrieved_docs = (
                    st.session_state.store.similarity_search(
                        question,
                        k=6
                    )
                )

                if not retrieved_docs:
                    st.warning("No relevant information was retrieved.")
                    st.stop()

                # Prepare document context
                context_parts = []

                for doc in retrieved_docs:

                    filename = doc.metadata.get(
                        "source", "Unknown document"
                    )

                    # PyPDFLoader page metadata starts at zero
                    page_number = int(
                        doc.metadata.get("page", 0)
                    ) + 1

                    context_parts.append(
                        f"""
                        SOURCE: {filename}
                        PAGE: {page_number}

                        CONTENT:
                        {doc.page_content}
                        """
                    )

                context = "\n\n".join(context_parts)

                # Initialize OpenAI LLM
                llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    temperature=0,
                    api_key=api_key
                )

                # RELEVANCE CHECK

                relevance_messages = [
                    SystemMessage(
                        content="""
                        You are a document relevance validator.

                        Determine whether the retrieved context
                        contains meaningful information relevant
                        to the user's question.

                        Return ONLY one of these:
                        RELEVANT
                        NOT_RELEVANT

                        Do not use general knowledge.
                        Reject unrelated questions.
                        Reject questions unsupported by the context.
                        """
                    ),
                    HumanMessage(
                        content=f"""
                        USER QUESTION:
                        {question}

                        RETRIEVED CONTEXT:
                        {context}

                        Is the context relevant to answering
                        this question?
                        """
                    )
                ]

                relevance_response = llm.invoke(relevance_messages)

                relevance_result = (
                    relevance_response.content.strip().upper()
                )

                if relevance_result != "RELEVANT":

                    st.error(
                        "Your question is outside the scope of "
                        "the uploaded documents. Please ask a "
                        "manufacturing quality-related question "
                        "supported by the documents."
                    )

                    st.stop()

                # Prepare LLM instructions
                messages = [

                    SystemMessage(
                        content="""
                        You are a Manufacturing Quality
                        Knowledge Assistant.

                        Answer questions using only the
                        retrieved document context.

                        Follow these instructions:

                        1. Do not invent information.

                        2. If the documents do not contain
                           the answer, clearly say so.

                        3. If two documents provide conflicting
                           information, identify the disagreement
                           and explain what each document states.

                        4. Use simple and professional language.

                        5. Mention the document filename and
                           page number supporting your answer.

                        6. Do not present general knowledge
                           as information from the documents.

                        7. If the retrieved context is insufficient,
                           clearly mention the limitation.
                        """
                    ),

                    HumanMessage(
                        content=f"""
                        USER QUESTION:

                        {question}

                        RETRIEVED DOCUMENT CONTEXT:

                        {context}

                        Generate an answer based on this context.
                        """
                    )
                ]

                # Generate answer
                response = llm.invoke(messages)

            # Display answer
            st.subheader("AI Generated Answer")

            st.write(response.content)

            # Display source references
            st.subheader("Sources")

            seen_sources = set()

            for doc in retrieved_docs:

                filename = doc.metadata.get(
                    "source", "Unknown document"
                )

                page_number = int(
                    doc.metadata.get("page", 0)
                ) + 1

                source_key = (filename, page_number)

                if source_key not in seen_sources:

                    st.write(
                        f"📄 **{filename}** — Page {page_number}"
                    )

                    seen_sources.add(source_key)

        except Exception as e:

            st.error(f"Question answering error: {str(e)}")


# ==================================================
# END OF APPLICATION
# ==================================================
