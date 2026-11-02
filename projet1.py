

import heapq
import itertools
import tkinter as tk
from tkinter import ttk


# 1. REPRESENTATION DES ETATS
# Un etat = tuple de 9 valeurs (ligne par ligne), 0 = case vide.
FIGURE_1 = (1, 2, 3,
            8, 0, 4,
            7, 6, 5)


def neighbors(state):
    """Etats atteignables en glissant un jeton dans la case vide."""
    result = []
    i = state.index(0)                      # position de la case vide
    row, col = divmod(i, 3)
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:   # haut, bas, gauche, droite
        r, c = row + dr, col + dc
        if 0 <= r < 3 and 0 <= c < 3:       # on reste dans le damier
            j = r * 3 + c
            new = list(state)               # copie modifiable
            new[i], new[j] = new[j], new[i] # echange case vide / jeton
            result.append(tuple(new))
    return result


def board_text(state):
    """Damier sous forme de texte (3 lignes)."""
    lines = []
    for r in range(3):
        row = state[r * 3: r * 3 + 3]
        lines.append(" ".join("_" if t == 0 else str(t) for t in row))
    return "\n".join(lines)


# 2. HEURISTIQUE h(n) : distance de Manhattan

def h_manhattan(state, goal):
    """Somme des distances de Manhattan de chaque jeton a sa place finale."""
    total = 0
    for i, t in enumerate(state):
        if t == 0:
            continue                        # la case vide ne compte pas
        r, c = divmod(i, 3)
        gr, gc = divmod(goal.index(t), 3)
        total += abs(r - gr) + abs(c - gc)
    return total


# 3. ALGORITHME A*

def astar(start, goal, h):
    """
    Retourne (chemin, trace).
      chemin : liste d'etats de start a goal (None si pas de solution)
      trace  : liste de (numero, g, h, f, etat) pour chaque exploration
    """
    tie = itertools.count()                 # departage les f egaux
    open_heap = [(h(start, goal), next(tie), 0, start)]   # (f, tie, g, etat)
    best_g = {start: 0}                     # meilleur g connu par etat
    parent = {start: None}                  # pour reconstruire le chemin
    closed = set()                          # etats deja explores
    trace = []

    while open_heap:
        f, _, g, state = heapq.heappop(open_heap)   # plus petit f
        if state in closed:                 # entree obsolete
            continue
        closed.add(state)
        trace.append((len(trace) + 1, g, f - g, f, state))

        if state == goal:                   # but atteint : reconstruire le chemin
            path = []
            while state is not None:
                path.append(state)
                state = parent[state]
            return path[::-1], trace

        for nb in neighbors(state):
            ng = g + 1
            if nb not in best_g or ng < best_g[nb]:
                best_g[nb] = ng
                parent[nb] = state
                heapq.heappush(open_heap, (ng + h(nb, goal), next(tie), ng, nb))

    return None, trace


# 4. INTERFACE TKINTER

MAX_TRACE_SHOWN = 300       # limite d'affichage pour garder l'interface fluide


class TaquinApp:
    def __init__(self, root):
        self.root = root
        root.title("Taquin - A*")

        self.state = FIGURE_1       # damier courant

        # --- damier (3x3 boutons) ---
        board = ttk.Frame(root, padding=10)
        board.grid(row=0, column=0, sticky="n")
        self.buttons = []
        for i in range(9):
            b = tk.Button(board, text="", width=4, height=2,
                          font=("Helvetica", 24, "bold"),
                          command=lambda i=i: self.on_click(i))
            b.grid(row=i // 3, column=i % 3, padx=2, pady=2)
            self.buttons.append(b)

        # --- commandes ---
        ctrl = ttk.Frame(root, padding=10)
        ctrl.grid(row=1, column=0, sticky="n")

        ttk.Button(ctrl, text="Resoudre (A*)", command=self.solve).grid(
            row=0, column=0, pady=4, sticky="ew")
        ttk.Button(ctrl, text="Reinitialiser", command=self.reset).grid(
            row=1, column=0, pady=4, sticky="ew")

        self.info = tk.StringVar(value="Glissez des jetons, puis cliquez sur Resoudre.")
        ttk.Label(ctrl, textvariable=self.info, wraplength=200).grid(row=2, column=0)

        # --- zone de texte : trace des explorations ---
        right = ttk.Frame(root, padding=10)
        right.grid(row=0, column=1, rowspan=2, sticky="nsew")
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)
        self.text = tk.Text(right, width=38, height=28, font=("Courier", 11))
        scroll = ttk.Scrollbar(right, command=self.text.yview)
        self.text.configure(yscrollcommand=scroll.set)
        self.text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.draw()

    # ---------- affichage ----------
    def draw(self):
        for i, b in enumerate(self.buttons):
            t = self.state[i]
            b.config(text="" if t == 0 else str(t),
                     relief="sunken" if t == 0 else "raised")

    # ---------- interaction utilisateur ----------
    def on_click(self, i):
        """Glisse le jeton i vers la case vide s'il lui est adjacent."""
        j = self.state.index(0)
        (ri, ci), (rj, cj) = divmod(i, 3), divmod(j, 3)
        if abs(ri - rj) + abs(ci - cj) == 1:        # cases voisines ?
            new = list(self.state)
            new[i], new[j] = new[j], new[i]
            self.state = tuple(new)
            self.draw()

    def reset(self):
        self.state = FIGURE_1
        self.text.delete("1.0", "end")
        self.info.set("Damier reinitialise.")
        self.draw()

    # ---------- resolution ----------
    def solve(self):
        # on part de la configuration FINALE (celle de l'utilisateur)
        # et on cherche la configuration INITIALE (figure 1)
        path, trace = astar(self.state, FIGURE_1, h_manhattan)

        self.text.delete("1.0", "end")
        for k, g, hh, f, st in trace[:MAX_TRACE_SHOWN]:
            self.text.insert("end", f"Exploration {k}: g={g} h={hh} f={f}\n")
            self.text.insert("end", board_text(st) + "\n\n")
        if len(trace) > MAX_TRACE_SHOWN:
            self.text.insert("end", f"... ({len(trace) - MAX_TRACE_SHOWN} "
                                    f"explorations non affichees)\n")

        if path is None:
            self.info.set("Aucune solution.")
        else:
            self.info.set(f"Solution : {len(path) - 1} deplacements, "
                          f"{len(trace)} etats explores.")


if __name__ == "__main__":
    root = tk.Tk()
    TaquinApp(root)
    root.mainloop()
