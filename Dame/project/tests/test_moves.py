import unittest

from project.core.board import Board
from project.core.move_generator import MoveGenerator
from project.core.pieces import Piece


class TestMoves(unittest.TestCase):
    def test_simple_pawn_moves(self):
        board = Board(8)
        board.grid = [[Piece.EMPTY for _ in range(8)] for _ in range(8)]
        board.set_piece(5, 2, Piece.PAWN_1)
        moves = MoveGenerator(board).get_valid_moves(1)
        self.assertTrue(any(move.sequence == [(5, 2), (4, 1)] for move in moves))
        self.assertTrue(any(move.sequence == [(5, 2), (4, 3)] for move in moves))
