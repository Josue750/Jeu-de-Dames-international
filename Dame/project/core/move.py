from dataclasses import dataclass, field
from typing import List, Tuple

Position = Tuple[int, int]


@dataclass
class Move:
    sequence: List[Position]
    captures: List[Position] = field(default_factory=list)
    piece: int = 0

    def capture_count(self) -> int:
        return len(self.captures)

    def last_position(self) -> Position:
        return self.sequence[-1]

    def start_position(self) -> Position:
        return self.sequence[0]
