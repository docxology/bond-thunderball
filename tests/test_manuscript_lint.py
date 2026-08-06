"""Closes V1 and V4 from TODO.md: two prose-integrity gates.

V1 — no measured metric decays in agent-facing prose. Any token count, test
count, or coverage percentage written into README.md, AGENTS.md, or docs/*.md
will go stale the moment the code changes, exactly as the "53 computed
manuscript tokens" in AGENTS.md did. Such counts may only live in the
regenerated ``docs/_generated/COUNTS.md``; prose describes the gate, not a
figure.

V4 — the manuscript's cross-references resolve. Every ``@fig:``/``@sec:``/
``@tbl:`` reference must name a label that is actually defined, and every
``[@citation_key]`` must name an entry that exists in ``references.bib``. A
dangling label or a bib key with no entry otherwise slips through every gate
in this package.
"""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# V1 — no decaying measured metric in agent-facing prose
# ---------------------------------------------------------------------------

#: Patterns that, matched outside COUNTS.md, are measured counts that will rot:
#: a token count, a test/pass/fail/skip count, or a measured 100% coverage.
DECAYING = [
    re.compile(r"\b\d+\s+(computed\s+)?manuscript\s+tokens?\b"),
    re.compile(
        r"\b\d+\s+(passed|passing|tests?|failures?|failing|failed|skipped|skips?)\b"
    ),
    re.compile(r"\b100(?:\.0+)?%\b"),
]


def _agent_facing_docs() -> list[Path]:
    docs = [PROJECT_ROOT / "AGENTS.md", PROJECT_ROOT / "README.md"]
    for p in sorted((PROJECT_ROOT / "docs").glob("*.md")):
        if "_generated" in p.parts:
            continue
        docs.append(p)
    return docs


def test_no_measured_metric_decays_in_agent_facing_prose() -> None:
    """The done-when for V1: counts live only in COUNTS.md; a reintroduced
    count (e.g. "89 manuscript tokens" or "201 passed") fails this immediately.
    """
    scanned: list[Path] = []
    offenders: list[str] = []
    for path in _agent_facing_docs():
        scanned.append(path)
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for pat in DECAYING:
                if pat.search(line):
                    offenders.append(f"{path.name}:{lineno}: {line.strip()}")
    # Pin the guard against being vacuous: it must actually scan the prose.
    assert len(scanned) >= 6, sorted(str(p.name) for p in scanned)
    assert not offenders, (
        "measured metric found in agent-facing prose (move it to "
        "docs/_generated/COUNTS.md):\n" + "\n".join(offenders)
    )


# ---------------------------------------------------------------------------
# V4 — manuscript cross-references resolve
# ---------------------------------------------------------------------------

REF_RE = re.compile(r"@([a-z]+):([A-Za-z0-9_]+)")
DEF_RE = re.compile(r"\{#([A-Za-z0-9_:]+)\}")
CITE_RE = re.compile(r"\[@([A-Za-z0-9_]+)\]")


def _numbered_sections() -> list[Path]:
    return sorted((PROJECT_ROOT / "manuscript").glob("[0-9]*.md"))


def test_manuscript_crossref_labels_resolve() -> None:
    """The done-when for V4: an unresolved @fig:/@sec:/@tbl: fails here."""
    referenced: set[tuple[str, str]] = set()
    defined: set[str] = set()
    for section in _numbered_sections():
        text = section.read_text(encoding="utf-8")
        referenced.update(REF_RE.findall(text))
        defined.update(DEF_RE.findall(text))
    # Pin against vacuity: we must have actually found labels to check.
    assert len(referenced) >= 5, sorted(referenced)
    assert len(defined) >= 5, sorted(defined)
    missing = sorted(f"{k}:{v}" for k, v in referenced if f"{k}:{v}" not in defined)
    assert not missing, f"crossref labels referenced but never defined: {missing}"


def test_manuscript_citation_keys_resolve() -> None:
    """The done-when for V4: a citation key absent from references.bib fails."""
    bib = (PROJECT_ROOT / "manuscript" / "references.bib").read_text(encoding="utf-8")
    bib_keys = set(re.findall(r"@\w+\{([^,]+),", bib))
    cited: set[str] = set()
    for section in _numbered_sections():
        cited.update(CITE_RE.findall(section.read_text(encoding="utf-8")))
    assert len(cited) >= 5, sorted(cited)
    assert len(bib_keys) >= 5, sorted(bib_keys)
    missing = sorted(k for k in cited if k not in bib_keys)
    assert not missing, f"citation keys with no bib entry: {missing}"
