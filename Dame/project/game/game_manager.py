from ..config.settings import DEFAULT_DEPTH
from ..core.analyzer import DamierAnalyzer
from ..core.board import Board
from ..core.game_rules import GameRules
from ..core.move_generator import MoveGenerator
from ..game.human_player import HumanPlayer
from ..ai.ai_player import AIPlayer
from ..utils.display import render_board


class GameManager:
    """Gère la boucle principale du jeu humain contre IA."""

    def __init__(self, size: int = 8, ai_depth: int = DEFAULT_DEPTH):
        self.analyzer = DamierAnalyzer(size)
        self.board = Board(size, analyzer=self.analyzer)
        self.rules = GameRules(self.board)
        self.current_player = 1
        self.human = HumanPlayer(1)
        self.ai = AIPlayer(2, ai_depth)

    def run(self):
        print("Jeu de dames - Humain vs IA")
        print(f"Damier {self.board.size}x{self.board.size}, pions par joueur = {self.analyzer.pieces_per_player}")
        while True:
            print(render_board(self.board))
            if self.rules.is_game_over(self.current_player):
                winner = self.rules.get_winner(self.current_player)
                if winner:
                    print(f"Fin de partie : joueur {winner} gagne !")
                else:
                    print("Fin de partie : match nul.")
                break

            if self.current_player == self.ai.player_id:
                print("IA réfléchit...")
                move = self.ai.choose_move(self.board)
                if move is None:
                    print("IA n'a aucun coup légal.")
                    break
                print(f"IA joue : {self._format_move(move)}")
            else:
                move = self.human.choose_move(self.board)
                if move is None:
                    continue

            MoveGenerator(self.board).apply_move(move)
            self.current_player = 1 if self.current_player == 2 else 2

    def _format_move(self, move):
        return " -> ".join(self._position_to_token(r, c) for r, c in move.sequence)

    def _position_to_token(self, row, col):
        letter = chr(ord("a") + col)
        rank = self.board.size - row
        return f"{letter}{rank}"
