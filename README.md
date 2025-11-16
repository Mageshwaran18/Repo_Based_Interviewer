# Repo_Based_Interviewer

A RAG (Retrieval-Augmented Generation) based intelligent interviewer system that analyzes GitHub repositories and conducts interactive technical interviews based on the repository content.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Example Workflow](#example-workflow)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

**Repo_Based_Interviewer** is an AI-powered system designed to conduct technical interviews based on the content of GitHub repositories. By leveraging RAG (Retrieval-Augmented Generation) technology, the system can:

- **Analyze** any public GitHub repository
- **Generate** relevant technical questions based on the codebase
- **Evaluate** user responses to assess technical understanding
- **Provide** feedback on answers with context from the repository

This tool is ideal for:
- Technical recruiters conducting code-based interviews
- Developers wanting to test their understanding of a codebase
- Educational institutions for assessment purposes
- Teams onboarding new developers

## ✨ Features

### Core Capabilities

- **Repository Analysis**: Automatically clones and analyzes GitHub repositories
- **Intelligent Question Generation**: Creates context-aware questions from:
  - Code structure and patterns
  - Documentation and comments
  - Dependencies and configurations
  - Architecture and design patterns
  
- **Multi-Level Questioning**: Generates questions at various difficulty levels:
  - Basic: Understanding of repository structure and purpose
  - Intermediate: Code implementation details
  - Advanced: Architecture decisions and optimization strategies

- **Answer Evaluation**: Uses RAG to:
  - Compare user answers against repository context
  - Provide detailed feedback
  - Score responses based on accuracy and completeness

- **Interactive Interview Sessions**: 
  - Real-time question-answer flow
  - Follow-up questions based on responses
  - Progress tracking throughout the interview

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface                           │
│              (CLI / Web Interface)                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Input Handler                              │
│         (GitHub URL Parser & Validator)                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Repository Processor                           │
│    ┌──────────────────┐    ┌──────────────────┐           │
│    │  Repo Cloner     │    │  Code Parser     │           │
│    └──────────────────┘    └──────────────────┘           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 RAG System Core                             │
│    ┌──────────────────┐    ┌──────────────────┐           │
│    │ Vector Database  │    │  Embeddings      │           │
│    │   (ChromaDB/     │◄───│  Generator       │           │
│    │    Pinecone)     │    │  (OpenAI/HF)     │           │
│    └──────────────────┘    └──────────────────┘           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          Question Generation Engine                         │
│    ┌──────────────────┐    ┌──────────────────┐           │
│    │ Context Retrieval│    │  LLM Integration │           │
│    │                  │───►│  (GPT-4/Claude)  │           │
│    └──────────────────┘    └──────────────────┘           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│            Answer Evaluation System                         │
│    ┌──────────────────┐    ┌──────────────────┐           │
│    │ Semantic Matcher │    │  Scoring Engine  │           │
│    └──────────────────┘    └──────────────────┘           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Results & Feedback                             │
│         (Report Generation & Analytics)                     │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Git
- API keys for LLM service (OpenAI, Anthropic, or Hugging Face)
- Sufficient disk space for cloning repositories

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Mageshwaran18/Repo_Based_Interviewer.git
   cd Repo_Based_Interviewer
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

5. **Initialize the vector database**
   ```bash
   python setup.py init-db
   ```

## 💻 Usage

### Basic Command Line Interface

```bash
# Start an interview session with a GitHub repository
python main.py --repo https://github.com/user/repository

# Specify question difficulty level
python main.py --repo https://github.com/user/repository --level intermediate

# Set number of questions
python main.py --repo https://github.com/user/repository --questions 10

# Generate a detailed report
python main.py --repo https://github.com/user/repository --report output.pdf
```

### Interactive Python API

```python
from repo_interviewer import RepoInterviewer

# Initialize the interviewer
interviewer = RepoInterviewer(
    repo_url="https://github.com/user/repository",
    api_key="your-api-key"
)

# Analyze the repository
interviewer.analyze_repository()

# Start interview session
session = interviewer.start_interview(
    num_questions=5,
    difficulty="intermediate"
)

# Get a question
question = session.get_next_question()
print(f"Q: {question.text}")

# Submit an answer
user_answer = input("Your answer: ")
evaluation = session.evaluate_answer(user_answer)

print(f"Score: {evaluation.score}/10")
print(f"Feedback: {evaluation.feedback}")

# Complete the interview
report = session.generate_report()
report.save("interview_report.pdf")
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# LLM Configuration
LLM_PROVIDER=openai  # options: openai, anthropic, huggingface
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
HUGGINGFACE_API_KEY=your_hf_api_key

# Vector Database
VECTOR_DB=chromadb  # options: chromadb, pinecone, faiss
CHROMADB_PATH=./data/chromadb
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=us-west1-gcp

# Repository Settings
TEMP_REPO_PATH=./temp/repos
MAX_REPO_SIZE_MB=500
ALLOWED_LANGUAGES=python,javascript,java,go,rust,typescript

# Question Generation
DEFAULT_NUM_QUESTIONS=5
MIN_DIFFICULTY=1
MAX_DIFFICULTY=10
QUESTION_TYPES=code_understanding,architecture,debugging,best_practices

# Evaluation
SIMILARITY_THRESHOLD=0.7
SCORING_METHOD=semantic  # options: semantic, keyword, hybrid

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/interviewer.log
```

### Configuration File

Alternatively, use `config.yaml`:

```yaml
llm:
  provider: openai
  model: gpt-4
  temperature: 0.7
  max_tokens: 2000

vector_db:
  type: chromadb
  persist_directory: ./data/chromadb
  collection_name: repo_embeddings

repository:
  temp_path: ./temp/repos
  max_size_mb: 500
  clone_depth: 1
  ignored_paths:
    - node_modules
    - venv
    - .git
    - __pycache__

interview:
  default_questions: 5
  difficulty_levels:
    - basic
    - intermediate
    - advanced
  question_categories:
    - code_structure
    - implementation_details
    - design_patterns
    - best_practices
    - debugging

evaluation:
  scoring:
    semantic_weight: 0.6
    keyword_weight: 0.4
  thresholds:
    excellent: 0.9
    good: 0.7
    satisfactory: 0.5
```

## 🔍 How It Works

### 1. Repository Analysis Phase

When you provide a GitHub repository URL, the system:

1. **Clones the repository** to a temporary local directory
2. **Scans the codebase** to identify:
   - Programming languages used
   - Project structure and organization
   - Key files (README, configuration, main source files)
   - Dependencies and external libraries
3. **Parses code files** to extract:
   - Function and class definitions
   - Comments and docstrings
   - Import statements and dependencies
   - Code patterns and conventions

### 2. Embedding Generation

The system processes the repository content:

1. **Chunks the content** into meaningful segments:
   - Individual functions/methods
   - Classes and modules
   - Documentation sections
   - Configuration files

2. **Generates embeddings** using the configured LLM:
   - Converts text to vector representations
   - Stores embeddings in the vector database
   - Indexes for efficient retrieval

### 3. Question Generation

Based on the analyzed repository:

1. **Retrieves relevant context** from the vector database
2. **Generates questions** using the LLM:
   - Formulates questions about code functionality
   - Creates scenario-based questions
   - Asks about design decisions and patterns
3. **Categorizes questions** by difficulty and type

### 4. Interview Execution

During the interview:

1. **Presents questions** one at a time
2. **Captures user responses**
3. **Allows time for thoughtful answers**
4. **Supports follow-up questions** based on responses

### 5. Answer Evaluation

For each answer:

1. **Retrieves relevant context** from the repository
2. **Compares answer** with expected knowledge:
   - Semantic similarity matching
   - Keyword extraction and matching
   - Contextual relevance scoring
3. **Generates detailed feedback**:
   - What was correct
   - What was missing
   - Additional insights from the codebase

### 6. Report Generation

After the interview:

1. **Compiles results** from all questions
2. **Calculates overall score**
3. **Generates insights**:
   - Strengths demonstrated
   - Areas for improvement
   - Repository comprehension level
4. **Exports report** in various formats (PDF, JSON, HTML)

## 📁 Project Structure

```
Repo_Based_Interviewer/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Entry point
│   ├── cli.py                     # Command-line interface
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py            # Configuration management
│   │   └── config.yaml            # Default configuration
│   ├── repository/
│   │   ├── __init__.py
│   │   ├── cloner.py              # Repository cloning logic
│   │   ├── parser.py              # Code parsing utilities
│   │   └── analyzer.py            # Repository analysis
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── embeddings.py          # Embedding generation
│   │   ├── vector_store.py        # Vector database interface
│   │   └── retriever.py           # Context retrieval
│   ├── question/
│   │   ├── __init__.py
│   │   ├── generator.py           # Question generation
│   │   ├── categorizer.py         # Question categorization
│   │   └── templates.py           # Question templates
│   ├── interview/
│   │   ├── __init__.py
│   │   ├── session.py             # Interview session management
│   │   ├── evaluator.py           # Answer evaluation
│   │   └── scorer.py              # Scoring logic
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── base.py                # Base LLM interface
│   │   ├── openai_client.py      # OpenAI integration
│   │   ├── anthropic_client.py   # Anthropic integration
│   │   └── huggingface_client.py # Hugging Face integration
│   ├── report/
│   │   ├── __init__.py
│   │   ├── generator.py           # Report generation
│   │   └── templates/             # Report templates
│   │       ├── pdf_template.html
│   │       └── html_template.html
│   └── utils/
│       ├── __init__.py
│       ├── logger.py              # Logging utilities
│       ├── validators.py          # Input validation
│       └── helpers.py             # Helper functions
├── tests/
│   ├── __init__.py
│   ├── test_repository.py
│   ├── test_rag.py
│   ├── test_questions.py
│   ├── test_interview.py
│   └── test_integration.py
├── data/
│   ├── chromadb/                  # Vector database storage
│   └── cache/                     # Cached embeddings
├── temp/
│   └── repos/                     # Temporary repository clones
├── logs/
│   └── interviewer.log            # Application logs
├── examples/
│   ├── basic_usage.py
│   ├── advanced_usage.py
│   └── custom_questions.py
├── docs/
│   ├── architecture.md
│   ├── api_reference.md
│   ├── deployment.md
│   └── troubleshooting.md
├── .env.example                   # Example environment variables
├── .gitignore
├── requirements.txt               # Python dependencies
├── setup.py                       # Package setup
├── pyproject.toml                 # Project metadata
├── README.md                      # This file
└── LICENSE
```

## 🛠️ Technologies Used

### Core Technologies

- **Python 3.8+**: Primary programming language
- **LangChain**: Framework for LLM application development
- **OpenAI API / Anthropic / Hugging Face**: Large Language Models for question generation and evaluation

### RAG Components

- **ChromaDB / Pinecone / FAISS**: Vector database for embeddings storage
- **Sentence Transformers**: Generate semantic embeddings
- **tiktoken**: Token counting and text chunking

### Repository Analysis

- **GitPython**: Git repository interaction
- **tree-sitter**: Code parsing for multiple languages
- **pygments**: Syntax highlighting and language detection

### Additional Libraries

- **python-dotenv**: Environment variable management
- **pydantic**: Data validation and settings management
- **rich**: Enhanced terminal output
- **typer**: CLI framework
- **pytest**: Testing framework
- **reportlab / weasyprint**: PDF report generation

## 📝 Example Workflow

### Example 1: Basic Interview

```bash
# Start a basic interview
$ python main.py --repo https://github.com/pallets/flask

Analyzing repository: flask...
✓ Repository cloned successfully
✓ Found 152 Python files
✓ Generated embeddings for 1,234 code chunks
✓ Ready to start interview

Starting interview session...

Question 1/5 [Difficulty: Intermediate]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
What is the primary purpose of the Flask class in the main 
application module, and what design pattern does it implement?

Your answer: [User provides answer]

Evaluation:
Score: 8/10
✓ Correctly identified Flask as the main application class
✓ Mentioned WSGI application pattern
✗ Could have mentioned the factory pattern usage
✓ Good understanding of core concepts

Feedback: Your answer demonstrates solid understanding of Flask's 
architecture. The Flask class indeed serves as the central WSGI 
application. Consider exploring the application factory pattern 
used in larger Flask applications for improved modularity.

[Continue with remaining questions...]

Interview Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Score: 42/50 (84%)

Strengths:
✓ Strong understanding of core concepts
✓ Good grasp of Flask's routing mechanism
✓ Understood decorator patterns

Areas for Improvement:
• Advanced configuration management
• Testing strategies
• Application factory pattern

Report saved to: interview_report_flask_20241116.pdf
```

### Example 2: Programmatic Usage

```python
from repo_interviewer import RepoInterviewer

# Initialize with custom settings
interviewer = RepoInterviewer(
    repo_url="https://github.com/django/django",
    config={
        "llm_provider": "openai",
        "model": "gpt-4",
        "num_questions": 10,
        "difficulty_range": (5, 8),  # Medium to Hard
        "focus_areas": ["orm", "views", "middleware"]
    }
)

# Analyze repository
analysis = interviewer.analyze_repository()
print(f"Detected languages: {analysis.languages}")
print(f"Total files: {analysis.file_count}")
print(f"Lines of code: {analysis.loc}")

# Generate custom questions
questions = interviewer.generate_questions(
    topics=["database", "authentication"],
    num_per_topic=3
)

# Start interview
session = interviewer.start_interview(questions=questions)

for i, question in enumerate(session.questions, 1):
    print(f"\n--- Question {i} ---")
    print(question.text)
    
    # Get user answer (could be from UI, API, etc.)
    user_answer = get_user_input()
    
    # Evaluate answer
    result = session.evaluate_answer(question.id, user_answer)
    
    print(f"Score: {result.score}")
    print(f"Feedback: {result.feedback}")
    
    # Ask follow-up if needed
    if result.score < 7 and question.has_followup:
        followup = session.generate_followup(question.id, user_answer)
        print(f"Follow-up: {followup.text}")

# Generate comprehensive report
report = session.generate_report(
    include_answers=True,
    include_code_references=True,
    format="pdf"
)

report.save("django_interview_detailed.pdf")
```

## 🤝 Contributing

We welcome contributions to the Repo_Based_Interviewer project! Here's how you can help:

### Ways to Contribute

1. **Report Bugs**: Open an issue describing the bug and how to reproduce it
2. **Suggest Features**: Share ideas for new features or improvements
3. **Submit Pull Requests**: Fix bugs or implement new features
4. **Improve Documentation**: Help us make the docs clearer and more comprehensive
5. **Share Feedback**: Let us know how you're using the tool

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/your-username/Repo_Based_Interviewer.git
cd Repo_Based_Interviewer

# Create a development branch
git checkout -b feature/your-feature-name

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run linting
flake8 src/
black src/ --check
mypy src/

# Make your changes and commit
git add .
git commit -m "Description of changes"

# Push and create a pull request
git push origin feature/your-feature-name
```

### Code Standards

- Follow PEP 8 style guidelines
- Write comprehensive docstrings
- Add unit tests for new features
- Maintain backward compatibility
- Update documentation as needed

### Pull Request Process

1. Ensure all tests pass
2. Update the README if needed
3. Add your changes to CHANGELOG.md
4. Request review from maintainers
5. Address review feedback

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://www.langchain.com/) framework
- Vector database powered by [ChromaDB](https://www.trychroma.com/)
- LLM services from [OpenAI](https://openai.com/), [Anthropic](https://www.anthropic.com/), and [Hugging Face](https://huggingface.co/)
- Inspired by the need for better technical assessment tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Mageshwaran18/Repo_Based_Interviewer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Mageshwaran18/Repo_Based_Interviewer/discussions)
- **Email**: [support@repo-interviewer.dev](mailto:support@repo-interviewer.dev)

## 🗺️ Roadmap

### Current Version (v1.0)
- ✅ Basic repository analysis
- ✅ Question generation from code
- ✅ Answer evaluation
- ✅ Report generation

### Upcoming Features (v1.1)
- [ ] Support for private repositories
- [ ] Multi-language support (beyond English)
- [ ] Video interview mode with speech-to-text
- [ ] Integration with popular ATS systems
- [ ] Team collaboration features

### Future Plans (v2.0)
- [ ] Real-time collaborative interviews
- [ ] AI-powered code review feedback
- [ ] Custom question banks
- [ ] Analytics dashboard
- [ ] Mobile application

---

**Made with ❤️ by the Repo_Based_Interviewer Team**

*Star ⭐ this repository if you find it helpful!*