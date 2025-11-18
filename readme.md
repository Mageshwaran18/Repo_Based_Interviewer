# AI-Powered GitHub Repository Interview System

## 📋 Overview

This project is an **automated technical interview system** that analyzes GitHub repositories and generates contextual interview questions based on the codebase. It leverages advanced AI techniques including **Retrieval-Augmented Generation (RAG)**, **hybrid search**, and **large language models (LLMs)** to conduct intelligent technical assessments.

The system downloads repository files, processes them into searchable chunks, stores them in a vector database, generates relevant technical questions, collects user responses, and evaluates answers with AI-powered scoring.

---

## ✨ Key Features

### 1. **Automated Repository Processing**
- Downloads files from any public GitHub repository
- Intelligently skips binary files (images, videos, archives, executables)
- Converts diverse file formats (`.py`, `.ipynb`, `.md`, `.json`, etc.) into unified text format
- Handles Jupyter notebooks with special cell extraction logic

### 2. **Intelligent Text Processing**
- Flattens and normalizes repository content
- Removes redundant whitespace and formatting inconsistencies
- Creates single-line representations for efficient processing

### 3. **Hybrid Search Architecture**
- **Dense embeddings** using `sentence-transformers/all-MiniLM-L6-v2`
- **Sparse retrieval** using BM25 algorithm for keyword matching
- Combined approach ensures both semantic and keyword-based relevance

### 4. **Context-Aware Question Generation**
- Generates technical interview questions specific to the repository
- Questions focus on design decisions, architecture choices, and implementation details
- Avoids generic or fundamental questions

### 5. **Interactive Interview Workflow**
- Presents questions sequentially to the user
- Collects and stores responses in structured JSON format

### 6. **AI-Powered Answer Evaluation**
- Evaluates user responses using LLM reasoning
- Provides marks out of 5 with detailed justifications
- Generates comprehensive evaluation reports

---

## 🛠️ Components & Technologies

### **Models**

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Embedding Model** | `all-MiniLM-L6-v2` | Converts text into 384-dimensional dense vectors for semantic search |
| **Sparse Encoder** | BM25 | Term-based retrieval for keyword matching |
| **LLM** | Llama 3.3 70B (via Groq) | Question generation and answer evaluation |

### **Databases & Storage**

- **Pinecone**: Serverless vector database for hybrid search (AWS `us-east-1` region)
- **Local JSON Files**: Stores questions, evaluations, and results

### **Core Libraries**

```python
# Data Processing
numpy, pandas

# NLP & Embeddings
langchain, langchain-huggingface, langchain-groq
sentence-transformers, pinecone-text

# Document Processing
PyPDF2, python-docx, nbformat, beautifulsoup4

# Vector Database
pinecone-client

# API Integration
requests, python-dotenv
```

### **Methods & Strategies**

#### **Text Chunking Strategy**
- **Chunk Size**: 400 characters
- **Overlap**: 50 characters
- **Separators**: Prioritizes natural boundaries (`\n\n`, `.`, `!`, `?`)
- **Rationale**: Balances context preservation with retrieval precision

#### **Hybrid Search Strategy**
```python
# Combines two retrieval methods:
1. Dense Vector Search (semantic similarity)
2. Sparse BM25 Search (keyword matching)

# Uses dotproduct metric for efficient similarity computation
```

#### **Quality Filtering**
- Validates sparse vector generation before upload
- Removes chunks with empty BM25 representations
- Ensures only meaningful content enters the index

---

## 🔄 Workflow

### **Simple Overview**

1. **Download** → Fetch repository files from GitHub
2. **Process** → Convert all files to text format
3. **Index** → Store in vector database with hybrid search
4. **Generate** → Create interview questions using AI
5. **Interview** → Ask questions and collect answers
6. **Evaluate** → Score responses with LLM reasoning

---

### **Detailed Workflow**

#### **Phase 1: Repository Acquisition**
```
GitHub URL → API Request → File Tree Traversal
    ↓
Filter Extensions → Download Valid Files → Save Locally
```

**Output**: `data/repo_files/` directory with filtered codebase

---

#### **Phase 2: Content Transformation**

```
Multiple File Formats (.py, .ipynb, .md, etc.)
    ↓
Parse & Extract Text Content
    ↓
Combine into Single Document
    ↓
Flatten & Normalize Text
    ↓
Convert to Single-Line String
```

**Output**: `data/combined_repo.txt`, `data/flattened_repo.txt`

---

#### **Phase 3: Vector Database Initialization**

```
Text String → RecursiveCharacterTextSplitter
    ↓
Generate 400-char Chunks (50-char overlap)
    ↓
Parallel Processing:
    ├─ Dense Embeddings (384-dim vectors)
    └─ Sparse BM25 Encoding
    ↓
Validate Sparse Vectors → Filter Empty Chunks
    ↓
Upload to Pinecone Index
```

**Output**: Indexed repository in Pinecone (`rbi` index)

---

#### **Phase 4: Question Generation (RAG Pipeline)**

```
User Query: "Generate interview questions"
    ↓
Pinecone Hybrid Retriever
    ├─ Semantic Search (embeddings)
    └─ Keyword Search (BM25)
    ↓
Retrieve Top-K Relevant Chunks
    ↓
Construct Prompt with Context
    ↓
LLM Generation (Llama 3.3 70B)
    ↓
Parse JSON Output
```

**Output**: `data/questions.json` with structured questions

**Prompt Engineering**:
- Enforces specific question types (architecture, design decisions, trade-offs)
- Restricts to 3 questions
- Requires strict JSON format with validation rules

---

#### **Phase 5: Interactive Interview**

```
Load questions.json
    ↓
For each question:
    Display → Collect Input → Store Response
    ↓
Compile all Q&A pairs
    ↓
Save to evaluation.json
```

**Output**: `data/evaluation.json` with user responses

---

#### **Phase 6: AI-Powered Evaluation**

```
Load evaluation.json
    ↓
For each Q&A pair:
    Construct Evaluation Prompt
    ↓
    LLM Analysis (Llama 3.3 70B)
    ↓
    Extract Marks (0-5) + Justification
    ↓
Aggregate Results
    ↓
Save final_output.json
```

**Evaluation Criteria**:
- Correctness and depth of answer
- Relevance to the question
- Technical accuracy
- Completeness of explanation

**Output**: `data/final_output.json` with scores and feedback

---

## 📂 Data Flow Architecture

```
GitHub Repo
    ↓
[Download Layer] → repo_files/
    ↓
[Processing Layer] → combined_repo.txt → flattened_repo.txt
    ↓
[Indexing Layer] → Pinecone Vector DB + BM25 Index
    ↓
[Generation Layer] → questions.json (RAG-based)
    ↓
[Interview Layer] → evaluation.json (User I/O)
    ↓
[Evaluation Layer] → final_output.json (LLM Scoring)
```

---

## 🚀 Getting Started

### Prerequisites
```bash
# Required API Keys
PINECONE_API_KEY=<your_pinecone_key>
GROQ_API_KEY=<your_groq_key>
```

### Installation
```bash
pip install -r requirements.txt
```

### Usage
```python
# 1. Download repository
download_github_repo("https://github.com/user/repo")

# 2. Process files
convert_repo_to_text()
flatten_single_file()

# 3. Index in Pinecone
retriever = await store_terms_to_pinecone()

# 4. Generate questions
rag_chain.invoke("Generate interview questions")

# 5. Conduct interview
conduct_interview_and_save()

# 6. Evaluate responses
evaluate_answers_with_llm()
```

---

## 📊 Output Format

### Questions JSON
```json
{
  "interview_questions": [
    {
      "question_number": 1,
      "question": "Why did you choose XGBoost for this project?"
    }
  ]
}
```

### Evaluation JSON
```json
{
  "final_evaluation": [
    {
      "question_number": 1,
      "question": "Why did you choose XGBoost for this project?",
      "user_answer": "...",
      "marks": 4,
      "justification": "Answer demonstrates understanding..."
    }
  ]
}
```

---

## 🎯 Use Cases

- **Technical Screening**: Automate initial candidate assessments
- **Code Review Training**: Generate discussion points for code reviews
- **Knowledge Testing**: Validate understanding of existing codebases
- **Documentation**: Create FAQs based on repository analysis
- **Onboarding**: Test new team members' comprehension of projects

---

## 🔐 Security Notes

- Only processes public GitHub repositories
- No authentication credentials are stored
- API keys managed via environment variables
- Rate limits respected for GitHub API calls

---

## 📝 License

This project is intended for educational and assessment purposes.

---

## 🤝 Contributing

This is a demonstration project showcasing RAG architecture for technical assessments. Feel free to adapt and extend for your specific use cases.

---

**Built with ❤️ using LangChain, Pinecone, and Groq**

---