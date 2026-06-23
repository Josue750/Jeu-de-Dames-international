"""
Table de Transposition (Transposition Table) pour mettre en cache les résultats.
Évite de recalculer les mêmes positions.
"""
from enum import Enum
from typing import Optional, Tuple

class TTFlag(Enum):
    """Types de valeurs dans la table de transposition."""
    EXACT = 0       # Valeur exacte
    LOWER = 1       # Valeur >= réelle (borne inférieure)
    UPPER = 2       # Valeur <= réelle (borne supérieure)

class TTEntry:
    """Entrée dans la table de transposition."""
    
    def __init__(self, depth: int, value: float, flag: TTFlag, 
                 best_move=None, age: int = 0):
        self.depth = depth
        self.value = value
        self.flag = flag
        self.best_move = best_move  # Pour la PVS
        self.age = age  # Pour le remplacement des entrées anciennes

class TranspositionTable:
    """Cache pour les positions évaluées."""
    
    def __init__(self, size_mb: int = 32):
        """
        Initialise la table de transposition.
        
        Args:
            size_mb: Taille en MB (estimée)
        """
        # Estimation: ~200 bytes par entrée
        self.max_entries = (size_mb * 1024 * 1024) // 200
        self.table = {}
        self.age_counter = 0
    
    def store(self, zobrist_hash: int, depth: int, value: float, 
              flag: TTFlag, best_move=None):
        """
        Stocke un résultat dans la table.
        
        Args:
            zobrist_hash: Hash Zobrist de la position
            depth: Profondeur de recherche
            value: Valeur de la position
            flag: Type de valeur (exact, lower, upper)
            best_move: Meilleur coup trouvé (pour PVS)
        """
        if len(self.table) >= self.max_entries:
            self._clear_old_entries()
        
        self.table[zobrist_hash] = TTEntry(depth, value, flag, best_move, self.age_counter)
    
    def lookup(self, zobrist_hash: int, depth: int) -> Optional[Tuple[float, TTFlag]]:
        """
        Récupère un résultat de la table.
        
        Args:
            zobrist_hash: Hash Zobrist
            depth: Profondeur demandée
            
        Returns:
            (valeur, flag) ou None si pas trouvé ou profondeur insuffisante
        """
        if zobrist_hash not in self.table:
            return None
        
        entry = self.table[zobrist_hash]
        
        # Ne retourner que si profondeur suffisante
        if entry.depth >= depth:
            return entry.value, entry.flag
        
        return None
    
    def get_best_move(self, zobrist_hash: int) -> Optional:
        """Récupère le meilleur coup pour une position."""
        if zobrist_hash in self.table:
            return self.table[zobrist_hash].best_move
        return None
    
    def _clear_old_entries(self):
        """Enlève 1/3 des entrées les plus anciennes pour faire place."""
        if not self.table:
            return
        
        # Trier par age
        sorted_entries = sorted(
            self.table.items(),
            key=lambda x: x[1].age
        )
        
        # Enlever 1/3
        entries_to_remove = len(sorted_entries) // 3
        for i in range(entries_to_remove):
            del self.table[sorted_entries[i][0]]
    
    def clear(self):
        """Vide complètement la table."""
        self.table.clear()
    
    def increment_age(self):
        """Incrémente le compteur d'âge (appelé entre les coups)."""
        self.age_counter += 1
    
    def get_stats(self) -> dict:
        """Retourne des statistiques sur la table."""
        return {
            'entries': len(self.table),
            'max_entries': self.max_entries,
            'fill_percent': (len(self.table) / self.max_entries * 100) if self.max_entries > 0 else 0
        }
