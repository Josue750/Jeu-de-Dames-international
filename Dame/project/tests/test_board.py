import unittest

from project.core.analyzer import DamierAnalyzer
from project.core.board import Board


class TestBoard(unittest.TestCase):
    def test_analyzer_counts(self):
        analyzer = DamierAnalyzer(8)
        self.assertEqual(analyzer.size, 8)
        self.assertEqual(analyzer.total_cells, 64)
        self.assertEqual(analyzer.rows_with_pieces, 3)
        self.assertEqual(analyzer.pieces_per_player, 12)

    def test_board_initial_positions(self):
        board = Board(10)
        self.assertEqual(board.count_pieces(1), 20)
        self.assertEqual(board.count_pieces(2), 20)
        self.assertEqual(board.total_piece_count(), 40)
