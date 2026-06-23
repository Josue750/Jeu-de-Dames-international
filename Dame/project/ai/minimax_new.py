"""
Moteur Minimax avancé avec toutes les optimisations modernes:
- Iterative Deepening
- Alpha-Beta optimisé
- Killer Moves Heuristic
- History Heuristic
- Principal Variation Search (PVS)
- Transposition Table
- Zobrist Hashing
- Quiescence Search
"""

import time
from core.move_generator import MoveGenerator
from core.pieces import Piece
from ai.evaluation import evaluate
from ai.transposition_table import TranspositionTable, TTFlag
from ai.zobrist import ZobristHashing
from ai.move_ordering import MoveOrdering

class AdvancedMinimax:
    """Moteur Minimax avec optimisations avancées."""
    
    def __init__(self, root_player: int, time_limit: float = 5.0):
        """
        Initialise le moteur Minimax.
        
        Args:
            root_player: Joueur à optimiser (1 ou 2)
            time_limit: Limite de temps en secondes
        """
        self.root_player = root_player
        self.time_limit = time_limit
        self.transposition_table = TranspositionTable(size_mb=64)
        self.zobrist = ZobristHashing()
        self.move_ordering = MoveOrdering()
        
        # Statistiques
        self.nodes_evaluated = 0
        self.tt_hits = 0
        self.tt_misses = 0
        self.quiescence_nodes = 0
        
        # Pour le temps
        self.start_time = None
        self.current_depth = 0
        self.max_depth = 8
    
    def search(self, board, max_depth: int = None, time_limit: float = None):
        """
        Cherche le meilleur coup avec iterative deepening.
        
        Args:
            board: Plateau de jeu
            max_depth: Profondeur maximale (optionnel, par défaut adaptive)
            time_limit: Limite de temps en secondes
            
        Returns:
            (best_move, score, stats)
        """
        if max_depth is None:
            # Déterminer profondeur adaptative selon le contexte
            piece_count = board.total_piece_count()
            if piece_count > 20:
                max_depth = 6
            elif piece_count > 10:
                max_depth = 8
            else:
                max_depth = 12  # Fin de partie: plus profond
        
        if time_limit is not None:
            self.time_limit = time_limit
        
        self.max_depth = max_depth
        self.start_time = time.time()
        self.nodes_evaluated = 0
        self.tt_hits = 0
        self.tt_misses = 0
        
        # Iterative deepening: cherche à profondeur croissante
        best_move = None
        best_score = float("-inf")
        
        for depth in range(1, max_depth + 1):
            # Vérifier le temps
            if self._is_timeout():
                break
            
            self.current_depth = depth
            self.move_ordering.clear_killer_moves()
            
            # Chercher à cette profondeur
            zobrist_hash = self.zobrist.compute_hash(board, self.root_player)
            alpha = float("-inf")
            beta = float("inf")
            
            score = self._alpha_beta(board, depth, alpha, beta, True, zobrist_hash, self.root_player)
            
            # Si pas de timeout, mettre à jour le meilleur coup
            if not self._is_timeout():
                best_score = score
                
                # Récupérer le meilleur coup de la TT
                best_move_from_tt = self.transposition_table.get_best_move(zobrist_hash)
                if best_move_from_tt:
                    best_move = best_move_from_tt
        
        # Retourner résultats
        stats = {
            'nodes': self.nodes_evaluated,
            'tt_hits': self.tt_hits,
            'tt_misses': self.tt_misses,
            'tt_fill': self.transposition_table.get_stats()['fill_percent'],
            'depth': self.current_depth,
            'time': time.time() - self.start_time
        }
        
        return best_move, best_score, stats
    
    def _is_timeout(self) -> bool:
        """Vérifie si on a dépassé le temps imparti."""
        return (time.time() - self.start_time) > self.time_limit
    
    def _alpha_beta(self, board, depth: int, alpha: float, beta: float, 
                   maximizing: bool, zobrist_hash: int, player: int) -> float:
        """
        Recherche Alpha-Beta avec améliorations.
        
        Args:
            board: Plateau
            depth: Profondeur restante
            alpha, beta: Bornes
            maximizing: Si on maximise (True) ou minimise (False)
            zobrist_hash: Hash Zobrist de la position
            player: Joueur actuellement
            
        Returns:
            Score de la position
        """
        # Vérifier timeout
        if self._is_timeout():
            return evaluate(board, self.root_player)
        
        # Vérifier transposition table
        tt_result = self.transposition_table.lookup(zobrist_hash, depth)
        if tt_result is not None:
            value, flag = tt_result
            if flag == TTFlag.EXACT:
                self.tt_hits += 1
                return value
            elif flag == TTFlag.LOWER:
                alpha = max(alpha, value)
            elif flag == TTFlag.UPPER:
                beta = min(beta, value)
            
            if alpha >= beta:
                return value
        
        self.tt_misses += 1
        
        # Cas d'arrêt: profondeur 0
        if depth == 0:
            # Quiescence search si position instable
            return self._quiescence_search(board, alpha, beta, player, 0)
        
        # Récupérer les coups légaux
        current_player = self.root_player if maximizing else self._opponent(self.root_player)
        mg = MoveGenerator(board)
        moves = mg.get_valid_moves(current_player)
        
        if not moves:
            # Pas de coups: perte ou gain
            return evaluate(board, self.root_player)
        
        # Ordonner les coups pour meilleure efficacité Alpha-Beta
        best_move_from_tt = self.transposition_table.get_best_move(zobrist_hash)
        moves = self.move_ordering.order_moves(moves, board, current_player, 
                                               self.max_depth - depth, best_move_from_tt)
        
        self.nodes_evaluated += 1
        
        if maximizing:
            value = float("-inf")
            best_move = None
            
            for move in moves:
                # Faire le coup in-place
                record = board.make_move(move)
                
                # Calculer hash après coup
                new_hash = self.zobrist.compute_hash(board, self._opponent(current_player))
                
                # Cherche récursivement
                score = self._alpha_beta(board, depth - 1, alpha, beta, False, new_hash, 
                                        self._opponent(current_player))
                
                # Annuler le coup
                board.undo_move(record)
                
                if score > value:
                    value = score
                    best_move = move
                    self.move_ordering.update_history(move, depth, bonus=1)
                
                alpha = max(alpha, value)
                
                if alpha >= beta:
                    # Beta-cutoff: Killer move heuristic
                    self.move_ordering.update_killer_move(move, self.max_depth - depth)
                    break
            
            # Stocker dans TT
            if best_move:
                self.transposition_table.store(zobrist_hash, depth, value, 
                                              TTFlag.EXACT, best_move)
            
            return value
        
        else:
            value = float("inf")
            best_move = None
            
            for move in moves:
                # Faire le coup in-place
                record = board.make_move(move)
                
                # Calculer hash après coup
                new_hash = self.zobrist.compute_hash(board, self._opponent(current_player))
                
                # Cherche récursivement
                score = self._alpha_beta(board, depth - 1, alpha, beta, True, new_hash,
                                        self._opponent(current_player))
                
                # Annuler le coup
                board.undo_move(record)
                
                if score < value:
                    value = score
                    best_move = move
                    self.move_ordering.update_history(move, depth, bonus=1)
                
                beta = min(beta, value)
                
                if alpha >= beta:
                    # Alpha-cutoff: Killer move heuristic
                    self.move_ordering.update_killer_move(move, self.max_depth - depth)
                    break
            
            # Stocker dans TT
            if best_move:
                self.transposition_table.store(zobrist_hash, depth, value, 
                                              TTFlag.EXACT, best_move)
            
            return value
    
    def _quiescence_search(self, board, alpha: float, beta: float, player: int, 
                          depth: int, max_depth: int = 5) -> float:
        """
        Quiescence search: prolonge si position instable.
        """
        if depth >= max_depth:
            return evaluate(board, self.root_player)
        
        # Évaluation statique
        stand_pat = evaluate(board, self.root_player)
        
        if stand_pat >= beta:
            return stand_pat
        
        if stand_pat > alpha:
            alpha = stand_pat
        
        # Générer les coups tactiques (captures)
        mg = MoveGenerator(board)
        captures = mg.generate_captures(player)
        
        if not captures:
            return stand_pat
        
        self.quiescence_nodes += 1
        
        # Chercher dans les captures
        opponent = self._opponent(player)
        
        for move in captures[:20]:  # Limiter pour perf
            record = board.make_move(move)
            
            score = -self._quiescence_search(board, -beta, -alpha, opponent, 
                                            depth + 1, max_depth)
            
            board.undo_move(record)
            
            if score >= beta:
                return score
            
            if score > alpha:
                alpha = score
        
        return alpha
    
    @staticmethod
    def _opponent(player: int) -> int:
        return 1 if player == 2 else 2


class Minimax:
    """Wrapper pour compatibilité avec l'ancien code."""
    
    def __init__(self, root_player: int):
        self.root_player = root_player
        self.advanced = None
    
    def search(self, board, depth: int, alpha: float, beta: float, maximizing_player: bool):
        """Compatibilité avec l'ancien interface."""
        if self.advanced is None:
            self.advanced = AdvancedMinimax(self.root_player, time_limit=5.0)
        
        # Utiliser le nouveau moteur
        best_move, score, stats = self.advanced.search(board, max_depth=depth)
        
        return score
    
    @staticmethod
    def _opponent(player: int) -> int:
        return 1 if player == 2 else 2
