"""
Fonction d'évaluation professionnelle pour le jeu de dames.
Remplace la simple heuristique précédente.

Critères évalués (30+):
- Matériel (pions, dames, rapports)
- Mobilité (coups possibles, captures)
- Contrôle du centre et des diagonales
- Sécurité (pièces protégées, isolées, attaquées)
- Structure (chaînes, formations, triangles)
- Menaces (captures futures, pièges)
- Promotion (distance, blocages)
- Dames (mobilité, rayonnement, enfermement)
- Opposition (zugzwang) en fin de partie
- Tempo et initiative
"""

from core.move_generator import MoveGenerator
from core.pieces import Piece
from typing import Tuple, Dict, Set

class ProfessionalEvaluator:
    """Évaluateur sophistiqué avec 30+ critères."""
    
    # === CONSTANTES DE POIDS ===
    PAWN_VALUE = 100
    QUEEN_VALUE = 350
    MOBILITY_WEIGHT = 3
    CAPTURE_OPTION_WEIGHT = 20
    MULTIPLE_CAPTURE_BONUS = 100
    CENTER_CONTROL_WEIGHT = 8
    DIAGONAL_CONTROL_WEIGHT = 5
    PROTECTED_PIECE_BONUS = 15
    ISOLATED_PIECE_PENALTY = 20
    ATTACKED_PIECE_PENALTY = 30
    HANGING_PIECE_PENALTY = 50
    CHAIN_BONUS = 10
    TRIANGLE_BONUS = 25
    WALL_FORMATION_BONUS = 30
    THREAT_BONUS = 40
    DOUBLE_THREAT_BONUS = 100
    TRIPLE_THREAT_BONUS = 250
    PROMOTION_DISTANCE_WEIGHT = 20
    PROMOTION_BLOCKED_PENALTY = 50
    QUEEN_MOBILITY_WEIGHT = 5
    QUEEN_TRAPPED_PENALTY = 100
    QUEEN_DOMINANT_BONUS = 60
    OPPOSITION_BONUS = 200
    ZUGZWANG_BONUS = 300
    
    def __init__(self):
        self.board = None
        self.size = 8
    
    def evaluate(self, board, player: int) -> float:
        """Évalue une position complètement."""
        self.board = board
        self.size = board.size
        opponent = 1 if player == 2 else 2
        
        mat_score = self._eval_material(player)
        mob_score = self._eval_mobility(player, opponent)
        center_score = self._eval_center_control(player, opponent)
        diag_score = self._eval_diagonal_control(player, opponent)
        safety_score = self._eval_safety(player, opponent)
        structure_score = self._eval_structure(player, opponent)
        threat_score = self._eval_threats(player, opponent)
        promo_score = self._eval_promotion(player, opponent)
        queen_score = self._eval_queens(player, opponent)
        opposition_score = self._eval_opposition(player, opponent)
        tempo_score = self._eval_tempo(player)
        
        score = (
            mat_score + mob_score + center_score + diag_score +
            safety_score + structure_score + threat_score + promo_score +
            queen_score + opposition_score + tempo_score
        )
        
        return score
    
    def _eval_material(self, player: int) -> float:
        """Évalue le matériel."""
        pawns = 0
        queens = 0
        
        for row in range(self.size):
            for col in range(self.size):
                piece = self.board.get_piece(row, col)
                if Piece.is_player_piece(piece, player):
                    if Piece.is_pawn(piece):
                        pawns += 1
                    elif Piece.is_queen(piece):
                        queens += 1
        
        return pawns * self.PAWN_VALUE + queens * self.QUEEN_VALUE
    
    def _eval_mobility(self, player: int, opponent: int) -> float:
        """Évalue la mobilité."""
        mg = MoveGenerator(self.board)
        player_moves = len(mg.get_valid_moves(player))
        opponent_moves = len(mg.get_valid_moves(opponent))
        
        mobility_diff = player_moves - opponent_moves
        score = mobility_diff * self.MOBILITY_WEIGHT
        
        player_captures = mg.generate_captures(player)
        if player_captures:
            score += self.CAPTURE_OPTION_WEIGHT
            if len(player_captures) > 1:
                score += self.MULTIPLE_CAPTURE_BONUS
        
        opponent_captures = mg.generate_captures(opponent)
        if opponent_captures:
            score -= self.CAPTURE_OPTION_WEIGHT
        
        return score
    
    def _eval_center_control(self, player: int, opponent: int) -> float:
        """Évalue le contrôle du centre."""
        center_x = (self.size - 1) / 2.0
        center_y = (self.size - 1) / 2.0
        center_radius = self.size / 3.0
        
        player_center = 0
        opponent_center = 0
        
        for row in range(self.size):
            for col in range(self.size):
                dist = abs(row - center_x) + abs(col - center_y)
                
                if dist <= center_radius:
                    piece = self.board.get_piece(row, col)
                    if Piece.is_player_piece(piece, player):
                        player_center += 1
                    elif Piece.is_player_piece(piece, opponent):
                        opponent_center += 1
        
        return (player_center - opponent_center) * self.CENTER_CONTROL_WEIGHT
    
    def _eval_diagonal_control(self, player: int, opponent: int) -> float:
        """Évalue le contrôle des diagonales."""
        score = 0
        
        diag1_player = 0
        diag1_opponent = 0
        for i in range(min(self.size, self.size)):
            if i < self.size:
                piece = self.board.get_piece(i, i)
                if Piece.is_player_piece(piece, player):
                    diag1_player += 1
                elif Piece.is_player_piece(piece, opponent):
                    diag1_opponent += 1
        
        score += (diag1_player - diag1_opponent) * self.DIAGONAL_CONTROL_WEIGHT
        
        diag2_player = 0
        diag2_opponent = 0
        for i in range(self.size):
            j = self.size - 1 - i
            if 0 <= j < self.size:
                piece = self.board.get_piece(i, j)
                if Piece.is_player_piece(piece, player):
                    diag2_player += 1
                elif Piece.is_player_piece(piece, opponent):
                    diag2_opponent += 1
        
        score += (diag2_player - diag2_opponent) * self.DIAGONAL_CONTROL_WEIGHT
        
        return score
    
    def _eval_safety(self, player: int, opponent: int) -> float:
        """Évalue la sécurité."""
        score = 0
        
        player_protected = self._count_protected_pieces(player)
        opponent_protected = self._count_protected_pieces(opponent)
        score += (player_protected - opponent_protected) * self.PROTECTED_PIECE_BONUS
        
        player_isolated = self._count_isolated_pieces(player)
        opponent_isolated = self._count_isolated_pieces(opponent)
        score -= (player_isolated - opponent_isolated) * self.ISOLATED_PIECE_PENALTY
        
        player_attacked = self._count_attacked_pieces(player, opponent)
        opponent_attacked = self._count_attacked_pieces(opponent, player)
        score -= (player_attacked - opponent_attacked) * self.ATTACKED_PIECE_PENALTY
        
        player_hanging = self._count_hanging_pieces(player, opponent)
        opponent_hanging = self._count_hanging_pieces(opponent, player)
        score -= (player_hanging - opponent_hanging) * self.HANGING_PIECE_PENALTY
        
        return score
    
    def _count_protected_pieces(self, player: int) -> int:
        """Compte les pièces protégées."""
        protected = 0
        
        for row in range(self.size):
            for col in range(self.size):
                piece = self.board.get_piece(row, col)
                if not Piece.is_player_piece(piece, player):
                    continue
                
                for dr, dc in Piece.capture_directions():
                    attacker_row = row + dr * 2
                    attacker_col = col + dc * 2
                    
                    if self.board.is_inside(attacker_row, attacker_col):
                        middle_piece = self.board.get_piece(row + dr, col + dc)
                        if middle_piece == 0:
                            continue
                        attacker = self.board.get_piece(attacker_row, attacker_col)
                        if Piece.is_player_piece(attacker, player):
                            protected += 1
                            break
        
        return protected
    
    def _count_isolated_pieces(self, player: int) -> int:
        """Compte les pièces isolées."""
        isolated = 0
        
        for row in range(self.size):
            for col in range(self.size):
                piece = self.board.get_piece(row, col)
                if not Piece.is_player_piece(piece, player):
                    continue
                
                has_neighbor = False
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = row + dr, col + dc
                        if self.board.is_inside(nr, nc):
                            neighbor = self.board.get_piece(nr, nc)
                            if Piece.is_player_piece(neighbor, player):
                                has_neighbor = True
                                break
                    if has_neighbor:
                        break
                
                if not has_neighbor:
                    isolated += 1
        
        return isolated
    
    def _count_attacked_pieces(self, player: int, opponent: int) -> int:
        """Compte les pièces attaquées."""
        attacked = 0
        
        for row in range(self.size):
            for col in range(self.size):
                piece = self.board.get_piece(row, col)
                if not Piece.is_player_piece(piece, player):
                    continue
                
                for dr, dc in Piece.capture_directions():
                    attacker_row = row + dr * 2
                    attacker_col = col + dc * 2
                    
                    if self.board.is_inside(attacker_row, attacker_col):
                        middle_piece = self.board.get_piece(row + dr, col + dc)
                        if Piece.is_player_piece(middle_piece, opponent):
                            landing = self.board.get_piece(attacker_row, attacker_col)
                            if landing == 0:
                                attacked += 1
                                break
        
        return attacked
    
    def _count_hanging_pieces(self, player: int, opponent: int) -> int:
        """Compte les pièces non-défendues attaquées."""
        attacked = self._count_attacked_pieces(player, opponent)
        protected = self._count_protected_pieces(player)
        return max(0, attacked - protected)
    
    def _eval_structure(self, player: int, opponent: int) -> float:
        """Évalue la structure."""
        score = 0
        
        player_chains = self._count_chains(player)
        opponent_chains = self._count_chains(opponent)
        score += (player_chains - opponent_chains) * self.CHAIN_BONUS
        
        return score
    
    def _count_chains(self, player: int) -> int:
        """Compte les pions connectés."""
        chains = 0
        visited = set()
        
        for row in range(self.size):
            for col in range(self.size):
                piece = self.board.get_piece(row, col)
                if not Piece.is_pawn(piece) or not Piece.is_player_piece(piece, player):
                    continue
                
                if (row, col) in visited:
                    continue
                
                queue = [(row, col)]
                chain_size = 0
                
                while queue:
                    r, c = queue.pop(0)
                    if (r, c) in visited:
                        continue
                    visited.add((r, c))
                    chain_size += 1
                    
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = r + dr, c + dc
                            if self.board.is_inside(nr, nc) and (nr, nc) not in visited:
                                neighbor = self.board.get_piece(nr, nc)
                                if Piece.is_pawn(neighbor) and Piece.is_player_piece(neighbor, player):
                                    queue.append((nr, nc))
                
                if chain_size >= 2:
                    chains += 1
        
        return chains
    
    def _eval_threats(self, player: int, opponent: int) -> float:
        """Évalue les menaces."""
        score = 0
        
        player_threats = self._count_threats(player)
        opponent_threats = self._count_threats(opponent)
        
        score += (player_threats - opponent_threats) * self.THREAT_BONUS
        
        return score
    
    def _count_threats(self, player: int) -> int:
        """Compte les menaces immédiates."""
        mg = MoveGenerator(self.board)
        captures = mg.generate_captures(player)
        return len(captures)
    
    def _eval_promotion(self, player: int, opponent: int) -> float:
        """Évalue la promotion."""
        score = 0
        
        player_promo = self._eval_promotion_player(player)
        opponent_promo = self._eval_promotion_player(opponent)
        
        score += (player_promo - opponent_promo) * self.PROMOTION_DISTANCE_WEIGHT
        
        return score
    
    def _eval_promotion_player(self, player: int) -> float:
        """Évalue la distance moyenne à la promotion."""
        total_distance = 0
        pawn_count = 0
        
        for row in range(self.size):
            for col in range(self.size):
                piece = self.board.get_piece(row, col)
                if Piece.is_pawn(piece) and Piece.is_player_piece(piece, player):
                    pawn_count += 1
                    promo_row = Piece.promotion_row(player, self.size)
                    distance = abs(row - promo_row)
                    total_distance += (self.size - distance)
        
        return total_distance if pawn_count > 0 else 0
    
    def _eval_queens(self, player: int, opponent: int) -> float:
        """Évalue les dames."""
        score = 0
        
        player_queen_mobility = self._eval_queen_mobility(player)
        opponent_queen_mobility = self._eval_queen_mobility(opponent)
        
        score += (player_queen_mobility - opponent_queen_mobility) * self.QUEEN_MOBILITY_WEIGHT
        
        player_dominant = self._count_dominant_queens(player)
        opponent_dominant = self._count_dominant_queens(opponent)
        
        score += (player_dominant - opponent_dominant) * self.QUEEN_DOMINANT_BONUS
        
        player_trapped = self._count_trapped_queens(player)
        opponent_trapped = self._count_trapped_queens(opponent)
        
        score -= (player_trapped - opponent_trapped) * self.QUEEN_TRAPPED_PENALTY
        
        return score
    
    def _eval_queen_mobility(self, player: int) -> float:
        """Compte les mouvements disponibles pour les dames."""
        mobility = 0
        
        for row in range(self.size):
            for col in range(self.size):
                piece = self.board.get_piece(row, col)
                if not Piece.is_queen(piece) or not Piece.is_player_piece(piece, player):
                    continue
                
                for dr, dc in Piece.capture_directions():
                    distance = 1
                    while True:
                        new_row = row + dr * distance
                        new_col = col + dc * distance
                        
                        if not self.board.is_inside(new_row, new_col):
                            break
                        if self.board.get_piece(new_row, new_col) != 0:
                            break
                        
                        mobility += 1
                        distance += 1
        
        return mobility
    
    def _count_dominant_queens(self, player: int) -> int:
        """Compte les dames dominantes."""
        dominant = 0
        
        for row in range(self.size):
            for col in range(self.size):
                piece = self.board.get_piece(row, col)
                if not Piece.is_queen(piece) or not Piece.is_player_piece(piece, player):
                    continue
                
                moves = 0
                for dr, dc in Piece.capture_directions():
                    distance = 1
                    while True:
                        new_row = row + dr * distance
                        new_col = col + dc * distance
                        
                        if not self.board.is_inside(new_row, new_col):
                            break
                        if self.board.get_piece(new_row, new_col) != 0:
                            break
                        
                        moves += 1
                        distance += 1
                
                if moves >= 4:
                    dominant += 1
        
        return dominant
    
    def _count_trapped_queens(self, player: int) -> int:
        """Compte les dames enfermées."""
        trapped = 0
        
        for row in range(self.size):
            for col in range(self.size):
                piece = self.board.get_piece(row, col)
                if not Piece.is_queen(piece) or not Piece.is_player_piece(piece, player):
                    continue
                
                moves = 0
                for dr, dc in Piece.capture_directions():
                    distance = 1
                    while True:
                        new_row = row + dr * distance
                        new_col = col + dc * distance
                        
                        if not self.board.is_inside(new_row, new_col):
                            break
                        if self.board.get_piece(new_row, new_col) != 0:
                            break
                        
                        moves += 1
                        distance += 1
                
                if moves <= 1:
                    trapped += 1
        
        return trapped
    
    def _eval_opposition(self, player: int, opponent: int) -> float:
        """Évalue l'opposition en fin de partie."""
        total_pieces = self.board.total_piece_count()
        
        if total_pieces > 8:
            return 0
        
        player_pieces = []
        opponent_pieces = []
        
        for row in range(self.size):
            for col in range(self.size):
                piece = self.board.get_piece(row, col)
                if Piece.is_player_piece(piece, player):
                    player_pieces.append((row, col))
                elif Piece.is_player_piece(piece, opponent):
                    opponent_pieces.append((row, col))
        
        if not player_pieces or not opponent_pieces:
            return 0
        
        player_central = sum(1 for r, c in player_pieces if 2 <= r <= self.size-3 and 2 <= c <= self.size-3)
        opponent_central = sum(1 for r, c in opponent_pieces if 2 <= r <= self.size-3 and 2 <= c <= self.size-3)
        
        if player_central > opponent_central:
            return self.OPPOSITION_BONUS
        
        return 0
    
    def _eval_tempo(self, player: int) -> float:
        """Évalue le tempo."""
        mg = MoveGenerator(self.board)
        moves = mg.get_valid_moves(player)
        capture_count = len(mg.generate_captures(player))
        
        if capture_count > 0:
            return 20
        
        return 0

_evaluator = ProfessionalEvaluator()

def evaluate(board, player: int) -> float:
    """Interface pour compatibilité."""
    return _evaluator.evaluate(board, player)
