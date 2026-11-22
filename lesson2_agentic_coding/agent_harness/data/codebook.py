"""The researcher's codebook: notebook 01 (lesson 1), copied word for word.

The agent may import it, never change it: the codebook is method, and method belongs to the researcher.
Keeping it identical to notebook 01 also means the saved answers replay (same prompt, same answer).
"""
from typing import Literal

from pydantic import BaseModel, Field

Domain = Literal["health", "finance", "manufacturing", "transport", "energy",
                 "retail & consumer", "ICT & telecom", "other"]

class PatentCode(BaseModel):
    is_ai: bool = Field(description="True if the invention uses or improves artificial intelligence or machine learning")
    technology: str = Field(description="The core technology in 2 to 5 words")
    problem_solved: str = Field(description="The problem the invention solves, in one short sentence")
    application_domain: Domain = Field(description="The main sector where the invention is used")
    automation_vs_augmentation: Literal["automates human work", "augments human work", "neither"]
    evidence_quote: str = Field(description="A phrase of 3 to 12 words copied word for word from the abstract that best supports your is_ai answer. Never empty.")

INSTRUCTIONS = """You are a research assistant coding patent abstracts for an innovation study.
Read the patent abstract and fill in every field of the codebook. Base your answers only on the text."""
