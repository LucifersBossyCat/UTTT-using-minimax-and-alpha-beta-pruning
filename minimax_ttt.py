import math
import time

WIN_LINES = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]

def check_win(board_9):
    """Checks a 9-length list for a winner."""
    for a, b, c in WIN_LINES:
        if board_9[a] != "." and board_9[a] == board_9[b] == board_9[c]:
            return board_9[a]
    return "."

def get_opponent(player):
    return "O" if player == "X" else "X"

class MinimaxBot:
    def __init__(self, depth=5):
        self.depth = depth

    def evaluate_small_box(self, box_list, player):
        """Scores a single 3x3 box based on 3-in-a-row, 2-in-a-row, and 1-in-a-row."""
        score = 0
        opp = get_opponent(player)

        for a, b, c in WIN_LINES:
            line = [box_list[a], box_list[b], box_list[c]]
            p_count = line.count(player)
            o_count = line.count(opp)
            e_count = line.count(".")

            if p_count == 3:
                score += 100
            elif p_count == 2 and e_count == 1:
                score += 10
            elif p_count == 1 and e_count == 2:
                score += 1
            elif o_count == 3:
                score -= 100
            elif o_count == 2 and e_count == 1:
                score -= 10
            elif o_count == 1 and e_count == 2:
                score -= 1

        return score

    def evaluate_board(self, state, macro_state, player):
        """Calculates total heuristic score of the board."""
        score = 0
        # The macro board is worth 200x more than a single small board move
        score += self.evaluate_small_box(macro_state, player) * 200
        
        # Evaluate all 9 small boards
        for m in range(9):
            base = m * 9
            box_list = state[base:base+9]
            score += self.evaluate_small_box(box_list, player)
            
        return score

    def get_valid_moves(self, state, macro_state, prev_move):
        """Returns a list of valid indices (0-80)."""
        valid = []
        target_macro = prev_move % 9 if prev_move is not None else -1

        # If free choice (first move, or sent to a finished macro)
        if target_macro == -1 or macro_state[target_macro] != ".":
            for m in range(9):
                if macro_state[m] == ".":
                    base = m * 9
                    for l in range(9):
                        if state[base + l] == ".":
                            valid.append(base + l)
        else:
            # Constrained choice
            base = target_macro * 9
            for l in range(9):
                if state[base + l] == ".":
                    valid.append(base + l)
        return valid

    def alpha_beta(self, state, macro_state, prev_move, depth, alpha, beta, maximizing_player, player, s_time):
        """The core Minimax algorithm with Alpha-Beta Pruning."""
        is_terminal = check_win(macro_state) != "."
        if depth == 0 or is_terminal:
            return self.evaluate_board(state, macro_state, player)

        valid_moves = self.get_valid_moves(state, macro_state, prev_move)
        if not valid_moves:
            return self.evaluate_board(state, macro_state, player)

        opp = get_opponent(player)
        current_turn = player if maximizing_player else opp

        if maximizing_player:
            max_eval = -math.inf
            for move in valid_moves:
                # Simulate move
                state[move] = current_turn
                m = move // 9
                old_macro = macro_state[m]
                if old_macro == ".":
                    macro_state[m] = check_win(state[m*9 : m*9+9])
                
                # Recurse
                eval = self.alpha_beta(state, macro_state, move, depth - 1, alpha, beta, False, player, s_time)
                
                # Undo move
                state[move] = "."
                macro_state[m] = old_macro

                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
            
        else:
            min_eval = math.inf
            for move in valid_moves:
                # Simulate move
                state[move] = current_turn
                m = move // 9
                old_macro = macro_state[m]
                if old_macro == ".":
                    macro_state[m] = check_win(state[m*9 : m*9+9])
                
                # Recurse
                eval = self.alpha_beta(state, macro_state, move, depth - 1, alpha, beta, True, player, s_time)
                
                # Undo move
                state[move] = "."
                macro_state[m] = old_macro

                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def get_best_move(self, state, macro_state, prev_move, player):
        """Entry point for the bot to pick a move."""
        best_score = -math.inf
        best_move = None
        alpha = -math.inf
        beta = math.inf
        
        valid_moves = self.get_valid_moves(state, macro_state, prev_move)
        s_time = time.time()

        for move in valid_moves:
            # Simulate move
            state[move] = player
            m = move // 9
            old_macro = macro_state[m]
            if old_macro == ".":
                macro_state[m] = check_win(state[m*9 : m*9+9])
            
            # Recurse into Minimax
            score = self.alpha_beta(state, macro_state, move, self.depth - 1, alpha, beta, False, player, s_time)
            
            # Undo move
            state[move] = "."
            macro_state[m] = old_macro

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

# =============================================================================
# CLI Game Loop for testing
# =============================================================================
if __name__ == "__main__":
    def print_cli_board(state):
        for i in range(9):
            if i % 3 == 0: print("-" * 25)
            row = []
            for j in range(9):
                # Map standard row/col to our block layout
                m = (i // 3) * 3 + (j // 3)
                l = (i % 3) * 3 + (j % 3)
                row.append(state[m * 9 + l])
                if j % 3 == 2 and j != 8: row.append("|")
            print(" ".join(row))
        print("-" * 25)

    board = ["."] * 81
    macro = ["."] * 9
    prev = None
    bot = MinimaxBot(depth=4) # Depth 4 is usually safe for python without timing out

    print("Rose (X) vs Daisy (O) - Minimax Engine")
    print_cli_board(board)

    while check_win(macro) == "." and "." in macro:
        # Human Move
        valid = bot.get_valid_moves(board, macro, prev)
        print(f"Valid indices: {valid}")
        move = int(input("Enter move (0-80): "))
        if move not in valid:
            print("Invalid move.")
            continue
        
        board[move] = "X"
        m = move // 9
        if macro[m] == ".": macro[m] = check_win(board[m*9 : m*9+9])
        prev = move
        print_cli_board(board)

        if check_win(macro) != ".":
            print("Rose Wins!")
            break

        # Bot Move
        print("Daisy is thinking...")
        move = bot.get_best_move(board, macro, prev, "O")
        print(f"Daisy plays: {move}")
        board[move] = "O"
        m = move // 9
        if macro[m] == ".": macro[m] = check_win(board[m*9 : m*9+9])
        prev = move
        print_cli_board(board)

        if check_win(macro) != ".":
            print("Daisy Wins!")
            break