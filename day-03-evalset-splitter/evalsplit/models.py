from dataclasses import dataclass, field
from typing import Dict, List, Mapping


@dataclass(frozen=True)
class SplitConfig:
    train_ratio: float = 0.8
    validation_ratio: float = 0.1
    test_ratio: float = 0.1
    seed: str = "default"
    text_fields: tuple[str, ...] = ("text",)

    def __post_init__(self) -> None:
        ratios = (self.train_ratio, self.validation_ratio, self.test_ratio)
        if any(r < 0 for r in ratios) or sum(ratios) <= 0:
            raise ValueError("split ratios must be non-negative and have a positive total")
        if abs(sum(ratios) - 1.0) > 1e-9:
            raise ValueError("split ratios must sum to 1.0")
        if not self.text_fields:
            raise ValueError("at least one text field is required")


@dataclass
class SplitResult:
    splits: Dict[str, List[dict]]
    report: dict
    warnings: List[str] = field(default_factory=list)
