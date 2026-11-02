"""Puissance 4 - Stage 1: Human vs Human (tkinter interface)."""
import tkinter as tk
from projet2_logic import Board, ROWS, COLS, EMPTY, P1, P2

CELL = 90
PAD = 8
COLORS = {EMPTY: "white", P1: "red", P2: "gold"}
NAMES = {P1: "Rouge", P2: "Jaune"}


class App:
    def __init__(self, root):
        root.title("Puissance 4")
        self.status = tk.Label(root, font=("Arial", 16))
        self.status.pack(pady=6)
        self.canvas = tk.Canvas(root, width=COLS * CELL, height=ROWS * CELL,
                                bg="royalblue", highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)
        tk.Button(root, text="Nouvelle partie", command=self.reset).pack(pady=6)
        self.reset()

    def reset(self):
        self.board = Board()
        self.current = P1
        self.game_over = False
        self.win_cells = []
        self.draw()
        self.status.config(text=f"Au tour du joueur {NAMES[self.current]}")

    def on_click(self, event):
        if self.game_over:
            return
        col = event.x // CELL
        if col not in self.board.valid_columns():
            return                                  # full column: ignore click
        self.board.drop(col, self.current)

        cells = self.board.winning_cells(self.current)
        if cells:
            self.win_cells = cells
            self.game_over = True
            self.status.config(text=f"Le joueur {NAMES[self.current]} gagne !")
        elif self.board.is_full():
            self.game_over = True
            self.status.config(text="Partie nulle !")
        else:
            self.current = P2 if self.current == P1 else P1
            self.status.config(text=f"Au tour du joueur {NAMES[self.current]}")
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                x0, y0 = c * CELL + PAD, r * CELL + PAD
                x1, y1 = (c + 1) * CELL - PAD, (r + 1) * CELL - PAD
                win = (r, c) in self.win_cells
                self.canvas.create_oval(
                    x0, y0, x1, y1, fill=COLORS[self.board.grid[r][c]],
                    outline="black" if win else "navy", width=5 if win else 2)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
