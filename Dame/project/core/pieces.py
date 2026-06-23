class Piece:
    """Représente les types de pièces et les opérations utilitaires."""

    EMPTY = 0
    PAWN_1 = 1
    PAWN_2 = 2
    QUEEN_1 = 3
    QUEEN_2 = 4

    @staticmethod
    def owner(value: int) -> int:
        if value in (Piece.PAWN_1, Piece.QUEEN_1):
            return 1
        if value in (Piece.PAWN_2, Piece.QUEEN_2):
            return 2
        return 0

    @staticmethod
    def is_pawn(value: int) -> bool:
        return value in (Piece.PAWN_1, Piece.PAWN_2)

    @staticmethod
    def is_queen(value: int) -> bool:
        return value in (Piece.QUEEN_1, Piece.QUEEN_2)

    @staticmethod
    def is_player_piece(value: int, player: int) -> bool:
        return Piece.owner(value) == player

    @staticmethod
    def promote(value: int) -> int:
        if value == Piece.PAWN_1:
            return Piece.QUEEN_1
        if value == Piece.PAWN_2:
            return Piece.QUEEN_2
        return value

    @staticmethod
    def promotion_row(player: int, size: int) -> int:
        return 0 if player == 1 else size - 1

    @staticmethod
    def forward_directions(player: int):
        if player == 1:
            return [(-1, -1), (-1, 1)]
        return [(1, -1), (1, 1)]

    @staticmethod
    def capture_directions():
        return [(-1, -1), (-1, 1), (1, -1), (1, 1)]
