"""Puissance 4 - game logic (no interface here, so the AI can reuse it)."""

ROWS, COLS = 6, 7
EMPTY, P1, P2 = 0, 1, 2          # P1 = Red, P2 = Yellow

DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]  # horiz, vert, 2 diagonals


class Board:
    def __init__(self):
        # grid[0] is the TOP row, grid[ROWS-1] is the BOTTOM row
        self.grid = [[EMPTY] * COLS for _ in range(ROWS)]

    # ---------- moves ----------
    def valid_columns(self):
        """Columns that are not full (top cell still empty)."""
        return [c for c in range(COLS) if self.grid[0][c] == EMPTY]

    def drop(self, col, player):
        """Drop a piece in `col`; it falls to the lowest free row.
        Returns the row where it landed, or None if the column is full."""
        for r in range(ROWS - 1, -1, -1):
            if self.grid[r][col] == EMPTY:
                self.grid[r][col] = player
                return r
        return None

    def undo(self, col):
        """Remove the top piece of `col` (useful for MinMax later)."""
        for r in range(ROWS):
            if self.grid[r][col] != EMPTY:
                self.grid[r][col] = EMPTY
                return

    def copy(self):
        b = Board()
        b.grid = [row[:] for row in self.grid]
        return b

    # ---------- end of game ----------
    def is_full(self):
        return not self.valid_columns()

    def winning_cells(self, player):
        """Return the 4 cells [(r, c), ...] aligned by `player`, or None."""
        for r in range(ROWS):
            for c in range(COLS):
                for dr, dc in DIRECTIONS:
                    cells = [(r + i * dr, c + i * dc) for i in range(4)]
                    if all(0 <= rr < ROWS and 0 <= cc < COLS
                           and self.grid[rr][cc] == player for rr, cc in cells):
                        return cells
        return None

    def has_won(self, player):
        return self.winning_cells(player) is not None
