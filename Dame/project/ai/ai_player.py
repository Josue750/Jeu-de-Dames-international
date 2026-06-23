"""
Joueur IA avec moteur Minimax avancé et recherche adaptative.
"""

import time
from core.move_generator import MoveGenerator
from ai.minimax import AdvancedMinimax


class AIPlayer:
    """Joueur IA qui choisit des coups en utilisant Minimax avancé."""

    def __init__(self, player_id: int, depth: int = 3, difficulty: str = "expert"):
        """
        Initialise l'IA.
        
        Args:
            player_id: 1 ou 2
            depth: Profondeur (ignorée, adaptative maintenant)
            difficulty: "beginner", "intermediate", "advanced", "expert", "master"
        """
        self.player_id = player_id
        self.difficulty = difficulty
        
        # Configurer selon le niveau de difficulté
        self.time_limits = {
            "beginner": 0.5,      # 500ms
            "intermediate": 1.0,  # 1s
            "advanced": 2.0,      # 2s
            "expert": 4.0,        # 4s
            "master": 8.0         # 8s
        }
        
        self.time_limit = self.time_limits.get(difficulty, 4.0)
        self.minimax = None
        self.move_count = 0
    
    def choose_move(self, board):
        """
        Choisit le meilleur coup pour le joueur.
        
        Utilise un moteur Minimax avancé avec:
        - Iterative Deepening
        - Recherche adaptative selon le nombre de pièces
        - Limite de temps
        - Alpha-Beta optimisé
        - Transposition Table
        - Move Ordering
        """
        valid_moves = MoveGenerator(board).get_valid_moves(self.player_id)
        if not valid_moves:
            return None
        
        # Créer le moteur Minimax si pas encore créé
        if self.minimax is None:
            self.minimax = AdvancedMinimax(self.player_id, time_limit=self.time_limit)
        
        # Mettre à jour la limite de temps selon le contexte
        self.minimax.time_limit = self._get_adaptive_time()
        
        # Chercher le meilleur coup
        start = time.time()
        best_move, score, stats = self.minimax.search(board)
        elapsed = time.time() - start
        
        # Debug: afficher les stats (optionnel)
        # print(f"AI ({self.difficulty}): depth={stats['depth']}, "
        #       f"nodes={stats['nodes']}, time={elapsed:.2f}s, "
        #       f"tt_fill={stats['tt_fill']:.1f}%")
        
        self.move_count += 1
        
        # Fallback si pas de coup trouvé
        if best_move is None:
            best_move = valid_moves[0]
        
        return best_move
    
    def _get_adaptive_time(self) -> float:
        """
        Détermine le temps de réflexion adaptatif.
        
        Plus de temps en fin de partie, moins en ouverture.
        """
        # Pourrait être amélioré en passant le board en paramètre
        # Pour l'instant, utiliser la configuration de difficulté
        return self.time_limit
    
    def reset(self):
        """Réinitialise l'IA (nouvel match)."""
        self.move_count = 0
        if self.minimax:
            self.minimax.transposition_table.clear()

