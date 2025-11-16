# Repository-Based Interviewer 🎯

A RAG (Retrieval-Augmented Generation) based intelligent interviewer system that analyzes GitHub repositories and conducts technical interviews based on the repository content.

## 📋 Overview

This project creates an AI-powered interviewer that:
- Takes GitHub repository links as input
- Analyzes the repository content (code, documentation, structure)
- Generates contextual questions based on the repository
- Evaluates user responses to assess understanding of the codebase

Perfect for technical interviews, code reviews, onboarding assessments, or self-learning!

## ✨ Features

- **Repository Analysis**: Automatically clones and analyzes GitHub repositories
- **Intelligent Question Generation**: Creates relevant questions based on:
  - Code patterns and implementations
  - Architecture and design decisions
  - Dependencies and technologies used
  - Documentation and README content
- **Context-Aware Evaluation**: Evaluates answers using RAG to compare against actual repository content
- **Multiple Question Types**: 
  - Code understanding questions
  - Architecture and design questions
  - Best practices and code quality questions
  - Debugging and troubleshooting scenarios
- **Scoring System**: Provides detailed feedback and scores for user responses

## 🏗️ System Architecture

```
┌─────────────────┐
│  GitHub Repo    │
│      URL        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Repository     │
│   Processor     │
│  - Clone repo   │
│  - Parse files  │
│  - Extract code │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vector Store   │
│  (Embeddings)   │
│  - Code chunks  │
│  - Documentation│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  RAG Engine     │
│  - Retrieval    │
│  - Generation   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Question      │
│   Generator     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   User          │
│   Interface     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Answer        │
│   Evaluator     │
│  (RAG-based)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Results &      │
│  Feedback       │
└─────────────────┘
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Git
- OpenAI API key (or compatible LLM API)
- Sufficient storage for repository cloning

### Installation

```bash
# Clone this repository
git clone https://github.com/Mageshwaran18/Repo_Based_Interviewer.git
cd Repo_Based_Interviewer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys
```

### Environment Variables

Create a `.env` file with the following:

```env
OPENAI_API_KEY=your_openai_api_key
VECTOR_DB_PATH=./vector_store
TEMP_REPO_PATH=./temp_repos
MAX_FILE_SIZE_MB=5
SUPPORTED_EXTENSIONS=.py,.js,.ts,.java,.cpp,.go,.rs
```

## 📖 Usage

### Basic Usage

```python
from repo_interviewer import RepoInterviewer

# Initialize the interviewer
interviewer = RepoInterviewer()

# Load a repository
repo_url = "https://github.com/username/repository"
interviewer.load_repository(repo_url)

# Generate questions
questions = interviewer.generate_questions(num_questions=5)

# Conduct interview
for question in questions:
    print(f"Q: {question.text}")
    user_answer = input("Your answer: ")
    
    # Evaluate answer
    evaluation = interviewer.evaluate_answer(question, user_answer)
    print(f"Score: {evaluation.score}/10")
    print(f"Feedback: {evaluation.feedback}")
```

### Command Line Interface

```bash
# Start interactive interview
python main.py --repo https://github.com/username/repository

# Generate specific number of questions
python main.py --repo https://github.com/username/repository --questions 10

# Export questions to file
python main.py --repo https://github.com/username/repository --export questions.json

# Resume previous session
python main.py --session session_id
```

### Web Interface

```bash
# Start web server
python app.py

# Open browser to http://localhost:5000
# Enter GitHub repository URL
# Start interview
```

## 🧠 How It Works

### 1. Repository Processing
- Clones the repository to a temporary location
- Parses and extracts code files based on supported extensions
- Filters out binary files, large files, and build artifacts
- Extracts metadata (structure, dependencies, README)

### 2. Vectorization & Indexing
- Chunks code files into semantic segments
- Generates embeddings using language models
- Stores in vector database (FAISS, Pinecone, or Chroma)
- Creates index for efficient retrieval

### 3. Question Generation
- Analyzes repository context and complexity
- Uses RAG to retrieve relevant code segments
- Generates questions covering:
  - Code functionality and logic
  - Design patterns used
  - Error handling approaches
  - Testing strategies
  - Performance considerations

### 4. Answer Evaluation
- Retrieves relevant context from vector store
- Compares user answer with actual repository content
- Uses LLM to assess:
  - Accuracy of understanding
  - Completeness of answer
  - Technical depth
- Provides constructive feedback

## 🛠️ Technology Stack

- **Language Models**: OpenAI GPT-4, Anthropic Claude, or local LLMs
- **Embeddings**: OpenAI Embeddings, Sentence Transformers
- **Vector Database**: FAISS, Pinecone, or ChromaDB
- **Code Parsing**: Tree-sitter, AST parsers
- **Web Framework**: Flask or FastAPI (for web interface)
- **Git Operations**: GitPython
- **UI**: Streamlit or React (optional)

## 📊 Evaluation Metrics

The system evaluates answers based on:

1. **Accuracy** (0-10): How correct the answer is
2. **Completeness** (0-10): Coverage of all aspects
3. **Depth** (0-10): Technical understanding demonstrated
4. **Relevance** (0-10): Alignment with actual repository content

**Overall Score** = Average of all metrics

## 🎯 Use Cases

- **Technical Interviews**: Assess candidate's ability to understand new codebases
- **Onboarding**: Help new developers learn project structure
- **Code Review Training**: Practice reviewing and understanding code
- **Self-Assessment**: Test your own understanding of repositories you've worked on
- **Educational**: Learn from open-source projects through guided questioning

## 🔧 Configuration

### Customizing Question Types

Edit `config/question_templates.yaml`:

```yaml
question_types:
  - type: "code_understanding"
    weight: 0.3
    difficulty: [easy, medium, hard]
  
  - type: "architecture"
    weight: 0.2
    difficulty: [medium, hard]
  
  - type: "best_practices"
    weight: 0.2
    difficulty: [medium]
  
  - type: "debugging"
    weight: 0.3
    difficulty: [easy, medium, hard]
```

### Adjusting Difficulty Levels

```python
interviewer.set_difficulty("medium")  # easy, medium, hard, expert
```

## 📁 Project Structure

```
Repo_Based_Interviewer/
├── src/
│   ├── repo_processor.py      # Repository cloning and parsing
│   ├── vectorizer.py           # Embedding generation and storage
│   ├── question_generator.py   # Question generation logic
│   ├── evaluator.py            # Answer evaluation
│   └── rag_engine.py           # RAG implementation
├── config/
│   ├── config.yaml             # Main configuration
│   └── question_templates.yaml # Question templates
├── tests/
│   └── test_*.py               # Unit tests
├── web/
│   ├── app.py                  # Web application
│   └── templates/              # HTML templates
├── main.py                     # CLI entry point
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
└── README.md                   # This file
```

## 🔒 Privacy & Security

- Repository contents are processed locally by default
- Sensitive files can be excluded via `.interviewignore` file
- API keys are never logged or stored in version control
- Temporary repositories are cleaned up after processing

## 🚧 Future Enhancements

- [ ] Support for multiple programming languages
- [ ] Integration with more LLM providers
- [ ] Advanced code graph analysis
- [ ] Collaborative interview mode
- [ ] Interview analytics and insights
- [ ] Custom question bank creation
- [ ] Integration with CI/CD pipelines
- [ ] Multi-repository analysis
- [ ] Voice-based interview mode
- [ ] Mobile application

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and development process.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Mageshwaran** - *Initial work* - [Mageshwaran18](https://github.com/Mageshwaran18)

## 🙏 Acknowledgments

- Thanks to the open-source community for LLM tools and libraries
- Inspired by the need for better technical interview processes
- Built with ❤️ for developers and interviewers

## 📞 Contact & Support

- GitHub Issues: [Create an issue](https://github.com/Mageshwaran18/Repo_Based_Interviewer/issues)
- Email: [Your contact email]
- Discussions: [GitHub Discussions](https://github.com/Mageshwaran18/Repo_Based_Interviewer/discussions)

## 🌟 Star History

If you find this project useful, please consider giving it a star ⭐!

---

**Note**: This is an AI-powered tool. Always verify important technical assessments with human review and judgment.