# RAG Campus Regulations Co-pilot

A small, reproducible Retrieval-Augmented Generation (RAG) prototype for answering student questions from university regulation documents with page citations or an explicit abstention.

> **Project status:** This is an offline-first command-line prototype for the PE6201 course project. It is not a production web service and must not replace official university communication.

## What is included

- Deterministic TF-IDF-style retrieval implemented in pure Python.
- `.txt` documents with `[Page N]` markers and `.pdf` documents read with `pypdf`.
- Citation-aware answers and a configurable minimum-relevance abstention rule.
- Offline extractive answer fallback, so the demo runs without an API key or network access.
- Optional OpenAI-compatible generation when `OPENAI_API_KEY` is set.
- A committed 50-question evaluation set and reproducible baseline-oriented metrics.
- Ten publicly accessible university policy PDFs in `data/public/`, with source URLs and checksums.

## Requirements

- Python 3.10 or newer (tested with Python 3.12).
- `pip` and a virtual-environment module.
- Internet access is only needed to install dependencies or use optional model generation. The offline demo does not require an API key.

## Installation

Run these commands from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate             # Windows PowerShell: .venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Quick smoke test

The small `data/demo/` corpus is recommended for the first run:

```bash
python -m rag_copilot.cli --data data/demo ask "What is the late submission penalty?"
```

The command prints JSON containing:

- `answer`: the extractive or model-generated answer;
- `abstained`: whether the system refused to answer because evidence was insufficient;
- `citations`: source filename and page number for the evidence used;
- `retrieval`: the top retrieved chunks and relevance scores.

Test the refusal path as well:

```bash
python -m rag_copilot.cli --data data/demo ask "What is the university's cryptocurrency investment policy?"
```

## Tests

Run the unit tests from the repository root:

```bash
python -m unittest discover -s tests -v
```

The tests verify citation inclusion for supported questions and abstention for an unsupported question. A successful run should end with `OK`.

For a quick syntax and CLI check:

```bash
python -m rag_copilot.cli --help
python -m compileall -q rag_copilot tests
```

## Evaluation

The committed `evaluation/questions.json` contains 50 fixed questions: 48 answerable questions and 2 questions that should trigger abstention. Each answerable item has a manually checked expected source file.

Run the evaluation against the small demo corpus:

```bash
python -m rag_copilot.cli --data data/demo evaluate
```

This command is a smoke test for the evaluation pipeline. Because the expected source files in `evaluation/questions.json` belong to the public corpus, its citation hit rate is not an accuracy baseline for `data/demo`.

Run the full evaluation against the ten-document public corpus:

```bash
python -m rag_copilot.cli --data data/public evaluate
```

The output reports:

- `questions`: total evaluation questions;
- `answerable_questions`: questions expected to have evidence;
- `citation_hit_rate`: whether a retrieved citation came from the expected source file;
- `unanswerable_questions`: questions expected to be rejected;
- `abstention_recall`: the proportion of unsupported questions correctly rejected.

These are retrieval and abstention metrics, not a human-rated answer-quality study. Answer correctness, citation completeness, and any claimed time saving require a separate manual scoring protocol or participant study. `Ctrl+F` over the same documents is the non-AI baseline.

## CLI options

```text
python -m rag_copilot.cli [--data DIRECTORY] [--min-score FLOAT] ask QUESTION...
python -m rag_copilot.cli [--data DIRECTORY] [--min-score FLOAT] evaluate [--file PATH]
```

- `--data` selects a directory recursively searched for `.txt` and `.pdf` files. It defaults to `data/demo`.
- `--min-score` controls the abstention threshold and defaults to `0.08`. Raising it generally makes the system more conservative; lowering it may increase unsupported answers.
- `evaluate --file` selects a compatible JSON evaluation file and defaults to `evaluation/questions.json`.

## Optional model generation

The default offline fallback is deterministic and is recommended for a reproducible course demonstration. To enable optional OpenAI-compatible generation:

```bash
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="gpt-4o-mini"
python -m rag_copilot.cli --data data/demo ask "What is the late submission penalty?"
```

The model receives only the retrieved evidence and is instructed not to invent unsupported facts. If the API call fails, the program silently falls back to the offline extractive answer. API usage may incur external costs; do not commit keys to the repository.

## Public document corpus

`data/public/` contains ten publicly accessible university policy PDFs. `data/public/SOURCES.md` lists each institution, title, official URL, and locally verified page count. `data/public/SHA256SUMS` records checksums for the committed PDFs.

The loader uses `pypdf` text extraction. Scanned or image-only PDF pages may produce little or no searchable text; this prototype does not perform OCR. If a PDF is replaced, regenerate and verify the checksum file before committing it.

## Deployment boundary

No server deployment is required for the submitted prototype: the supported demonstration is a local terminal run, and the application does not expose an HTTP API or persistent database. For a classroom demo, clone the repository, install the dependencies, and run the smoke test or evaluation command above.

A future deployment could wrap `CampusCopilot` in a Flask/FastAPI service and add authentication, rate limiting, document versioning, logging, and privacy controls. Those controls are intentionally outside this course prototype and should be implemented before handling private or high-stakes institutional data.

## Troubleshooting

- **`ModuleNotFoundError: pypdf`**: activate `.venv` and run `python -m pip install -r requirements.txt`.
- **`No .txt or .pdf documents found`**: run the command from the repository root or pass the correct `--data` path.
- **PDF produces no useful citations**: check whether the PDF is scanned/image-only; OCR is not included.
- **Answers are too broad or unsupported**: increase `--min-score`, for example `--min-score 0.12`, and verify the source document.
- **Optional model output is unavailable**: confirm `OPENAI_API_KEY` is set; the offline fallback should still work without it.

## Scope and responsible use

This prototype retrieves public documents only. It does not register courses, process payments, make disciplinary decisions, or replace official university communication. Students should verify deadlines, disciplinary matters, housing obligations, and other high-stakes matters with the official university channel.

## Repository layout

```text
rag-campus-copilot/
├── rag_copilot/              # retrieval, answering, and CLI implementation
├── data/demo/                # small offline smoke-test corpus
├── data/public/              # ten public PDFs, sources, and checksums
├── evaluation/questions.json # fixed evaluation questions
├── tests/                    # unit tests
├── requirements.txt
└── README.md
```

## GitHub

Repository: <https://github.com/haowang020627/pe6201-rag-campus-regulations-copilot>

To clone and run the project:

```bash
git clone https://github.com/haowang020627/pe6201-rag-campus-regulations-copilot.git
cd pe6201-rag-campus-regulations-copilot
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m rag_copilot.cli --data data/demo ask "What is the late submission penalty?"
```
