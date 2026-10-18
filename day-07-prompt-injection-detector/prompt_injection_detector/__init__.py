"""Explainable prompt-injection triage heuristics."""

from .detector import detect
from .models import Finding, Report

__all__ = ["Finding", "Report", "detect"]
