import streamlit as st
import os
import re
import requests
import time
import json
from pathlib import Path
import nbformat
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.retrievers import PineconeHybridSearchRetriever
from pinecone_text.sparse import BM25Encoder
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()

# Constants
BM25_PATH = "bm25_encoder.json"
INDEX_NAME = "rbi-interview"
SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp",
    ".ico", ".tiff", ".tif", ".mp3", ".mp4", ".wav", ".avi",
    ".mov", ".zip", ".tar", ".gz", ".rar", ".7z", ".pdf",
    ".exe", ".dll", ".so", ".csv", ".tsv"
}
TEXT_EXTENSIONS = {".txt", ".py", ".md", ".json", ".yaml", ".yml", ".html", ".js", ".jsx", ".ts", ".tsx"}

# Set page config
st.set_page_config(page_title="GitHub Repo Interview Bot", page_icon="💼", layout="wide")

# Initialize session state
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'retriever' not in st.session_state:
    st.session_state.retriever = None
if 'interview_started' not in st.session_state:
    st.session_state.interview_started = False
if 'processing' not in st.session_state:
    st.session_state.processing = False

def download_github_repo(repo_url, save_dir="data/repo_files"):
    """Download GitHub repository files"""
    repo_url = repo_url.replace(".git", "")
    match = re.match(r"https://github.com/([^/]+)/([^/]+)", repo_url)
    
    if not match:
        raise ValueError("Invalid GitHub URL")
    
    user, repo = match.groups()
    api_url = f"https://api.github.com/repos/{user}/{repo}/contents"
    
    os.makedirs(save_dir, exist_ok=True)
    
    def download_recursive(api_path, local_path):
        response = requests.get(api_path)
        data = response.json()
        
        if isinstance(data, dict) and "message" in data:
            st.error(f"GitHub API Error: {data['message']}")
            return
        
        for item in data:
            name = item["name"]
            file_path = os.path.join(local_path, name)
            
            if name.lower() in ["node_modules", ".git", "__pycache__"]:
                continue
            
            if item["type"] == "dir":
                os.makedirs(file_path, exist_ok=True)
                download_recursive(item["url"], file_path)
            
            elif item["type"] == "file":
                ext = os.path.splitext(name)[1].lower()
                if ext in SKIP_EXTENSIONS:
                    continue
                
                file_data = requests.get(item["download_url"]).content
                with open(file_path, "wb") as f:
                    f.write(file_data)
    
    download_recursive(api_url, save_dir)
    return True

def convert_repo_to_text(input_dir="data/repo_files", output_file="data/combined_repo.txt"):
    """Convert repository files to combined text"""
    all_texts = []
    
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            
            try:
                if ext in TEXT_EXTENSIONS:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        all_texts.append(f"\n\n===== FILE: {file} =====\n\n{content}")
                
                elif ext == ".ipynb":
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        nb = nbformat.read(f, as_version=4)
                        cells_text = []
                        for cell in nb.cells:
                            if cell.cell_type in ["code", "markdown"]:
                                cells_text.append(cell.source)
                        all_texts.append(f"\n\n===== FILE: {file} =====\n\n" + "\n\n".join(cells_text))
            
            except Exception as e:
                continue
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_texts))
    
    return output_file

def flatten_text(input_file, output_file="data/flattened_repo.txt"):
    """Flatten text by removing extra whitespace"""
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()
    
    flat_text = re.sub(r"\n+", "\n", text)
    flat_text = re.sub(r"[ \t]+", " ", flat_text)
    flat_text = flat_text.strip()
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as out:
        out.write(flat_text)
    
    return output_file

def convert_to_single_line(input_file="data/flattened_repo.txt"):
    """Convert text to single line"""
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()
    
    single_line = " ".join(text.split())
    return single_line

def initialize_pinecone():
    """Initialize Pinecone index"""
    api_key = os.getenv("PINECONE_API_KEY")
    pc = Pinecone(api_key=api_key)
    existing = [i.name for i in pc.list_indexes()]
    
    if INDEX_NAME in existing:
        pc.delete_index(INDEX_NAME)
        time.sleep(5)
    
    pc.create_index(
        name=INDEX_NAME,
        dimension=384,
        metric='dotproduct',
        spec=ServerlessSpec(cloud='aws', region='us-east-1')
    )
    time.sleep(30)
    
    return pc.Index(INDEX_NAME)

def process_repository(repo_url):
    """Process repository and create retriever"""
    try:
        # Download repo
        st.info("📥 Downloading repository...")
        download_github_repo(repo_url)
        
        # Convert to text
        st.info("📄 Converting files to text...")
        combined_file = convert_repo_to_text()
        
        # Flatten text
        st.info("🔄 Processing text...")
        flattened_file = flatten_text(combined_file)
        combined_text = convert_to_single_line(flattened_file)
        
        # Split into chunks
        st.info("✂️ Splitting into chunks...")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        chunks = splitter.split_text(combined_text)
        
        # Initialize Pinecone
        st.info("🗄️ Setting up vector database...")
        index = initialize_pinecone()
        
        # Setup embeddings and BM25
        st.info("🧠 Creating embeddings...")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        
        bm25 = BM25Encoder().default()
        bm25.fit(chunks)
        bm25.dump(BM25_PATH)
        
        # Create retriever
        retriever = PineconeHybridSearchRetriever(
            embeddings=embeddings,
            sparse_encoder=bm25,
            index=index
        )
        
        st.info("⬆️ Uploading to vector database...")
        retriever.add_texts(chunks)
        
        return retriever, len(chunks)
    
    except Exception as e:
        st.error(f"Error processing repository: {str(e)}")
        return None, 0

def generate_questions(retriever):
    """Generate interview questions using LLM"""
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=1024,
            groq_api_key=groq_api_key
        )
        
        prompt = ChatPromptTemplate.from_template("""
You are a senior software engineer conducting an interview. 
Use the context below (project code and documentation) to generate interview questions.

Context:
{context}

Instructions:
- Generate 10 meaningful technical questions about the project
- Questions must be specific to the code, design, architecture, or data structures
- Ask questions like:
    - Why did you choose this data structure or algorithm?
    - Why this design pattern or component was used?
    - Explain the purpose of a specific function/module
    - Trade-offs or alternatives in the code
- Make the questions suitable for a real-world technical interview
- Number the questions from 1 to 10
- Only use information present in the context

Output format:
1. Question 1
2. Question 2
...
10. Question 10
""")
        
        rag_chain = (
            {
                "context": retriever,
                "question": RunnablePassthrough()
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        
        answer = rag_chain.invoke("Generate interview questions based on this project.")
        
        # Parse questions
        questions = []
        lines = answer.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Remove numbering
                question = re.sub(r'^\d+[\.)]\s*', '', line)
                question = re.sub(r'^[-•]\s*', '', question)
                if question:
                    questions.append(question)
        
        return questions
    
    except Exception as e:
        st.error(f"Error generating questions: {str(e)}")
        return []

# UI Layout
st.title("💼 GitHub Repository Technical Interview Bot")
st.markdown("---")

# Sidebar for repo input
with st.sidebar:
    st.header("Repository Setup")
    repo_url = st.text_input(
        "Enter GitHub Repository URL:",
        placeholder="https://github.com/username/repo",
        help="Enter the full GitHub repository URL"
    )
    
    if st.button("🚀 Start Interview Process", type="primary", disabled=st.session_state.processing):
        if repo_url:
            st.session_state.processing = True
            st.session_state.interview_started = False
            st.session_state.current_question = 0
            st.session_state.answers = {}
            
            with st.spinner("Processing repository..."):
                retriever, chunk_count = process_repository(repo_url)
                
                if retriever:
                    st.session_state.retriever = retriever
                    st.success(f"✅ Processed {chunk_count} chunks!")
                    
                    with st.spinner("Generating interview questions..."):
                        questions = generate_questions(retriever)
                        
                        if questions:
                            st.session_state.questions = questions
                            st.session_state.interview_started = True
                            st.success(f"✅ Generated {len(questions)} questions!")
                        else:
                            st.error("Failed to generate questions")
            
            st.session_state.processing = False
        else:
            st.warning("Please enter a GitHub repository URL")
    
    st.markdown("---")
    st.markdown("### Instructions")
    st.markdown("""
    1. Enter a GitHub repository URL
    2. Click 'Start Interview Process'
    3. Answer questions one by one
    4. Review your answers at the end
    """)

# Main content area
if st.session_state.interview_started and st.session_state.questions:
    total_questions = len(st.session_state.questions)
    current = st.session_state.current_question
    
    # Progress bar
    progress = (current) / total_questions
    st.progress(progress)
    st.markdown(f"**Question {current + 1} of {total_questions}**")
    
    # Display current question
    if current < total_questions:
        st.markdown("---")
        st.markdown(f"### 📝 {st.session_state.questions[current]}")
        
        # Answer input
        answer = st.text_area(
            "Your Answer:",
            height=200,
            key=f"answer_{current}",
            value=st.session_state.answers.get(current, "")
        )
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if current > 0:
                if st.button("⬅️ Previous"):
                    st.session_state.answers[current] = answer
                    st.session_state.current_question -= 1
                    st.rerun()
        
        with col2:
            if current < total_questions - 1:
                if st.button("Next ➡️", type="primary"):
                    st.session_state.answers[current] = answer
                    st.session_state.current_question += 1
                    st.rerun()
            else:
                if st.button("✅ Finish Interview", type="primary"):
                    st.session_state.answers[current] = answer
                    st.session_state.current_question += 1
                    st.rerun()
        
        with col3:
            if st.button("💾 Save Progress"):
                st.session_state.answers[current] = answer
                st.success("Progress saved!")
    
    else:
        # Interview complete
        st.markdown("---")
        st.success("🎉 Interview Complete!")
        st.markdown("### Your Answers:")
        
        for i, question in enumerate(st.session_state.questions):
            with st.expander(f"Question {i + 1}: {question[:100]}..."):
                st.markdown(f"**Q:** {question}")
                st.markdown(f"**A:** {st.session_state.answers.get(i, 'No answer provided')}")
        
        if st.button("🔄 Start New Interview"):
            st.session_state.questions = []
            st.session_state.current_question = 0
            st.session_state.answers = {}
            st.session_state.interview_started = False
            st.rerun()

else:
    # Welcome screen
    st.markdown("""
    ## Welcome to the GitHub Repository Interview Bot! 👋
    
    This application helps you prepare for technical interviews by:
    
    - 📥 **Analyzing your GitHub repository**
    - 🤖 **Generating relevant technical questions**
    - 💬 **Conducting an interactive interview**
    - 📊 **Reviewing your answers**
    
    ### How it works:
    
    1. Enter a GitHub repository URL in the sidebar
    2. Click "Start Interview Process" to analyze the code
    3. Answer the generated questions one by one
    4. Review your complete interview at the end
                
    **Ready to start? Enter a repository URL in the sidebar! 🚀**
    """)
    
    # Example repositories
    st.markdown("---")
    st.markdown("### 💡 Try these example repositories:")
    st.code("https://github.com/Mageshwaran18/Music_Popularity_Prediction")
    