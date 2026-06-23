"""
ai_interface.py
Interface d'accueil pour le module IA d'Emmanuel.
Auteur : Alimath
Projet : Bras Robotique Joueur de Dames
"""

import random
from game_logic import GameBoard, PLAYER_1, PLAYER_2


class AIInterface:
    def __init__(self, player=PLAYER_2):
        self.player = player

    def compute_best_move(self, game):
        raise NotImplementedError("Emmanuel : implemente compute_best_move() !")


class AIPlaceholder(AIInterface):
    """IA temporaire (aleatoire) en attente du module Minimax d'Emmanuel."""

    def __init__(self, player=PLAYER_2):
        super().__init__(player)

    def compute_best_move(self, game):
        legal = game.get_legal_moves(self.player)
        if not legal:
            return None
        return random.choice(legal)
