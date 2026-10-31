"""Validated contracts shared by local and generated content."""

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Level = Literal["A1", "A2", "B1"]


class Vocabulary(BaseModel):
    """A phrase, contextual explanation and recall sentence."""

    model_config = ConfigDict(extra="forbid")
    term: str = Field(min_length=1, max_length=100)
    explanation_de: str = Field(min_length=1, max_length=250)
    meaning_ar: str = Field(min_length=1, max_length=150)
    example: str = Field(min_length=1, max_length=250)
    answer: str = Field(min_length=1, max_length=100)
    translation_de: str = Field(min_length=1, max_length=200)
    translation_ar: str = Field(min_length=1, max_length=200)

    @model_validator(mode="after")
    def answer_occurs(self) -> "Vocabulary":
        """Require a literal cloze answer."""
        if self.answer not in self.example:
            raise ValueError("The answer must occur verbatim in the example.")
        return self


class Lesson(BaseModel):
    """One bounded, original lesson."""

    model_config = ConfigDict(extra="forbid")
    id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,80}$")
    level: Level
    title: str = Field(min_length=1, max_length=120)
    goal: str = Field(min_length=1, max_length=300)
    dialogue: list[str] = Field(min_length=5, max_length=12)
    vocabulary: list[Vocabulary] = Field(min_length=8, max_length=8)
    grammar_de: str = Field(min_length=1, max_length=700)
    grammar_ar: str = Field(min_length=1, max_length=700)
    speaking: str = Field(min_length=1, max_length=350)
    speaking_ar: str = Field(min_length=1, max_length=350)
    culture: str = Field(min_length=1, max_length=400)

    @model_validator(mode="after")
    def level_length(self) -> "Lesson":
        """Check the level-specific sentence budget and distinct vocabulary."""
        lo, hi = (8, 12) if self.level == "B1" else (5, 8)
        if not lo <= len(self.dialogue) <= hi:
            raise ValueError(f"{self.level} requires {lo}–{hi} sentences.")
        if len({v.term for v in self.vocabulary}) != 8:
            raise ValueError("Use eight distinct vocabulary items.")
        german_fields = [
            self.title,
            self.goal,
            self.grammar_de,
            self.speaking,
            self.culture,
            *self.dialogue,
        ]
        for vocab in self.vocabulary:
            german_fields.extend(
                [
                    vocab.term,
                    vocab.explanation_de,
                    vocab.example,
                    vocab.answer,
                    vocab.translation_de,
                ]
            )
        if any(re.search(r"[\u0600-\u06ff]", text) for text in german_fields):
            raise ValueError("German fields must not contain Arabic text.")
        return self


class Correction(BaseModel):
    """One constructive sentence correction."""

    original: str
    corrected: str
    explanation_de: str
    explanation_ar: str


class Feedback(BaseModel):
    """Feedback without invented proficiency scores."""

    encouragement: str
    corrections: list[Correction]
    next_goal: str
