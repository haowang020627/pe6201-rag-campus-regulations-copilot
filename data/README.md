# Data Documentation

## Purpose

This directory contains the documents used by the RAG Campus Regulations Co-pilot.

- `data/demo/` is a small offline smoke-test corpus for a first run and unit-test demonstration.
- `data/public/` is the evaluation corpus containing ten publicly accessible university policy or student-regulation PDFs.

## Public corpus

The ten PDF filenames, institutions, titles, official URLs, page counts, and local validation notes are recorded in [`public/SOURCES.md`](public/SOURCES.md). SHA-256 checksums for the committed PDF files are recorded in [`public/SHA256SUMS`](public/SHA256SUMS).

The corpus was selected to cover several regulation patterns, including academic progression, student conduct, disciplinary processes, research administration, grievances, and institutional responsibilities. The documents are used as a reproducible public corpus for a course prototype; they are not claimed to represent every university or every current policy.

## Processing and loading

The loader recursively searches a selected data directory for `.txt` and `.pdf` files. Text PDFs are parsed with `pypdf`. The demo text files include explicit `[Page N]` markers so that citations can be demonstrated offline. PDF page numbers are preserved during extraction where text is available.

The prototype does not include OCR. Scanned or image-only pages may therefore produce little searchable text. If a PDF is replaced or refreshed, regenerate the checksum file and update `SOURCES.md` with the retrieval date and any relevant version information.

## Data limitations and responsible use

The corpus contains public documents and should not be treated as a live institutional policy service. Regulations can change after the repository snapshot. Users must verify deadlines, sanctions, appeals, and other high-stakes matters against the current official source. No private student records are included or required for the demo.

## Reproducibility check

From `data/public/`, verify the committed checksums with:

```bash
sha256sum -c SHA256SUMS
```

Then run the full evaluation from the repository root:

```bash
python -m rag_copilot.cli --data data/public evaluate
```