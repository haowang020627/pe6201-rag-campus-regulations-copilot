# RAG Campus Regulations Co-pilot

A small, reproducible Retrieval-Augmented Generation (RAG) prototype for answering student questions from university regulation documents with page citations or an explicit abstention.

## What is included

- Deterministic TF-IDF-style retrieval implemented in pure Python.
- `.txt` documents with `[Page N]` markers and `.pdf` documents via `pypdf`.
- Citation-aware answers and a minimum-relevance abstention rule.
- Offline extractive answer fallback, so the demo runs without an API key.
- Optional OpenAI-compatible generation when `OPENAI_API_KEY` is set.
- A committed evaluation file and a reproducible baseline-oriented evaluation command.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m rag_copilot.cli --data data/demo ask "What is the late submission penalty?"
python -m rag_copilot.cli --data data/demo evaluate
python -m unittest discover -s tests -v
```

The repository also contains `data/public/`, a corpus of ten publicly accessible university policy PDFs. See `data/public/SOURCES.md` for the institution, title, official URL, and locally verified page count. PDF page numbers are retained in citations. `data/demo/` remains a small offline smoke-test corpus.

## Optional model generation

```bash
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="gpt-4o-mini"
python -m rag_copilot.cli --data data/demo ask "What is the late submission penalty?"
```

The model is instructed to use only retrieved evidence. If the API is unavailable, the deterministic offline fallback remains usable.

## Evaluation protocol

The committed `evaluation/questions.json` contains 50 fixed questions: 48 answerable questions and 2 questions that should trigger abstention. Each answerable item has a manually checked expected source file. Run `python -m rag_copilot.cli --data data/public evaluate` to report source citation hit rate and abstention recall. Answer correctness and citation completeness still require the manual scoring sheet used in the final report. Do not claim a time reduction unless it is measured with student participants. `Ctrl+F` over the same documents is the non-AI baseline.

## Scope and responsible use

This prototype retrieves public documents only. It does not register courses, process payments, make disciplinary decisions, or replace official university communication. Students should verify high-stakes matters with the official university channel.

## GitHub

```bash
git init
git add .
git commit -m "Initial RAG campus regulations copilot"
git branch -M main
git remote add origin https://github.com/<your-account>/<your-repository>.git
git push -u origin main
```
