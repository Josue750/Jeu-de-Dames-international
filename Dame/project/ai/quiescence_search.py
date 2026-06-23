"""
Quiescence Search - Prolonge la recherche dans les positions instables.
Évite l'effet d'horizon (évaluation à côté d'une capture).
"""

from core.move_generator import MoveGenerator
from core.pieces import Piece

class QuiescenceSearch:
    """Prolonge la recherche tant qu'il y a des tactiques."""
    
    def __init__(self, evaluator, move_generator):
        self.evaluator = evaluator
        self.move_generator = move_generator
    
    def search(self, board, alpha: float, beta: float, player: int, 
               max_depth: int = 20, current_depth: int = 0) -> float:
        """
        Quiescence search: continue à évaluer tant qu'il y a des coups tactiques.
        
        Args:
            board: Plateau
            alpha: Borne alpha
            beta: Borne beta
            player: Joueur pour lequel on évalue
            max_depth: Profondeur max de quiescence
            current_depth: Profondeur courante
            
        Returns:
            Score de la position stable
        """
        # Arrêt si profondeur max atteinte
        if current_depth >= max_depth:
            return self.evaluator.evaluate(board, player)
        
        # Évaluation statique actuelle
        stand_pat = self.evaluator.evaluate(board, player)
        
        # Si c'est catastrophique, pas besoin de continuer
        if stand_pat >= beta:
            return stand_pat
        
        if stand_pat > alpha:
            alpha = stand_pat
        
        # Générer les coups tactiques (captures et promotions)
        tactical_moves = self._get_tactical_moves(board, player)
        
        if not tactical_moves:
            return stand_pat
        
        # Chercher dans les coups tactiques
        opponent = 1 if player == 2 else 2
        
        for move in tactical_moves:
            # Faire le coup
            mg = MoveGenerator(board)
            record = mg.apply_move(move)
            
            # Cherche dans la position après le coup
            score = -self.search(board, -beta, -alpha, opponent, max_depth, 
                                current_depth + 1)
            
            # Annuler le coup
            mg.undo_move(record)
            
            if score >= beta:
                return score
            
            if score > alpha:
                alpha = score
        
        return alpha
    
    def _get_tactical_moves(self, board, player) -> list:
        """Récupère les coups tactiques (captures et promotions)."""
        tactical_moves = []
        
        # D'abord les captures (priorité)
        mg = MoveGenerator(board)
        captures = mg.generate_captures(player)
        tactical_moves.extend(captures)
        
        # Ensuite les promotions
        all_moves = mg.generate_moves(player)
        
        for move in all_moves:
            end_row = move.last_position()[0]
            promotion_row = Piece.promotion_row(player, board.size)
            if end_row == promotion_row:
                tactical_moves.append(move)
        
        return tactical_moves
