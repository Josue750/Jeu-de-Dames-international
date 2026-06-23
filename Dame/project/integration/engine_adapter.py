"""Adaptateur entre l'interface graphique et le moteur de dames.

Cette couche est la seule responsable de la communication avec le moteur.
L'interface ne doit plus contenir de logique métier, de validation ou d'IA.
"""

import os
import sys
from copy import deepcopy

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from core.board import Board
    from core.game_rules import GameRules
    from core.move_generator import MoveGenerator
    from core.move import Move
    from ai.ai_player import AIPlayer
    from core.pieces import Piece
except ImportError as exc:
    raise ImportError(
        "Impossible d'importer le moteur de jeu depuis integration/engine_adapter.py. "
        "Vérifiez que le dossier moteur/core et moteur/ai sont accessibles."
    ) from exc


class EngineAdapter:
    """Point d'accès unique entre l'interface et le moteur."""

    def __init__(self, size: int = 8, ai_depth: int = 3, human_player: int = 1, ai_player: int = 2):
        self.size = size
        self.ai_depth = ai_depth
        self.human_player = human_player
        self.ai_player = ai_player
        self._initialize_engine()

    def _initialize_engine(self):
        self.board = Board(self.size)
        self.rules = GameRules(self.board)
        self.current_player = self.human_player
        self.turn_number = 1
        self.ai = AIPlayer(self.ai_player, depth=self.ai_depth)

    def new_game(self, size: int = None, ai_depth: int = None):
        if size is not None:
            self.size = size
        if ai_depth is not None:
            self.ai_depth = ai_depth
        self._initialize_engine()

    def reset_game(self):
        self.new_game(size=self.size, ai_depth=self.ai_depth)

    def get_board(self):
        return deepcopy(self.board.grid)

    def get_board_size(self):
        return self.board.size

    def get_current_player(self):
        return self.current_player

    def get_turn_number(self):
        return self.turn_number

    def get_piece_at(self, row: int, col: int):
        return self.board.get_piece(row, col)

    def is_player_piece(self, row: int, col: int, player: int):
        return Piece.is_player_piece(self.get_piece_at(row, col), player)

    def is_queen_piece(self, piece_value: int):
        return Piece.is_queen(piece_value)

    def get_legal_moves(self, position=None):
        moves = MoveGenerator(self.board).get_valid_moves(self.current_player)
        move_dicts = [self._move_to_dict(move) for move in moves]
        if position is not None:
            row, col = position
            move_dicts = [move for move in move_dicts if move["from"] == [row, col]]
        return move_dicts

    def make_move(self, move):
        if self.is_game_over():
            return False
        move_obj = self._parse_move(move)
        legal_moves = MoveGenerator(self.board).get_valid_moves(self.current_player)
        if not any(self._moves_equal(move_obj, legal) for legal in legal_moves):
            return False
        MoveGenerator(self.board).apply_move(move_obj)
        self._switch_player()
        return True

    def get_score(self):
        return {
            1: self.board.count_pieces(1),
            2: self.board.count_pieces(2),
        }

    def is_game_over(self):
        return self.rules.is_game_over(self.current_player)

    def get_winner(self):
        return self.rules.get_winner(self.current_player)

    def ai_move(self, player=None):
        if self.is_game_over():
            return None

        if player is None:
            player = self.current_player

        ai = AIPlayer(player, depth=self.ai_depth)
        move_obj = ai.choose_move(self.board)
        if move_obj is None:
            return None

        MoveGenerator(self.board).apply_move(move_obj)
        self._switch_player()
        return self._move_to_dict(move_obj)

    def _parse_move(self, move):
        if isinstance(move, Move):
            return move
        if isinstance(move, dict):
            if "sequence" in move and move["sequence"]:
                sequence = [tuple(pos) for pos in move["sequence"]]
                captures = [tuple(pos) for pos in move.get("captured", move.get("captures", []))]
                return Move(sequence=sequence, captures=captures, piece=move.get("piece", 0))
            if "from" in move and "to" in move:
                return Move(sequence=[tuple(move["from"]), tuple(move["to"])], captures=[tuple(pos) for pos in move.get("captured", move.get("captures", []))], piece=move.get("piece", 0))
        raise ValueError("Move non valide. Attendu dict avec 'from' et 'to' ou 'sequence'.")

    def _move_to_dict(self, move):
        return {
            "from": list(move.start_position()),
            "to": list(move.last_position()),
            "sequence": [list(pos) for pos in move.sequence],
            "captured": [list(pos) for pos in move.captures],
            "piece": move.piece,
        }

    @staticmethod
    def _moves_equal(move_a, move_b):
        return list(move_a.sequence) == list(move_b.sequence)

    def _switch_player(self):
        self.current_player = 1 if self.current_player == 2 else 2
        if self.current_player == self.human_player:
            self.turn_number += 1
