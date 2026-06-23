import unittest

from project.ai.ai_player import AIPlayer
from project.core.board import Board


class TestAI(unittest.TestCase):
    def test_ai_returns_move_on_opening_position(self):
        ai = AIPlayer(player_id=2, depth=1)
        board = Board(8)
        move = ai.choose_move(board)
        self.assertIsNotNone(move)

    def test_minimax_with_simple_position(self):
        ai = AIPlayer(player_id=2, depth=2)
        board = Board(8)
        self.assertIsNotNone(ai.choose_move(board))
