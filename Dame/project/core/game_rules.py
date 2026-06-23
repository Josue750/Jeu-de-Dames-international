from .move_generator import MoveGenerator


class GameRules:
    """Fournit les règles de fin de partie et les vérifications de validité."""

    def __init__(self, board):
        self.board = board

    def has_legal_move(self, player: int) -> bool:
        return bool(MoveGenerator(self.board).get_valid_moves(player))

    def is_game_over(self, current_player: int) -> bool:
        opponent = 1 if current_player == 2 else 2
        if self.board.count_pieces(opponent) == 0:
            return True
        if not self.has_legal_move(current_player):
            return True
        return False

    def get_winner(self, current_player: int):
        opponent = 1 if current_player == 2 else 2
        if self.board.count_pieces(opponent) == 0:
            return current_player
        if not self.has_legal_move(current_player):
            return opponent
        return None
