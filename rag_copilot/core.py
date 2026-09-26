"""Small, reproducible retrieval-augmented question answering core."""
from __future__ import annotations
import logging, math, os, re
from dataclasses import dataclass
from pathlib import Path

TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n+")

@dataclass(frozen=True)
class Chunk:
    source: str
    page: int
    text: str
    @property
    def citation(self) -> str:
        return f"{self.source}, p. {self.page}"

@dataclass(frozen=True)
class Retrieval:
    chunk: Chunk
    score: float

def tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text)]

def load_documents(data_dir: str | Path) -> list[Chunk]:
    logging.getLogger("pypdf").setLevel(logging.ERROR)
    root = Path(data_dir); chunks = []
    for path in sorted(root.rglob("*")):
        if path.suffix.lower() == ".txt":
            page, buf = 1, []
            for line in path.read_text(encoding="utf-8").splitlines():
                marker = re.match(r"\s*\[Page\s+(\d+)\]\s*$", line, re.I)
                if marker:
                    if " ".join(buf).strip(): chunks.append(Chunk(path.name, page, " ".join(buf).strip()))
                    page, buf = int(marker.group(1)), []
                else: buf.append(line)
            if " ".join(buf).strip(): chunks.append(Chunk(path.name, page, " ".join(buf).strip()))
        elif path.suffix.lower() == ".pdf":
            try:
                from pypdf import PdfReader
            except ImportError as exc:
                raise RuntimeError("Install requirements.txt to read PDF files.") from exc
            for n, page in enumerate(PdfReader(str(path)).pages, 1):
                text = (page.extract_text() or "").strip()
                if text: chunks.append(Chunk(path.name, n, text))
    if not chunks: raise FileNotFoundError(f"No .txt or .pdf documents found under {root}")
    return chunks

class Retriever:
    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks; self.df = {}; self.vectors = []
        for c in chunks:
            # Index the filename as lightweight provenance metadata. This helps a
            # question mentioning a university select that university's document,
            # while the answer itself is still generated from page text only.
            terms = set(tokenize(c.text + " " + c.source)); self.vectors.append(terms)
            for t in terms: self.df[t] = self.df.get(t, 0) + 1
    def _vector(self, text: str):
        counts = {}
        for t in tokenize(text): counts[t] = counts.get(t, 0) + 1
        n = len(self.chunks)
        return {t: (1 + math.log(v)) * math.log((1+n)/(1+self.df.get(t,0))) for t,v in counts.items()}
    def search(self, query: str, k: int = 3) -> list[Retrieval]:
        q = self._vector(query); qn = math.sqrt(sum(v*v for v in q.values())) or 1
        out = []
        for c, terms in zip(self.chunks, self.vectors):
            v = {t: math.log((1+len(self.chunks))/(1+self.df[t])) for t in terms}
            denom = (math.sqrt(sum(x*x for x in v.values())) * qn) or 1
            out.append(Retrieval(c, sum(q.get(t,0)*x for t,x in v.items())/denom))
        return sorted(out, key=lambda x: x.score, reverse=True)[:k]

class CampusCopilot:
    def __init__(self, chunks: list[Chunk], min_score: float = 0.08):
        self.retriever = Retriever(chunks); self.min_score = min_score
    def answer(self, question: str, k: int = 3) -> dict:
        hits = self.retriever.search(question, k); evidence = [r for r in hits if r.score >= self.min_score]
        if not evidence:
            return {"answer":"I do not have enough evidence in the current documents to answer this question.", "abstained":True, "citations":[], "retrieval":[]}
        return {"answer":self._generate(question, evidence), "abstained":False, "citations":[r.chunk.citation for r in evidence], "retrieval":[{"citation":r.chunk.citation,"score":round(r.score,4)} for r in hits]}
    def _generate(self, question: str, evidence: list[Retrieval]) -> str:
        if os.getenv("OPENAI_API_KEY"):
            try:
                from openai import OpenAI
                ctx = "\n\n".join(f"[{r.chunk.citation}] {r.chunk.text}" for r in evidence)
                prompt = ("Answer only from the evidence. If unsupported, say exactly: I do not have enough evidence in the current documents. "
                          "Be concise and cite the source.\n\nQuestion: " + question + "\n\nEvidence:\n" + ctx)
                res = OpenAI().chat.completions.create(model=os.getenv("OPENAI_MODEL","gpt-4o-mini"), messages=[{"role":"user","content":prompt}], temperature=0)
                return res.choices[0].message.content.strip()
            except Exception:
                pass
        q = set(tokenize(question)); candidates = []
        for r in evidence:
            for sentence in SENTENCE_RE.split(r.chunk.text):
                if sentence.strip(): candidates.append((len(q & set(tokenize(sentence))), sentence.strip()))
        return " ".join(s for _, s in sorted(candidates, reverse=True)[:2]) or evidence[0].chunk.text[:500]
