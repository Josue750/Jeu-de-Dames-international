from .board import Board
from .move import Move
from .pieces import Piece


class MoveGenerator:
    """Génère les coups légaux et applique les mouvements selon les règles du jeu."""

    def __init__(self, board: Board):
        self.board = board
        self.size = board.size

    def get_valid_moves(self, player: int):
        captures = self.generate_captures(player)
        if captures:
            return captures
        return self.generate_moves(player)

    def generate_moves(self, player: int):
        moves = []
        for row, col in self.board.get_all_pieces(player):
            piece = self.board.get_piece(row, col)
            if Piece.is_pawn(piece):
                for dr, dc in Piece.forward_directions(player):
                    new_row = row + dr
                    new_col = col + dc
                    if self.board.is_inside(new_row, new_col) and self.board.get_piece(new_row, new_col) == Piece.EMPTY:
                        moves.append(Move(sequence=[(row, col), (new_row, new_col)], captures=[], piece=piece))
            if Piece.is_queen(piece):
                for dr, dc in Piece.capture_directions():
                    distance = 1
                    while True:
                        new_row = row + dr * distance
                        new_col = col + dc * distance
                        if not self.board.is_inside(new_row, new_col):
                            break
                        if self.board.get_piece(new_row, new_col) != Piece.EMPTY:
                            break
                        moves.append(Move(sequence=[(row, col), (new_row, new_col)], captures=[], piece=piece))
                        distance += 1
        return moves

    def generate_captures(self, player: int):
        candidate_moves = []
        for row, col in self.board.get_all_pieces(player):
            piece = self.board.get_piece(row, col)
            if Piece.is_pawn(piece):
                candidate_moves.extend(self._explore_pawn_captures(row, col, player, self.board.copy(), [(row, col)], []))
            elif Piece.is_queen(piece):
                candidate_moves.extend(self._explore_queen_captures(row, col, player, self.board.copy(), [(row, col)], []))

        if not candidate_moves:
            return []

        max_captures = max(move.capture_count() for move in candidate_moves)
        best_moves = [move for move in candidate_moves if move.capture_count() == max_captures]
        
        # Ordonner les meilleurs coups par valeur matérielle
        best_moves.sort(key=lambda m: self._score_capture(m), reverse=True)
        
        return best_moves
    
    def _score_capture(self, move) -> float:
        """Évalue la valeur d'une capture."""
        score = 0
        for captured_pos in move.captures:
            captured_piece = self.board.get_piece(captured_pos[0], captured_pos[1])
            if Piece.is_queen(captured_piece):
                score += 350
            else:
                score += 100
        return score

    def _explore_pawn_captures(self, row, col, player, board, path, captures):
        sequences = []
        piece = board.get_piece(row, col)
        found_capture = False
        for dr, dc in Piece.capture_directions():
            middle_row = row + dr
            middle_col = col + dc
            landing_row = row + dr * 2
            landing_col = col + dc * 2
            if not board.is_inside(landing_row, landing_col):
                continue
            if board.get_piece(landing_row, landing_col) != Piece.EMPTY:
                continue
            middle_piece = board.get_piece(middle_row, middle_col)
            if not Piece.is_player_piece(middle_piece, 3 - player) or middle_piece == Piece.EMPTY:
                continue
            next_board = board.copy()
            next_board.set_piece(middle_row, middle_col, Piece.EMPTY)
            next_board.set_piece(row, col, Piece.EMPTY)
            next_board.set_piece(landing_row, landing_col, piece)
            new_path = path + [(landing_row, landing_col)]
            new_captures = captures + [(middle_row, middle_col)]
            deeper = self._explore_pawn_captures(landing_row, landing_col, player, next_board, new_path, new_captures)
            if deeper:
                sequences.extend(deeper)
            else:
                sequences.append(Move(sequence=new_path, captures=new_captures, piece=piece))
            found_capture = True
        if not found_capture and captures:
            sequences.append(Move(sequence=path, captures=captures, piece=piece))
        return sequences

    def _explore_queen_captures(self, row, col, player, board, path, captures):
        sequences = []
        piece = board.get_piece(row, col)
        found_capture = False
        for dr, dc in Piece.capture_directions():
            scan_row, scan_col = row + dr, col + dc
            while board.is_inside(scan_row, scan_col) and board.get_piece(scan_row, scan_col) == Piece.EMPTY:
                scan_row += dr
                scan_col += dc
            if not board.is_inside(scan_row, scan_col):
                continue
            target_value = board.get_piece(scan_row, scan_col)
            if not Piece.is_player_piece(target_value, 3 - player):
                continue
            landing_row = scan_row + dr
            landing_col = scan_col + dc
            while board.is_inside(landing_row, landing_col):
                if board.get_piece(landing_row, landing_col) != Piece.EMPTY:
                    break
                next_board = board.copy()
                next_board.set_piece(scan_row, scan_col, Piece.EMPTY)
                next_board.set_piece(row, col, Piece.EMPTY)
                next_board.set_piece(landing_row, landing_col, piece)
                new_path = path + [(landing_row, landing_col)]
                new_captures = captures + [(scan_row, scan_col)]
                deeper = self._explore_queen_captures(landing_row, landing_col, player, next_board, new_path, new_captures)
                if deeper:
                    sequences.extend(deeper)
                else:
                    sequences.append(Move(sequence=new_path, captures=new_captures, piece=piece))
                found_capture = True
                landing_row += dr
                landing_col += dc
        if not found_capture and captures:
            sequences.append(Move(sequence=path, captures=captures, piece=piece))
        return sequences

    def apply_move(self, move: Move):
        start = move.start_position()
        end = move.last_position()
        piece = self.board.get_piece(*start)
        record = {"start": start, "end": end, "piece": piece, "removed": []}
        for captured in move.captures:
            captured_value = self.board.get_piece(*captured)
            self.board.set_piece(captured[0], captured[1], Piece.EMPTY)
            record["removed"].append((captured, captured_value))
        self.board.set_piece(start[0], start[1], Piece.EMPTY)
        if Piece.is_pawn(piece) and end[0] == Piece.promotion_row(Piece.owner(piece), self.size):
            piece = Piece.promote(piece)
        self.board.set_piece(end[0], end[1], piece)
        return record

    def undo_move(self, record):
        self.board.set_piece(record["end"][0], record["end"][1], Piece.EMPTY)
        self.board.set_piece(record["start"][0], record["start"][1], record["piece"])
        for position, value in record.get("removed", []):
            self.board.set_piece(position[0], position[1], value)
