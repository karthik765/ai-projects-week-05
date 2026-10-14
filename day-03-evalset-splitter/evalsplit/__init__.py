"""Deterministic, leakage-aware JSONL dataset splitting."""

from .models import SplitConfig, SplitResult
from .splitter import split_records

__all__ = ["SplitConfig", "SplitResult", "split_records"]
