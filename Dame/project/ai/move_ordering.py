"""
Move Ordering - Ordonnancement intelligent des coups pour optimiser Alpha-Beta.
Les bons coups testés en premier = meilleure élagage.
"""
from typing import List

class MoveOrdering:
    """Ordonne les coups pour maximiser l'efficacité Alpha-Beta."""
    
    def __init__(self):
        self.killer_moves = {}  # (depth, player) -> [move1, move2]
        self.history = {}       # move -> count (combien de fois c'était bon)
    
    def order_moves(self, moves: List, board, player: int, depth: int, 
                   best_move_from_tt=None) -> List:
        """
        Ordonne les coups par heuristique.
        
        Priorité:
        1. Meilleur coup de la table de transposition
        2. Meilleures captures (captures avec gain)
        3. Promotions
        4. Killer moves
        5. Coups histoire (history heuristic)
        6. Autres coups
        
        Args:
            moves: Liste des coups à ordonner
            board: Plateau de jeu
            player: Joueur actuel
            depth: Profondeur actuelle
            best_move_from_tt: Meilleur coup connu (TT)
            
        Returns:
            Coups ordonnés
        """
        if not moves:
            return moves
        
        scored_moves = []
        
        for move in moves:
            score = 0
            
            # 1. TT best move: priorité maximale
            if best_move_from_tt and move.sequence == best_move_from_tt.sequence:
                score = 1000000
            
            # 2. Captures: scorer par gain matériel
            elif move.capture_count() > 0:
                # Captures de dames: +1000 par dame
                # Captures de pions: +100 par pion
                for captured_pos in move.captures:
                    captured_piece = board.get_piece(captured_pos[0], captured_pos[1])
                    if captured_piece in (3, 4):  # Dame
                        score += 1000
                    else:  # Pion
                        score += 100
                
                # Bonus pour captures multiples
                if move.capture_count() > 1:
                    score += 500
            
            # 3. Promotions: +800
            elif self._is_promotion_move(move, board, player):
                score += 800
            
            # 4. Killer moves: +50
            elif self._is_killer_move(move, depth):
                score += 50
            
            # 5. History heuristic: +1 à +50
            else:
                move_key = (move.start_position(), move.last_position())
                history_count = self.history.get(move_key, 0)
                score += min(history_count, 50)
            
            scored_moves.append((score, move))
        
        # Trier par score décroissant
        scored_moves.sort(key=lambda x: x[0], reverse=True)
        
        return [move for _, move in scored_moves]
    
    def _is_promotion_move(self, move, board, player) -> bool:
        """Vérifie si un coup mène à une promotion."""
        from core.pieces import Piece
        end_row = move.last_position()[0]
        promotion_row = Piece.promotion_row(player, board.size)
        return end_row == promotion_row
    
    def _is_killer_move(self, move, depth) -> bool:
        """Vérifie si c'est un killer move."""
        key = (depth, None)
        if key in self.killer_moves:
            for killer in self.killer_moves[key]:
                if move.sequence == killer.sequence:
                    return True
        return False
    
    def update_killer_move(self, move, depth: int):
        """
        Met à jour les killer moves.
        Garder les 2 meilleurs coups par profondeur.
        """
        key = (depth, None)
        if key not in self.killer_moves:
            self.killer_moves[key] = []
        
        # Vérifier qu'on n'ajoute pas un doublon
        for killer in self.killer_moves[key]:
            if move.sequence == killer.sequence:
                return
        
        self.killer_moves[key].append(move)
        
        # Garder max 2 killer moves par profondeur
        if len(self.killer_moves[key]) > 2:
            self.killer_moves[key] = self.killer_moves[key][-2:]
    
    def update_history(self, move, depth: int, bonus: int = 1):
        """
        Met à jour la history heuristic.
        Plus un coup est bon, plus on le priorizera.
        """
        move_key = (move.start_position(), move.last_position())
        current = self.history.get(move_key, 0)
        # Bonus dépend de la profondeur
        self.history[move_key] = current + (bonus * depth * depth)
    
    def clear_killer_moves(self):
        """Efface les killer moves (entre les coups)."""
        self.killer_moves.clear()
    
    def reset_history(self):
        """Réinitialise la history (optionnel)."""
        # Attention: peut aussi garder l'historique entre les coups
        # self.history.clear()
        pass
