from __future__ import annotations
import argparse, json
from pathlib import Path
from .core import CampusCopilot, load_documents

def main():
    p = argparse.ArgumentParser(description="RAG Campus Regulations Co-pilot")
    p.add_argument("--data", default="data/demo", help="Directory containing .txt or .pdf files")
    p.add_argument("--min-score", type=float, default=0.08)
    sub = p.add_subparsers(dest="command", required=True)
    ask = sub.add_parser("ask"); ask.add_argument("question", nargs="+")
    ev = sub.add_parser("evaluate"); ev.add_argument("--file", default="evaluation/questions.json")
    args = p.parse_args()
    copilot = CampusCopilot(load_documents(args.data), min_score=args.min_score)
    if args.command == "ask":
        print(json.dumps(copilot.answer(" ".join(args.question)), indent=2))
        return
    rows = json.loads(Path(args.file).read_text(encoding="utf-8"))
    correct = answerable = correct_abstentions = unanswerable = 0
    for row in rows:
        result = copilot.answer(row["question"])
        should_abstain = bool(row.get("should_abstain", False))
        if should_abstain:
            unanswerable += 1
            if result["abstained"]: correct_abstentions += 1
        else:
            answerable += 1
            if row.get("expected_source") and any(citation.startswith(row["expected_source"] + ",") for citation in result["citations"]): correct += 1
    print(json.dumps({"questions":len(rows), "answerable_questions":answerable,
                      "citation_hit_rate":correct/answerable if answerable else 0,
                      "unanswerable_questions":unanswerable,
                      "abstention_recall":correct_abstentions/unanswerable if unanswerable else 0}, indent=2))

if __name__ == "__main__": main()
