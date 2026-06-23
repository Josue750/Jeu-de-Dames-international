from copy import deepcopy
from .analyzer import DamierAnalyzer
from .pieces import Piece


class Board:
    """Représente le plateau de dames et initialise les pièces sur les cases sombres."""

    def __init__(self, size: int, analyzer: DamierAnalyzer = None):
        self.size = size
        self.analyzer = analyzer or DamierAnalyzer(size)
        self.grid = [[Piece.EMPTY for _ in range(size)] for _ in range(size)]
        self._initialize_positions()

    def _initialize_positions(self):
        rows = self.analyzer.rows_with_pieces
        for row in range(rows):
            for col in range(self.size):
                if self.analyzer.is_dark_square(row, col):
                    self.grid[row][col] = Piece.PAWN_2
        for row in range(self.size - rows, self.size):
            for col in range(self.size):
                if self.analyzer.is_dark_square(row, col):
                    self.grid[row][col] = Piece.PAWN_1

    def copy(self):
        return deepcopy(self)

    def get_piece(self, row: int, col: int) -> int:
        if 0 <= row < self.size and 0 <= col < self.size:
            return self.grid[row][col]
        return Piece.EMPTY

    def set_piece(self, row: int, col: int, value: int):
        if 0 <= row < self.size and 0 <= col < self.size:
            self.grid[row][col] = value

    def is_inside(self, row: int, col: int) -> bool:
        return 0 <= row < self.size and 0 <= col < self.size

    def get_all_pieces(self, player: int):
        pieces = []
        for row in range(self.size):
            for col in range(self.size):
                if Piece.is_player_piece(self.grid[row][col], player):
                    pieces.append((row, col))
        return pieces

    def count_pieces(self, player: int) -> int:
        return len(self.get_all_pieces(player))

    def total_piece_count(self) -> int:
        return sum(1 for row in self.grid for value in row if value != Piece.EMPTY)
    
    # ============= OPTIMISATIONS: make_move / undo_move (in-place) =============
    
    def make_move(self, move):
        """
        Applique un coup au plateau IN-PLACE (sans copie).
        Retourne un record pour undo_move.
        
        BEAUCOUP plus rapide que copy() + apply_move().
        Utiliser avec undo_move() pour la recherche.
        """
        from .move import Move
        
        start = move.start_position()
        end = move.last_position()
        piece = self.get_piece(start[0], start[1])
        
        record = {
            "start": start,
            "end": end,
            "piece": piece,
            "removed": []
        }
        
        # Enlever les pièces capturées
        for captured_pos in move.captures:
            captured_value = self.get_piece(captured_pos[0], captured_pos[1])
            self.set_piece(captured_pos[0], captured_pos[1], Piece.EMPTY)
            record["removed"].append((captured_pos, captured_value))
        
        # Enlever la pièce de sa position actuelle
        self.set_piece(start[0], start[1], Piece.EMPTY)
        
        # Promotion si applicable
        final_piece = piece
        if Piece.is_pawn(piece) and end[0] == Piece.promotion_row(Piece.owner(piece), self.size):
            final_piece = Piece.promote(piece)
            record["promoted"] = (piece, final_piece)
        
        # Placer la pièce à sa nouvelle position
        self.set_piece(end[0], end[1], final_piece)
        
        return record
    
    def undo_move(self, record):
        """
        Annule un coup appliqué par make_move().
        Restaure l'état exact du plateau.
        """
        # Enlever la pièce de sa position finale
        self.set_piece(record["end"][0], record["end"][1], Piece.EMPTY)
        
        # Restaurer la pièce originale
        self.set_piece(record["start"][0], record["start"][1], record["piece"])
        
        # Restaurer les pièces capturées
        for position, value in record.get("removed", []):
            self.set_piece(position[0], position[1], value)
