from .extract import extract_turn
from .models import CurationReport, Turn
from .normalize import find_conflicts, merge_duplicates


def curate(turns: list[Turn]) -> CurationReport:
    candidates = []
    ignored = 0
    for turn in turns:
        extracted = extract_turn(turn)
        if not extracted:
            ignored += 1
        candidates.extend(extracted)
    memories = merge_duplicates(candidates)
    return CurationReport(memories, find_conflicts(memories), ignored)
