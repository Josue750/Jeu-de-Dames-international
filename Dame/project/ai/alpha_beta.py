class AlphaBetaPruner:
    """Fournit des utilitaires pour l'élagage Alpha-Beta."""

    @staticmethod
    def should_prune(alpha: float, beta: float) -> bool:
        return alpha >= beta

    @staticmethod
    def update_alpha(alpha: float, value: float) -> float:
        return max(alpha, value)

    @staticmethod
    def update_beta(beta: float, value: float) -> float:
        return min(beta, value)
