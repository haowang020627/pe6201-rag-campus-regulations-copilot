# Evaluation Documentation

## Evaluation goal

The evaluation checks whether the retriever finds the expected source for supported questions and whether the system abstains for questions outside the committed corpus.

## Evaluation set

`questions.json` contains 50 fixed English questions:

- 48 answerable questions, each with a manually checked `expected_source` filename;
- 2 deliberately unanswerable questions with `expected_source: null` and `should_abstain: true`.

The questions cover the ten public PDF documents in `data/public/`. The two negative examples use fictional topics that are absent from the corpus, providing a simple test of the refusal path.

## Metrics

### Citation hit rate

For each answerable question, the evaluation checks whether the system abstains. If it does not abstain, the retrieved citation is checked against the expected source filename. Citation hit rate is:

```text
number of answerable questions with expected source retrieved
/ number of answerable questions
```

This is a source-retrieval metric. It does not prove that the generated answer is fully correct or that every citation is complete.

### Abstention recall

For each unanswerable question, the evaluation checks whether `abstained` is true. Abstention recall is:

```text
number of unanswerable questions correctly rejected
/ number of unanswerable questions
```

A high value is useful but does not measure false refusals on supported questions or safety in a larger production distribution.

## Reproduce the evaluation

Install the dependencies and run from the repository root:

```bash
python -m pip install -r requirements.txt
python -m rag_copilot.cli --data data/public evaluate
```

The expected current result is approximately:

```text
questions: 50
answerable_questions: 48
citation_hit_rate: 0.9167
unanswerable_questions: 2
abstention_recall: 1.0
```

## Interpretation and limitations

The set is small and developer-authored. Its wording may be easier for the implementation than real student questions, and two negative examples are not enough to estimate production safety. The evaluation does not yet include human answer-quality ratings, a controlled `Ctrl+F` comparison, representative student participants, confidence intervals, latency measurements, or API cost measurements. These should be part of a future evaluation before any institutional deployment claim is made.