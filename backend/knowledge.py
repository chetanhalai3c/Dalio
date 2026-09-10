from pathlib import Path
import re


# =========================
# Knowledge Configuration
# =========================

KNOWLEDGE_DIR = (
    Path(__file__).resolve().parent.parent
    / "knowledge"
)


# =========================
# Full File Loader
# =========================

def load_knowledge_files(
    filenames: list[str],
) -> str:
    knowledge_sections = []

    for filename in filenames:
        file_path = KNOWLEDGE_DIR / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Knowledge file not found: {filename}"
            )

        content = file_path.read_text(
            encoding="utf-8"
        )

        knowledge_sections.append(
            f"""
=========================
SOURCE: {filename}
=========================

{content}
"""
        )

    return "\n".join(knowledge_sections)


# =========================
# Markdown Section Splitter
# =========================

def _split_markdown_sections(
    content: str,
) -> list[str]:
    sections = re.split(
        r"(?=^#{1,6}\s)",
        content,
        flags=re.MULTILINE,
    )

    return [
        section.strip()
        for section in sections
        if section.strip()
    ]


# =========================
# Lightweight Knowledge Retrieval
# =========================

def retrieve_knowledge(
    query: str,
    filenames: list[str],
    keywords: list[str] | None = None,
    max_sections: int = 6,
    max_chars: int = 9000,
) -> str:
    search_terms = {
        word.lower()
        for word in re.findall(
            r"[A-Za-z0-9_-]+",
            query,
        )
        if len(word) >= 4
    }

    if keywords:
        search_terms.update(
            keyword.lower()
            for keyword in keywords
        )

    candidates = []

    for filename in filenames:
        file_path = KNOWLEDGE_DIR / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Knowledge file not found: {filename}"
            )

        content = file_path.read_text(
            encoding="utf-8"
        )

        sections = _split_markdown_sections(
            content
        )

        for section in sections:
            section_lower = section.lower()

            score = sum(
                section_lower.count(term)
                for term in search_terms
            )

            candidates.append(
                {
                    "filename": filename,
                    "section": section,
                    "score": score,
                }
            )

    candidates.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    relevant = [
        item
        for item in candidates
        if item["score"] > 0
    ]

    if not relevant:
        relevant = candidates[:max_sections]

    selected = relevant[:max_sections]

    output_sections = []

    for item in selected:
        output_sections.append(
            f"""
=========================
SOURCE: {item["filename"]}
=========================

{item["section"]}
"""
        )

    result = "\n".join(output_sections)

    return result[:max_chars]