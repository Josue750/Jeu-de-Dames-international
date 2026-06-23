"""
gui_interface.py
Interface graphique Tkinter pour le simulateur de jeu de dames.
Auteur : Alimath
Projet : Bras Robotique Joueur de Dames
"""

import tkinter as tk
from tkinter import messagebox

from integration.engine_adapter import EngineAdapter

CELL_SIZE  = 70
PADDING    = 20
COLOR_DARK   = "#6B3F2A"
COLOR_LIGHT  = "#F0D9B5"
COLOR_SELECT = "#FFD700"
COLOR_TARGET = "#90EE90"
COLOR_P1     = "#FFFFFF"
COLOR_P2     = "#1A1A1A"
COLOR_BG     = "#2C2C2C"
PLAYER_1 = 1
PLAYER_2 = 2
PLAYER_NAMES = {PLAYER_1: "Joueur 1 (Blanc)", PLAYER_2: "Joueur 2 (Noir)"}
AI_LABEL = "Minimax intégré"


class GUIInterface:

    def __init__(self, root, mode="hvh", size: int = 8, depth: int = 3):
        self.root = root
        self.mode = mode
        self.adapter = EngineAdapter(size=size, ai_depth=depth)
        self.selected_piece = None
        self.legal_moves = []
        self.piece_moves = []
        self.board_size = self.adapter.get_board_size()
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        self.root.title("Simulateur Jeu de Dames - Bras Robotique")
        self.root.configure(bg=COLOR_BG)
        self.root.resizable(False, False)
        board_px = self.board_size * CELL_SIZE + 2 * PADDING

        self.canvas = tk.Canvas(self.root, width=board_px, height=board_px,
                                bg=COLOR_BG, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)
        self.canvas.bind("<Button-1>", self._on_click)

        side = tk.Frame(self.root, bg=COLOR_BG, width=220)
        side.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)

        tk.Label(side, text="JEU DE DAMES", bg=COLOR_BG, fg="#FFD700",
                 font=("Arial", 14, "bold")).pack(pady=(10, 2))
        tk.Label(side, text="Bras Robotique", bg=COLOR_BG, fg="#AAAAAA",
                 font=("Arial", 10)).pack(pady=(0, 4))
        tk.Label(side, text="IA : " + AI_LABEL, bg=COLOR_BG, fg="#FF9800",
                 font=("Arial", 9, "italic")).pack(pady=(0, 16))

        self.lbl_tour   = tk.Label(side, text="", bg=COLOR_BG, fg="white",   font=("Arial", 11))
        self.lbl_joueur = tk.Label(side, text="", bg=COLOR_BG, fg="#90EE90", font=("Arial", 11, "bold"))
        self.lbl_p1     = tk.Label(side, text="", bg=COLOR_BG, fg="#CCCCCC", font=("Arial", 10))
        self.lbl_p2     = tk.Label(side, text="", bg=COLOR_BG, fg="#CCCCCC", font=("Arial", 10))
        for w in (self.lbl_tour, self.lbl_joueur, self.lbl_p1, self.lbl_p2):
            w.pack(pady=2)

        tk.Frame(side, bg="#444444", height=1).pack(fill=tk.X, pady=12)
        tk.Label(side, text="Derniers coups :", bg=COLOR_BG, fg="#AAAAAA",
                 font=("Arial", 9)).pack()
        self.log_box = tk.Text(side, width=24, height=12, bg="#1A1A1A", fg="#CCCCCC",
                               font=("Courier", 9), state=tk.DISABLED, relief=tk.FLAT)
        self.log_box.pack(pady=5)
        tk.Frame(side, bg="#444444", height=1).pack(fill=tk.X, pady=8)
        tk.Button(side, text="Nouvelle partie", command=self._new_game,
                  bg="#444444", fg="white", font=("Arial", 10),
                  relief=tk.FLAT, padx=10, pady=5).pack(pady=5)
        tk.Label(side, text="Blanc=O  Noir=X  Dame=D",
                 bg=COLOR_BG, fg="#888888", font=("Arial", 9)).pack(pady=10)

    def _draw_board(self):
        self.canvas.delete("all")
        targets = {tuple(m["to"]): m for m in self.piece_moves}
        board = self.adapter.get_board()

        for r in range(self.board_size):
            for c in range(self.board_size):
                x1 = PADDING + c * CELL_SIZE
                y1 = PADDING + r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                if (r + c) % 2 == 0:
                    fill = COLOR_LIGHT
                elif (r, c) in targets:
                    fill = COLOR_TARGET
                elif self.selected_piece == (r, c):
                    fill = COLOR_SELECT
                else:
                    fill = COLOR_DARK

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="")

                if c == 0:
                    self.canvas.create_text(x1 - 12, (y1 + y2) // 2, text=str(r),
                                            fill="#888888", font=("Arial", 8))
                if r == self.board_size - 1:
                    self.canvas.create_text((x1 + x2) // 2, y2 + 12, text=str(c),
                                            fill="#888888", font=("Arial", 8))

                piece = board[r][c]
                if piece != 0:
                    self._draw_piece(r, c, piece)

    def _draw_piece(self, r, c, piece):
        x = PADDING + c * CELL_SIZE + CELL_SIZE // 2
        y = PADDING + r * CELL_SIZE + CELL_SIZE // 2
        radius = CELL_SIZE // 2 - 8
        is_p1 = piece in (1, 3)
        color = COLOR_P1 if is_p1 else COLOR_P2
        outline = "#AAAAAA" if is_p1 else "#555555"
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                fill=color, outline=outline, width=2)
        if self.adapter.is_queen_piece(piece):
            self.canvas.create_text(x, y, text="D",
                                    fill="#FFD700",
                                    font=("Arial", 16, "bold"))

    def _on_click(self, event):
        if self.adapter.is_game_over():
            return
        c = (event.x - PADDING) // CELL_SIZE
        r = (event.y - PADDING) // CELL_SIZE
        if not (0 <= r < self.board_size and 0 <= c < self.board_size):
            return

        cp = self.adapter.get_current_player()
        if self.mode == "aia" or (self.mode == "hva" and cp == PLAYER_2):
            return

        targets = {tuple(m["to"]): m for m in self.piece_moves}

        if self.selected_piece and (r, c) in targets:
            move = targets[(r, c)]
            if self.adapter.make_move(move):
                self._log_move(move)
                self.selected_piece = None
                self.piece_moves = []
                self._refresh()
                if self.mode == "hva" and not self.adapter.is_game_over():
                    self.root.after(400, self._ai_play)
        elif self.adapter.is_player_piece(r, c, cp):
            self.selected_piece = (r, c)
            self.piece_moves = self.adapter.get_legal_moves(position=(r, c))
            self._draw_board()
        else:
            self.selected_piece = None
            self.piece_moves = []
            self._draw_board()

    def _ai_play(self):
        if self.adapter.is_game_over():
            return

        if self.mode == "hva":
            move = self.adapter.ai_move()
        elif self.mode == "aia":
            move = self.adapter.ai_move(player=self.adapter.get_current_player())
        else:
            return

        if move:
            self._log_move(move)
        self._refresh()

    def _refresh(self):
        self.legal_moves = self.adapter.get_legal_moves()
        self._draw_board()
        self._update_labels()
        if self.adapter.is_game_over():
            winner = self.adapter.get_winner()
            if winner:
                msg = "Partie terminee !\nGagnant : " + PLAYER_NAMES.get(winner, "Inconnu")
            else:
                msg = "Match nul !"
            messagebox.showinfo("Fin de partie", msg)
        elif self.mode == "aia":
            self.root.after(400, self._ai_play)

    def _update_labels(self):
        score = self.adapter.get_score()
        self.lbl_tour.config(text="Tour n " + str(self.adapter.get_turn_number()))
        cp = self.adapter.get_current_player()
        self.lbl_joueur.config(text="=> " + PLAYER_NAMES.get(cp, "Inconnu"))
        self.lbl_p1.config(text="Blanc O : " + str(score.get(PLAYER_1, 0)) + " pieces")
        self.lbl_p2.config(text="Noir  X : " + str(score.get(PLAYER_2, 0)) + " pieces")

    def _log_move(self, move):
        self.log_box.config(state=tk.NORMAL)
        cap = " [capture]" if move.get("captured") else ""
        self.log_box.insert(tk.END, str(move["from"]) + "->" + str(move["to"]) + cap + "\n")
        self.log_box.see(tk.END)
        self.log_box.config(state=tk.DISABLED)

    def _new_game(self):
        self.adapter.reset_game()
        self.selected_piece = None
        self.piece_moves = []
        self.log_box.config(state=tk.NORMAL)
        self.log_box.delete("1.0", tk.END)
        self.log_box.config(state=tk.DISABLED)
        self._refresh()


def run_gui(mode="hvh", size: int = 8, depth: int = 3):
    root = tk.Tk()
    GUIInterface(root, mode=mode, size=size, depth=depth)
    root.mainloop()


def choose_game_mode():
    choice = {"mode": None}

    def set_mode(value):
        choice["mode"] = value
        selector.destroy()

    selector = tk.Tk()
    selector.title("Mode de jeu")
    selector.configure(bg=COLOR_BG)
    selector.resizable(False, False)

    frame = tk.Frame(selector, bg=COLOR_BG, padx=20, pady=20)
    frame.pack()

    tk.Label(frame,
             text="Choisissez un mode de jeu",
             bg=COLOR_BG,
             fg="#FFD700",
             font=("Arial", 14, "bold")).pack(pady=(0, 16))

    tk.Button(frame, text="Humain vs Humain", width=20,
              command=lambda: set_mode("hvh"),
              bg="#444444", fg="white", font=("Arial", 11),
              relief=tk.FLAT, padx=10, pady=8).pack(pady=6)
    tk.Button(frame, text="Humain vs IA", width=20,
              command=lambda: set_mode("hva"),
              bg="#444444", fg="white", font=("Arial", 11),
              relief=tk.FLAT, padx=10, pady=8).pack(pady=6)
    tk.Button(frame, text="IA vs IA", width=20,
              command=lambda: set_mode("aia"),
              bg="#444444", fg="white", font=("Arial", 11),
              relief=tk.FLAT, padx=10, pady=8).pack(pady=6)

    selector.mainloop()
    return choice["mode"]


def main():
    mode = choose_game_mode()
    if mode:
        run_gui(mode)


if __name__ == "__main__":
    main()
