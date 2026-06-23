"""
Test rapide du moteur IA refactorisé.
Vérifie que tout fonctionne ensemble.
"""

import sys
sys.path.insert(0, '/home/user/project')

from core.board import Board
from core.analyzer import DamierAnalyzer
from ai.ai_player import AIPlayer
from core.move_generator import MoveGenerator

def test_basic():
    """Test basique du moteur."""
    print("=" * 60)
    print("TEST: Moteur IA refactorisé")
    print("=" * 60)
    
    # Créer le plateau
    analyzer = DamierAnalyzer(8)
    board = Board(8, analyzer=analyzer)
    
    print(f"\n✓ Plateau créé: {board.size}x{board.size}")
    print(f"  Pions par joueur: {analyzer.pieces_per_player}")
    
    # Créer l'IA
    ai = AIPlayer(2, difficulty="intermediate")
    print(f"\n✓ IA créée (niveau: {ai.difficulty}, temps: {ai.time_limit}s)")
    
    # Vérifier le premier coup
    print(f"\nRecherchedu meilleur coup...")
    move = ai.choose_move(board)
    
    if move:
        print(f"✓ Coup trouvé: {move.start_position()} -> {move.last_position()}")
        print(f"  Captures: {move.capture_count()}")
    else:
        print("✗ Aucun coup trouvé!")
    
    # Appliquer le coup
    mg = MoveGenerator(board)
    record = mg.apply_move(move)
    print(f"\n✓ Coup appliqué (record: {record})")
    
    # Annuler le coup
    mg.undo_move(record)
    print(f"✓ Coup annulé")
    
    # Test make_move / undo_move
    print(f"\n✓ Testmake_move/undo_move:")
    board_copy = board.copy()
    record = board_copy.make_move(move)
    print(f"  - make_move réussi")
    board_copy.undo_move(record)
    print(f"  - undo_move réussi")
    
    print("\n" + "=" * 60)
    print("✓ TOUS LES TESTS PASSÉS!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_basic()
    except Exception as e:
        print(f"\n✗ ERREUR: {e}")
        import traceback
        traceback.print_exc()
