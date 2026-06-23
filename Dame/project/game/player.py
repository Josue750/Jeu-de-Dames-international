from abc import ABC, abstractmethod


class Player(ABC):
    """Interface commune pour les joueurs humain et IA."""

    def __init__(self, player_id: int):
        self.player_id = player_id

    @abstractmethod
    def choose_move(self, board):
        raise NotImplementedError
