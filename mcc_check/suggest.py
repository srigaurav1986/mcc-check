"""नाम या narration से MCC का संकेत (suggestion) देना।

यह केवल संकेत है। अंतिम MCC acquirer या payment service provider तय करता है।
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .data import MCC_TABLE


@dataclass(frozen=True)
class Suggestion:
    code: str
    name: str
    score: int
    matched: tuple


def normalize(text: str) -> str:
    """Lowercase करें, विराम चिह्न हटाएँ, और देवनागरी अक्षर बनाए रखें।"""
    text = text.lower()
    text = re.sub(r"[^\wऀ-ॿ]+", " ", text)
    return f" {' '.join(text.split())} "


def suggest(text: str, limit: int = 3) -> list:
    haystack = normalize(text)
    results = []
    for entry in MCC_TABLE:
        matched = [kw for kw in entry.keywords if f" {kw} " in haystack]
        if matched:
            score = sum(len(kw) for kw in matched)
            results.append(Suggestion(entry.code, entry.name, score, tuple(matched)))
    results.sort(key=lambda s: (-s.score, s.code))
    return results[:limit]


def confidence(results: list) -> float:
    """पहले सुझाव का हिस्सा, सभी मिलान वाले सुझावों के योग में (0 से 1)।"""
    if not results:
        return 0.0
    total = sum(r.score for r in results)
    return round(results[0].score / total, 2)
