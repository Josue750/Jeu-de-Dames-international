"""
game_logic.py
Logique du jeu de dames 8x8.
Auteur : Alimath
Projet : Bras Robotique Joueur de Dames

Encodage plateau :
    0 = vide
    1 = pion joueur 1 (blanc)
    2 = pion joueur 2 (noir)
    3 = dame joueur 1
    4 = dame joueur 2
"""

import copy
import json

BOARD_SIZE = 8
EMPTY    = 0
P1_PION  = 1
P2_PION  = 2
P1_DAME  = 3
P2_DAME  = 4
PLAYER_1 = 1
PLAYER_2 = 2


class GameBoard:

    def __init__(self):
        self.board = self._init_board()
        self.current_player = PLAYER_1
        self.turn_number = 1
        self.game_status = "en_cours"
        self.winner = None
        self.move_history = []

    def _init_board(self):
        board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if (r + c) % 2 == 1:
                    if r < 3:
                        board[r][c] = P2_PION
                    elif r > 4:
                        board[r][c] = P1_PION
        return board

    def _is_player_piece(self, r, c, player):
        piece = self.board[r][c]
        if player == PLAYER_1:
            return piece in (P1_PION, P1_DAME)
        return piece in (P2_PION, P2_DAME)

    def _is_dame(self, r, c):
        return self.board[r][c] in (P1_DAME, P2_DAME)

    def _is_empty(self, r, c):
        return self.board[r][c] == EMPTY

    def _in_bounds(self, r, c):
        return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

    def _opponent(self, player):
        return PLAYER_2 if player == PLAYER_1 else PLAYER_1

    def _is_opponent_piece(self, r, c, player):
        return self._is_player_piece(r, c, self._opponent(player))

    def _get_directions(self, r, c, player):
        if self._is_dame(r, c):
            return [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        if player == PLAYER_1:
            return [(-1, -1), (-1, 1)]
        return [(1, -1), (1, 1)]

    def get_legal_moves(self, player=None):
        if player is None:
            player = self.current_player
        captures = self._get_all_captures(player)
        if captures:
            return captures
        return self._get_all_simple_moves(player)

    def _get_all_simple_moves(self, player):
        moves = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self._is_player_piece(r, c, player):
                    for dr, dc in self._get_directions(r, c, player):
                        nr, nc = r + dr, c + dc
                        if self._in_bounds(nr, nc) and self._is_empty(nr, nc):
                            moves.append({"from": [r, c], "to": [nr, nc], "captured": None})
        return moves

    def _get_all_captures(self, player):
        captures = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self._is_player_piece(r, c, player):
                    caps = self._get_captures_for_piece(r, c, player, self.board)
                    captures.extend(caps)
        return captures

    def _get_captures_for_piece(self, r, c, player, board):
        captures = []
        dirs = self._get_directions(r, c, player)
        for dr, dc in dirs:
            mr, mc = r + dr, c + dc
            lr, lc = r + 2*dr, c + 2*dc
            if (self._in_bounds(mr, mc) and self._in_bounds(lr, lc)
                    and self._is_opponent_piece(mr, mc, player)
                    and board[lr][lc] == EMPTY):
                captures.append({"from": [r, c], "to": [lr, lc], "captured": [mr, mc]})
        return captures

    def apply_move(self, move):
        if self.game_status != "en_cours":
            return False
        legal = self.get_legal_moves()
        if not self._move_in_list(move, legal):
            return False
        r1, c1 = move["from"]
        r2, c2 = move["to"]
        piece = self.board[r1][c1]
        self.board[r2][c2] = piece
        self.board[r1][c1] = EMPTY
        if move["captured"]:
            rc, cc = move["captured"]
            self.board[rc][cc] = EMPTY
        self._check_promotion(r2, c2)
        self.move_history.append(copy.deepcopy(move))
        self._switch_player()
        self._check_game_over()
        return True

    def _move_in_list(self, move, legal):
        for m in legal:
            if m["from"] == move["from"] and m["to"] == move["to"]:
                return True
        return False

    def _check_promotion(self, r, c):
        piece = self.board[r][c]
        if piece == P1_PION and r == 0:
            self.board[r][c] = P1_DAME
        elif piece == P2_PION and r == BOARD_SIZE - 1:
            self.board[r][c] = P2_DAME

    def _switch_player(self):
        self.current_player = self._opponent(self.current_player)
        if self.current_player == PLAYER_1:
            self.turn_number += 1

    def _check_game_over(self):
        for player in (PLAYER_1, PLAYER_2):
            if not self.get_legal_moves(player):
                self.game_status = "termine"
                self.winner = self._opponent(player)
                return
        p1 = sum(1 for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)
                 if self.board[r][c] in (P1_PION, P1_DAME))
        p2 = sum(1 for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)
                 if self.board[r][c] in (P2_PION, P2_DAME))
        if p1 == 0:
            self.game_status = "termine"
            self.winner = PLAYER_2
        elif p2 == 0:
            self.game_status = "termine"
            self.winner = PLAYER_1

    def is_game_over(self):
        return self.game_status == "termine"

    def to_json(self):
        return {
            "board_state": self.board,
            "current_player": self.current_player,
            "turn_number": self.turn_number,
            "game_status": self.game_status,
            "winner": self.winner,
            "move_history": self.move_history
        }

    def to_json_string(self):
        return json.dumps(self.to_json(), indent=2, ensure_ascii=False)

    def count_pieces(self, player):
        if player == PLAYER_1:
            return sum(1 for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)
                       if self.board[r][c] in (P1_PION, P1_DAME))
        return sum(1 for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)
                   if self.board[r][c] in (P2_PION, P2_DAME))
