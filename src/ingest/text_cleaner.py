# text_cleaner.py - Text cleaning pipeline
import unicodedata
import re


def normalize_unicode(text: str) -> str:
    """Normalize Unicode to NFC form and replace common artifacts."""
    # Normalize to NFC (composed form)
    text = unicodedata.normalize("NFC", text)
    # Replace common Unicode artifacts
    text = text.replace("\u00a0", " ")   # Non-breaking space
    text = text.replace("\u200b", "")    # Zero-width space
    text = text.replace("\ufeff", "")    # BOM
    text = text.replace("\u2028", "\n")  # Line separator
    text = text.replace("\u2029", "\n")  # Paragraph separator
    return text


def collapse_whitespace(text: str) -> str:
    """Reduce excessive whitespace while preserving paragraph breaks."""
    # Replace tabs with spaces
    text = text.replace("\t", " ")
    # Collapse multiple spaces to one
    text = re.sub(r" {2,}", " ", text)
    # Collapse 3+ newlines to 2 (preserve paragraph breaks)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip trailing whitespace on each line
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    return text


def remove_boilerplate(text: str, patterns: list[str] | None = None) -> str:
    """Remove repeated headers, footers, and page numbers."""
    lines = text.split("\n")
    if patterns is None:
        # Common boilerplate patterns
        patterns = [
            r"^\s*Page \d+ of \d+\s*$",
            r"^\s*-\s*\d+\s*-\s*$",
            r"^\s*\d+\s*$",  # Bare page numbers
            r"^(CONFIDENTIAL|DRAFT|DO NOT DISTRIBUTE)\s*$",
        ]

    compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
    cleaned_lines = []
    for line in lines:
        if any(p.match(line) for p in compiled):
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def remove_empty_sections(text: str, min_chars: int = 10) -> str:
    """Remove sections that contain too little text to be useful."""
    paragraphs = text.split("\n\n")
    meaningful = [p for p in paragraphs if len(p.strip()) >= min_chars]
    return "\n\n".join(meaningful)


def clean_text(text: str) -> str:
    """Run the full cleaning pipeline."""
    text = normalize_unicode(text)
    text = collapse_whitespace(text)
    text = remove_boilerplate(text)
    text = remove_empty_sections(text)
    text = text.strip()
    return text