import unittest

from project.core.board import Board
from project.core.move_generator import MoveGenerator
from project.core.pieces import Piece


class TestCapture(unittest.TestCase):
    def test_simple_capture_removes_piece(self):
        board = Board(8)
        board.grid = [[Piece.EMPTY for _ in range(8)] for _ in range(8)]
        board.set_piece(4, 1, Piece.PAWN_1)
        board.set_piece(3, 2, Piece.PAWN_2)
        moves = MoveGenerator(board).get_valid_moves(1)
        self.assertTrue(moves)
        move = moves[0]
        self.assertEqual(move.captures, [(3, 2)])
        MoveGenerator(board).apply_move(move)
        self.assertEqual(board.get_piece(3, 2), Piece.EMPTY)

    def test_multiple_capture_sequence(self):
        board = Board(8)
        board.grid = [[Piece.EMPTY for _ in range(8)] for _ in range(8)]
        board.set_piece(5, 2, Piece.PAWN_1)
        board.set_piece(4, 3, Piece.PAWN_2)
        board.set_piece(2, 5, Piece.PAWN_2)
        moves = MoveGenerator(board).get_valid_moves(1)
        self.assertTrue(any(move.capture_count() == 2 for move in moves))
