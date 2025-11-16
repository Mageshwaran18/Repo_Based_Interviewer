# Repo_Based_Interviewer

A lightweight RAG (Retrieval-Augmented Generation) system that:
- Accepts a GitHub repository URL as input.
- Automatically fetches and indexes repository content (code, docs, README).
- Generates interview-style questions from the repository contents.
- Presents questions to a user and evaluates user answers using retrieval and automated scoring.

## Key features
- Repo ingestion: clone or fetch files via GitHub API.
- Document processing: parse markdown, code, and text into retrievable chunks.
- Embedding + vector store: build a semantic index for fast retrieval (FAISS, SQLite, etc.).
- Question generation: produce topical, repository-specific questions.
- Answer evaluation: score answers with similarity/LLM-based rubric and provide feedback.
- Configurable pipeline components and scoring thresholds.

## Architecture (high level)
1. Fetch repository -> normalize files.
2. Chunk & embed documents -> store in vector DB.
3. Use retriever to pull context for question generation.
4. Generate questions and present them to the user (CLI/web).
5. Collect user responses -> retrieve evidence -> evaluate/scored feedback.

## Quick start (example)
1. Install dependencies:
    - Python 3.9+
    - pip install -r requirements.txt
2. Set environment variables (example):
    - GITHUB_TOKEN (optional, higher rate limits)
    - OPENAI_API_KEY or other embedding/model keys
3. Run:
    - python run_interview.py --repo https://github.com/owner/repo
    - Options: --mode [interview|generate|evaluate], --vector-store [faiss|sqlite], --limit-files N

## Usage notes
- Input: a single GitHub repo URL (public or authenticated via token).
- The system indexes README, docs, and code comments first for best question coverage.
- Questions can be multiple-choice, short-answer, or open-ended depending on config.
- Evaluation strategies:
  - Embedding similarity between user answer and retrieved evidence.
  - LLM-based rubric scoring that checks correctness, completeness, and relevance.
  - Configurable scoring thresholds and partial-credit rules.

## Configuration
- config.yml contains options for chunk size, embedding model, retriever top-k, question templates, and evaluation settings.
- Swap embedding/model provider by updating config and credentials.

## Example CLI
- Generate questions only:
  - python run_interview.py --repo <url> --mode generate --out questions.json
- Interactive interview (prompt user, then evaluate):
  - python run_interview.py --repo <url> --mode interview

## Extensibility
- Add new document loaders for additional file types.
- Plug in alternative embedding backends or local LLMs.
- Extend evaluation with custom rubrics or human-in-the-loop review.

## Contributing
- Follow repository coding standards, add tests for new components, and open PRs with clear descriptions.

## License
- Project uses an open-source license — update LICENSE file as appropriate.

Notes
- Avoid exposing secrets when indexing private repos.
- Adjust evaluation sensitivity for different domains (code vs. design docs).
- For production, prefer authenticated GitHub access and persistent vector storage.