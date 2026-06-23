import re
from typing import List, Optional, Tuple

Position = Tuple[int, int]


def render_board(board) -> str:
    letters = " ".join(chr(ord("a") + col) for col in range(board.size))
    lines = [f"  {letters}"]
    for row in range(board.size):
        rank = board.size - row
        row_values = []
        for col in range(board.size):
            value = board.get_piece(row, col)
            if value == 0:
                row_values.append(".")
            elif value == 1:
                row_values.append("x")
            elif value == 2:
                row_values.append("o")
            elif value == 3:
                row_values.append("X")
            elif value == 4:
                row_values.append("O")
            else:
                row_values.append("?")
        lines.append(f"{rank:2} {' '.join(row_values)}")
    return "\n".join(lines)


def parse_move_input(raw: str, size: int) -> List[Position]:
    raw = raw.strip().replace("->", " ").replace("=>", " ").replace("-", " ")
    tokens = re.findall(r"\([^)]+\)|[a-zA-Z]\d+", raw)
    moves = []
    for token in tokens:
        position = _token_to_position(token, size)
        if position is not None:
            moves.append(position)
    return moves


def _token_to_position(token: str, size: int) -> Optional[Position]:
    token = token.strip()
    if token.startswith("(") and token.endswith(")"):
        content = token[1:-1].strip()
        parts = [part.strip() for part in content.split(",")]
        if len(parts) != 2:
            return None
        if not parts[0].isdigit() or not parts[1].isdigit():
            return None
        row = int(parts[0])
        col = int(parts[1])
        if 0 <= row < size and 0 <= col < size:
            return row, col
        return None
    match = re.fullmatch(r"([a-zA-Z])(\d+)", token)
    if not match:
        return None
    col = ord(match.group(1).lower()) - ord("a")
    rank = int(match.group(2))
    row = size - rank
    if 0 <= row < size and 0 <= col < size:
        return row, col
    return None
