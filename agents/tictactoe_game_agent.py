"""
Tic-Tac-Toe AI Agent with Tool Calling (ReAct Pattern)
=====================================================
Bagaimana Agent bermain game dengan Tool Calling:
1. Environment menyediakan game state (papan 3x3)
2. Agent mengeksekusi Tool:
   - view_board[]: melihat posisi papan saat ini
   - make_move[row, col]: meletakkan simbol (X atau O)
   - check_status[]: mengecek apakah ada yang menang atau seri
"""

class TicTacToeGame:
    def __init__(self):
        # Inisialisasi papan 3x3 kosong
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.winner = None

    def display(self) -> str:
        res = "\n  0   1   2\n"
        for i, row in enumerate(self.board):
            res += f"{i} " + " | ".join(row) + "\n"
            if i < 2:
                res += "  ---+---+---\n"
        return res

    def make_move(self, row: int, col: int, player: str) -> str:
        if not (0 <= row <= 2 and 0 <= col <= 2):
            return f"Illegal move: Koordinat ({row}, {col}) di luar batas papan (0-2)!"
        if self.board[row][col] != " ":
            return f"Illegal move: Kotak ({row}, {col}) sudah terisi oleh '{self.board[row][col]}'!"
        
        self.board[row][col] = player
        
        # Cek kondisi menang
        if self._check_win(player):
            self.winner = player
            return f"Move sukses: {player} bermain di ({row}, {col}). GAME OVER: {player} MENANG!"
        
        # Cek seri (board penuh)
        if all(cell != " " for r in self.board for cell in r):
            self.winner = "Draw"
            return f"Move sukses: {player} bermain di ({row}, {col}). GAME OVER: Hasil SERI!"

        return f"Move sukses: {player} bermain di ({row}, {col}). Giliran berikutnya."

    def _check_win(self, player: str) -> bool:
        b = self.board
        # Cek baris & kolom
        for i in range(3):
            if all(b[i][j] == player for j in range(3)) or all(b[j][i] == player for j in range(3)):
                return True
        # Cek diagonal
        if b[0][0] == b[1][1] == b[2][2] == player:
            return True
        if b[0][2] == b[1][1] == b[2][0] == player:
            return True
        return False

# ==============================================================================
# DEMONSTRASI LOOP RE-ACT AGENT BERMAIN TIC-TAC-TOE
# ==============================================================================
if __name__ == "__main__":
    game = TicTacToeGame()

    print("=" * 60)
    print("SIMULASI RE-ACT AGENT BERMAIN TIC-TAC-TOE")
    print("=" * 60)

    # Contoh Trajectory Agent AI (sebagai 'O') melawan Manusia (sebagai 'X')
    # Manusia jalan duluan di tengah (1, 1)
    game.make_move(1, 1, "X")
    print("\n[User Move] Manusia meletakkan 'X' di (1, 1):")
    print(game.display())

    # Giliran Agent (O)
    print(">>> Agent Turn (O) <<<")
    print("Thought 1: Lawan mengambil posisi tengah (1, 1). Menurut strategi dasar Tic-Tac-Toe, posisi terbaik berikutnya adalah salah satu sudut. Saya akan memeriksa papan.")
    print("Action 1: view_board[]")
    print(f"Observation 1:\n{game.display()}")
    
    print("Thought 2: Sudut (0, 0) masih kosong. Saya akan mengambil sudut (0, 0).")
    print("Action 2: make_move[row=0, col=0]")
    res = game.make_move(0, 0, "O")
    print(f"Observation 2: {res}")
    print(game.display())

    # Manusia bermain di (0, 1)
    print("\n[User Move] Manusia meletakkan 'X' di (0, 1):")
    game.make_move(0, 1, "X")
    print(game.display())

    # Giliran Agent (O) lagi
    print(">>> Agent Turn (O) <<<")
    print("Thought 3: Lawan memiliki X di (0, 1) dan (1, 1). Ini ancaman serius karena jika lawan meletakkan X di (2, 1), mereka akan menang! Saya HARUS memblokir di baris 2 kolom 1.")
    print("Action 3: make_move[row=2, col=1]")
    res = game.make_move(2, 1, "O")
    print(f"Observation 3: {res}")
    print(game.display())
    print("\n[SUCCESS] Agent berhasil menganalisis ancaman lawan dan memblokir kemenangan lawan!")
