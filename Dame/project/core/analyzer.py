class DamierAnalyzer:
    """Analyse les propriétés d'un damier de dames de taille dynamique."""

    def __init__(self, size: int):
        self.size = size
        self.total_cells = size * size
        self.dark_squares = self._compute_dark_squares()
        self.rows_with_pieces = (size // 2) - 1
        self.pieces_per_player = (size // 2) * ((size // 2) - 1)

    def _compute_dark_squares(self):
        squares = []
        for row in range(self.size):
            for col in range(self.size):
                if self.is_dark_square(row, col):
                    squares.append((row, col))
        return squares

    def is_dark_square(self, row: int, col: int) -> bool:
        return (row + col) % 2 == 1

    def __repr__(self):
        return (
            f"DamierAnalyzer(size={self.size}, total_cells={self.total_cells}, "
            f"dark_squares={len(self.dark_squares)}, rows_with_pieces={self.rows_with_pieces}, "
            f"pieces_per_player={self.pieces_per_player})"
        )
