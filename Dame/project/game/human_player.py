from .player import Player
from ..core.move_generator import MoveGenerator
from ..utils.display import parse_move_input


class HumanPlayer(Player):
    """Gère l'interaction utilisateur et la saisie de coups."""

    def choose_move(self, board):
        valid_moves = MoveGenerator(board).get_valid_moves(self.player_id)
        if not valid_moves:
            return None

        raw_input = input(f"Joueur {self.player_id} > ").strip()
        tokens = parse_move_input(raw_input, board.size)
        if len(tokens) < 2:
            print("Entrée invalide. Exemple : b6 a5 ou b6-c5.")
            return None

        for move in valid_moves:
            if move.sequence == tokens:
                return move

        print("Coup invalide ou non autorisé. Vérifiez la capture obligatoire et la prise majoritaire.")
        return None
