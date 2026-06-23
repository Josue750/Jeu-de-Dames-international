import unittest

from project.core.board import Board
from project.core.move_generator import MoveGenerator
from project.core.pieces import Piece


class TestPromotion(unittest.TestCase):
    def test_pawn_promotion_to_queen(self):
        board = Board(8)
        board.grid = [[Piece.EMPTY for _ in range(8)] for _ in range(8)]
        board.set_piece(1, 2, Piece.PAWN_1)
        move = MoveGenerator(board).generate_moves(1)[0]
        self.assertEqual(move.sequence, [(1, 2), (0, 1)])
        MoveGenerator(board).apply_move(move)
        self.assertEqual(board.get_piece(0, 1), Piece.QUEEN_1)
