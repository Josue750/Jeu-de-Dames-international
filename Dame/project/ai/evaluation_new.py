"""
Nouvelle fonction d'évaluation professionnelle pour le jeu de dames.
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
    # Ajuster ces valeurs pour tuner la stratégie
    
    # Matériel
    PAWN_VALUE = 100
    QUEEN_VALUE = 350  # Environ 3.5x un pion (au lieu de 3x)
    
    # Mobilité
    MOBILITY_WEIGHT = 3
    CAPTURE_OPTION_WEIGHT = 20
    MULTIPLE_CAPTURE_BONUS = 100
    
    # Centre et diagonales
    CENTER_CONTROL_WEIGHT = 8
    DIAGONAL_CONTROL_WEIGHT = 5
    
    # Sécurité
    PROTECTED_PIECE_BONUS = 15
    ISOLATED_PIECE_PENALTY = 20
    ATTACKED_PIECE_PENALTY = 30
    HANGING_PIECE_PENALTY = 50
    
    # Structure
    CHAIN_BONUS = 10
    TRIANGLE_BONUS = 25
    WALL_FORMATION_BONUS = 30
    
    # Menaces
    THREAT_BONUS = 40
    DOUBLE_THREAT_BONUS = 100
    TRIPLE_THREAT_BONUS = 250
    
    # Promotion
    PROMOTION_DISTANCE_WEIGHT = 20
    PROMOTION_BLOCKED_PENALTY = 50
    
    # Dames
    QUEEN_MOBILITY_WEIGHT = 5
    QUEEN_TRAPPED_PENALTY = 100
    QUEEN_DOMINANT_BONUS = 60
    
    # Opposition (fin de partie)
    OPPOSITION_BONUS = 200
    ZUGZWANG_BONUS = 300
    
    def __init__(self):
        self.board = None
        self.size = 8
    
    def evaluate(self, board, player: int) -> float:
        """
        Évalue une position complètement.
        
        Args:
            board: Plateau de jeu
            player: Joueur pour lequel on évalue (1 ou 2)
            
        Returns:
            Score en centièmes de pion (100 = 1 pion)
        """
        self.board = board
        self.size = board.size
        opponent = 1 if player == 2 else 2
        
        # Calculer les scores pour chaque critère
        
        # 1. MATÉRIEL
        mat_score = self._eval_material(player)
        
        # 2. MOBILITÉ
        mob_score = self._eval_mobility(player, opponent)
        
        # 3. CENTRE ET DIAGONALES
        center_score = self._eval_center_control(player, opponent)
        diag_score = self._eval_diagonal_control(player, opponent)
        
        # 4. SÉCURITÉ
        safety_score = self._eval_safety(player, opponent)
        
        # 5. STRUCTURE
        structure_score = self._eval_structure(player, opponent)
        
        # 6. MENACES
        threat_score = self._eval_threats(player, opponent)
        
        # 7. PROMOTION
        promo_score = self._eval_promotion(player, opponent)
        
        # 8. DAMES
        queen_score = self._eval_queens(player, opponent)
        
        # 9. OPPOSITION (si fin de partie)
        opposition_score = self._eval_opposition(player, opponent)
        
        # 10. TEMPO
        tempo_score = self._eval_tempo(player)
        
        # === SCORE FINAL ===
        score = (
            mat_score +
            mob_score +
            center_score +
            diag_score +
            safety_score +
            structure_score +
            threat_score +
            promo_score +
            queen_score +
            opposition_score +
            tempo_score
        )
        
        return score
    
    # ============= CRITÈRE 1: MATÉRIEL =============
    def _eval_material(self, player: int) -> float:
        """Évalue simplement le matériel."""
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
    
    # ============= CRITÈRE 2: MOBILITÉ =============
    def _eval_mobility(self, player: int, opponent: int) -> float:
        """Évalue les options de mouvement."""
        mg = MoveGenerator(self.board)
        
        player_moves = mg.get_valid_moves(player)
        opponent_moves = mg.get_valid_moves(opponent)
        
        player_mobility = len(player_moves)
        opponent_mobility = len(opponent_moves)
        
        # Bonus si on a plus de coups que l'adversaire
        mobility_diff = player_mobility - opponent_mobility
        
        score = mobility_diff * self.MOBILITY_WEIGHT
        
        # Bonus si captures possibles
        player_captures = mg.generate_captures(player)
        if player_captures:
            score += self.CAPTURE_OPTION_WEIGHT
            if len(player_captures) > 1:
                score += self.MULTIPLE_CAPTURE_BONUS
        
        # Pénalité si adversaire peut capturer
        opponent_captures = mg.generate_captures(opponent)
        if opponent_captures:
            score -= self.CAPTURE_OPTION_WEIGHT
        
        return score
    
    # ============= CRITÈRE 3: CONTRÔLE DU CENTRE =============
    def _eval_center_control(self, player: int, opponent: int) -> float:
        """Évalue le contrôle du centre."""
        center_x = (self.size - 1) / 2.0
        center_y = (self.size - 1) / 2.0
        center_radius = self.size / 3.0
        
        player_center = 0
        opponent_center = 0
        
        for row in range(self.size):
            for col in range(self.size):
                # Calculer distance au centre
                dist = abs(row - center_x) + abs(col - center_y)
                
                if dist <= center_radius:
                    piece = self.board.get_piece(row, col)
                    if Piece.is_player_piece(piece, player):
                        player_center += 1
                    elif Piece.is_player_piece(piece, opponent):
                        opponent_center += 1
        
        return (player_center - opponent_center) * self.CENTER_CONTROL_WEIGHT
    
    # ============= CRITÈRE 4: CONTRÔLE DES DIAGONALES =============
    def _eval_diagonal_control(self, player: int, opponent: int) -> float:
        """Évalue le contrôle des diagonales importantes."""
        # Les grandes diagonales sont stratégiques
        score = 0
        
        # Diagonale 1: (0,0) -> (size-1, size-1)
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
        
        # Diagonale 2: (0, size-1) -> (size-1, 0)
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
    
    # ============= CRITÈRE 5: SÉCURITÉ =============
    def _eval_safety(self, player: int, opponent: int) -> float:
        """Évalue la sécurité des pièces."""
        score = 0
        
        # Calculer les pièces attaquées/protégées
        player_protected = self._count_protected_pieces(player)
        opponent_protected = self._count_protected_pieces(opponent)
        
        score += (player_protected - opponent_protected) * self.PROTECTED_PIECE_BONUS
        
        # Pièces isolées (dangereuses)
        player_isolated = self._count_isolated_pieces(player)
        opponent_isolated = self._count_isolated_pieces(opponent)
        
        score -= (player_isolated - opponent_isolated) * self.ISOLATED_PIECE_PENALTY
        
        # Pièces attaquées
        player_attacked = self._count_attacked_pieces(player, opponent)
        opponent_attacked = self._count_attacked_pieces(opponent, player)
        
        score -= (player_attacked - opponent_attacked) * self.ATTACKED_PIECE_PENALTY
        
        # Pièces suspendues (attacks non défendues)
        player_hanging = self._count_hanging_pieces(player, opponent)
        opponent_hanging = self._count_hanging_pieces(opponent, player)
        
        score -= (player_hanging - opponent_hanging) * self.HANGING_PIECE_PENALTY
        
        return score
    
    def _count_protected_pieces(self, player: int) -> int:
        """Compte les pièces protégées (défendues par une autre)."""
        protected = 0
        
        for row in range(self.size):
            for col in range(self.size):
                piece = self.board.get_piece(row, col)
                if not Piece.is_player_piece(piece, player):
                    continue
                
                # Vérifier si cette pièce est protégée
                # Chercher une autre pièce du même joueur qui pourrait la prendre
                for dr, dc in Piece.capture_directions():
                    attacker_row = row + dr * 2
                    attacker_col = col + dc * 2
                    
                    if self.board.is_inside(attacker_row, attacker_col):
                        middle_piece = self.board.get_piece(row + dr, col + dc)
                        if middle_piece == 0:  # Chemin libre
                            continue
                        attacker = self.board.get_piece(attacker_row, attacker_col)
                        if Piece.is_player_piece(attacker, player):
                            protected += 1
                            break
        
        return protected
    
    def _count_isolated_pieces(self, player: int) -> int:
        """Compte les pièces sans alliées à proximité."""
        isolated = 0
        
        for row in range(self.size):
            for col in range(self.size):
                piece = self.board.get_piece(row, col)
                if not Piece.is_player_piece(piece, player):
                    continue
                
                # Vérifier s'il y a un allié à proximité (distance 1)
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
        """Compte les pièces attaquées par l'adversaire."""
        attacked = 0
        
        for row in range(self.size):
            for col in range(self.size):
                piece = self.board.get_piece(row, col)
                if not Piece.is_player_piece(piece, player):
                    continue
                
                # Vérifier si l'adversaire peut capturer cette pièce
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
        """Compte les pièces non-défendues qui sont attaquées."""
        attacked = self._count_attacked_pieces(player, opponent)
        protected = self._count_protected_pieces(player)
        return max(0, attacked - protected)
    
    # ============= CRITÈRE 6: STRUCTURE =============
    def _eval_structure(self, player: int, opponent: int) -> float:
        """Évalue la structure des formations."""
        score = 0
        
        # Chaînes de pions (connected pawns)
        player_chains = self._count_chains(player)
        opponent_chains = self._count_chains(opponent)
        score += (player_chains - opponent_chains) * self.CHAIN_BONUS
        
        # Triangles
        player_triangles = self._count_triangles(player)
        opponent_triangles = self._count_triangles(opponent)
        score += (player_triangles - opponent_triangles) * self.TRIANGLE_BONUS
        
        # Murs défensifs
        player_walls = self._count_wall_formations(player)
        opponent_walls = self._count_wall_formations(opponent)
        score += (player_walls - opponent_walls) * self.WALL_FORMATION_BONUS
        
        return score
    
    def _count_chains(self, player: int) -> int:
        """Compte les pions connectés (côte à côte)."""
        chains = 0
        visited = set()
        
        for row in range(self.size):
            for col in range(self.size):
                piece = self.board.get_piece(row, col)
                if not Piece.is_pawn(piece) or not Piece.is_player_piece(piece, player):
                    continue
                
                if (row, col) in visited:
                    continue
                
                # BFS pour compter la chaîne
                queue = [(row, col)]
                chain_size = 0
                
                while queue:
                    r, c = queue.pop(0)
                    if (r, c) in visited:
                        continue
                    visited.add((r, c))
                    chain_size += 1
                    
                    # Vérifier les voisins
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
    
    def _count_triangles(self, player: int) -> int:
        """Compte les formations de triangle (3 pions en triangle)."""
        triangles = 0
        checked = set()
        
        pieces = []
        for row in range(self.size):
            for col in range(self.size):
                piece = self.board.get_piece(row, col)
                if Piece.is_player_piece(piece, player):
                    pieces.append((row, col))
        
        # Chercher triangles
        for i, (r1, c1) in enumerate(pieces):
            for j, (r2, c2) in enumerate(pieces[i+1:], i+1):
                for k, (r3, c3) in enumerate(pieces[j+1:], j+1):
                    if self._is_triangle((r1, c1), (r2, c2), (r3, c3)):
                        key = tuple(sorted([(r1, c1), (r2, c2), (r3, c3)]))
                        if key not in checked:
                            checked.add(key)
                            triangles += 1
        
        return triangles
    
    def _is_triangle(self, p1: Tuple, p2: Tuple, p3: Tuple) -> bool:
        """Vérifie si 3 points forment un triangle compact."""
        max_dist = 3
        dist1 = abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
        dist2 = abs(p2[0] - p3[0]) + abs(p2[1] - p3[1])
        dist3 = abs(p3[0] - p1[0]) + abs(p3[1] - p1[1])
        return dist1 <= max_dist and dist2 <= max_dist and dist3 <= max_dist
    
    def _count_wall_formations(self, player: int) -> int:
        """Compte les murs défensifs (pions en ligne)."""
        walls = 0
        
        # Chercher des lignes de pions
        for row in range(self.size):
            line_count = 0
            for col in range(self.size):
                piece = self.board.get_piece(row, col)
                if Piece.is_pawn(piece) and Piece.is_player_piece(piece, player):
                    line_count += 1
                else:
                    if line_count >= 3:
                        walls += 1
                    line_count = 0
            if line_count >= 3:
                walls += 1
        
        return walls
    
    # ============= CRITÈRE 7: MENACES =============
    def _eval_threats(self, player: int, opponent: int) -> float:
        """Évalue les menaces et pièges."""
        score = 0
        
        # Menaces simples (captures possibles au prochain coup)
        player_threats = self._count_threats(player)
        opponent_threats = self._count_threats(opponent)
        
        score += (player_threats - opponent_threats) * self.THREAT_BONUS
        
        # Menaces doubles/triples
        player_double = self._count_double_threats(player)
        opponent_double = self._count_double_threats(opponent)
        
        score += (player_double - opponent_double) * self.DOUBLE_THREAT_BONUS
        
        return score
    
    def _count_threats(self, player: int) -> int:
        """Compte les menaces immédiates."""
        mg = MoveGenerator(self.board)
        captures = mg.generate_captures(player)
        return len(captures)
    
    def _count_double_threats(self, player: int) -> int:
        """Compte les coups qui créent plusieurs menaces."""
        mg = MoveGenerator(self.board)
        moves = mg.get_valid_moves(player)
        double_threats = 0
        
        for move in moves[:10]:  # Limiter pour perf
            test_board = self.board.copy()
            record = test_board.make_move(move)
            opponent = 1 if player == 2 else 2
            threats_after = self._count_threats(opponent)
            test_board.undo_move(record)
            
            if threats_after >= 2:
                double_threats += 1
        
        return double_threats
    
    # ============= CRITÈRE 8: PROMOTION =============
    def _eval_promotion(self, player: int, opponent: int) -> float:
        """Évalue la proximité de promotion."""
        score = 0
        
        player_promo = self._eval_promotion_player(player)
        opponent_promo = self._eval_promotion_player(opponent)
        
        score += (player_promo - opponent_promo) * self.PROMOTION_DISTANCE_WEIGHT
        
        # Pénalité si promotion adverse est bloquée
        player_blocked = self._count_promotion_blocks(player, opponent)
        opponent_blocked = self._count_promotion_blocks(opponent, player)
        
        score -= (opponent_blocked - player_blocked) * self.PROMOTION_BLOCKED_PENALTY
        
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
                    # Moins la distance est grande, meilleur c'est
                    total_distance += (self.size - distance)
        
        return total_distance if pawn_count > 0 else 0
    
    def _count_promotion_blocks(self, player: int, opponent: int) -> int:
        """Compte les pions bloqués avant promotion."""
        blocked = 0
        
        for row in range(self.size):
            for col in range(self.size):
                piece = self.board.get_piece(row, col)
                if not Piece.is_pawn(piece) or not Piece.is_player_piece(piece, player):
                    continue
                
                promo_row = Piece.promotion_row(player, self.size)
                
                # Vérifier si le pion est bloqué
                for dr, dc in Piece.forward_directions(player):
                    next_row = row + dr
                    if next_row == promo_row:
                        # Prochaine case est la ligne de promo
                        blocker = self.board.get_piece(next_row, col + dc)
                        if Piece.is_player_piece(blocker, opponent):
                            blocked += 1
                            break
        
        return blocked
    
    # ============= CRITÈRE 9: DAMES =============
    def _eval_queens(self, player: int, opponent: int) -> float:
        """Évalue la force/faiblesse des dames."""
        score = 0
        
        # Mobilité des dames
        player_queen_mobility = self._eval_queen_mobility(player)
        opponent_queen_mobility = self._eval_queen_mobility(opponent)
        
        score += (player_queen_mobility - opponent_queen_mobility) * self.QUEEN_MOBILITY_WEIGHT
        
        # Dames dominantes vs dames enfermées
        player_dominant = self._count_dominant_queens(player)
        opponent_dominant = self._count_dominant_queens(opponent)
        
        score += (player_dominant - opponent_dominant) * self.QUEEN_DOMINANT_BONUS
        
        # Dames enfermées
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
                
                # Compter les cases disponibles pour cette dame
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
        """Compte les dames en position dominante."""
        dominant = 0
        
        for row in range(self.size):
            for col in range(self.size):
                piece = self.board.get_piece(row, col)
                if not Piece.is_queen(piece) or not Piece.is_player_piece(piece, player):
                    continue
                
                # Dame dominante si beaucoup de mouvements disponibles
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
                
                # Dame enfermée si peu de mouvements
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
    
    # ============= CRITÈRE 10: OPPOSITION (FIN DE PARTIE) =============
    def _eval_opposition(self, player: int, opponent: int) -> float:
        """Évalue l'opposition en fin de partie."""
        # Seulement actif si peu de pièces
        total_pieces = self.board.total_piece_count()
        
        if total_pieces > 8:
            return 0  # Pas fin de partie
        
        # Chercher l'opposition
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
        
        # Opposition si contrôle mieux les cases centrales
        player_central = sum(1 for r, c in player_pieces if 2 <= r <= self.size-3 and 2 <= c <= self.size-3)
        opponent_central = sum(1 for r, c in opponent_pieces if 2 <= r <= self.size-3 and 2 <= c <= self.size-3)
        
        if player_central > opponent_central:
            return self.OPPOSITION_BONUS
        
        return 0
    
    # ============= CRITÈRE 11: TEMPO =============
    def _eval_tempo(self, player: int) -> float:
        """Évalue l'initiative/tempo."""
        # Bonus si on est en position aggressive
        # Détecté par: menaces, captures possibles, etc.
        
        mg = MoveGenerator(self.board)
        moves = mg.get_valid_moves(player)
        
        capture_count = len(mg.generate_captures(player))
        
        # Si on a des captures, on a l'initiative
        if capture_count > 0:
            return 20  # Bonus tempo
        
        return 0

def evaluate(board, player: int) -> float:
    """Interface pour compatibilité avec l'ancien code."""
    evaluator = ProfessionalEvaluator()
    return evaluator.evaluate(board, player)
