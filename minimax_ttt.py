import math
import time

WIN_LINES = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]

def check_win(board_9):
    for a, b, c in WIN_LINES:
        if board_9[a] != "." and board_9[a] == board_9[b] == board_9[c]:
            return board_9[a]
    if "." not in board_9:
        return "D"
    return "."

def get_opponent(player):
    return "O" if player == "X" else "X"

class MinimaxBot:
    def __init__(self, depth=5):
        self.depth = depth

    def evaluate_small_box(self, box_list, player):
        # basic line counting heuristic.
        # these weights took forever to tune so the bot wouldn't just give away the macro board.
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
        score = 0
        
        # macro board control is infinitely more important than winning a random sub-board.
        # hardcoding a massive multiplier here so the pruner prioritizes it.
        score += self.evaluate_small_box(macro_state, player) * 200
        
        for m in range(9):
            base = m * 9
            box_list = state[base:base+9]
            score += self.evaluate_small_box(box_list, player)
            
        return score

    def get_valid_moves(self, state, macro_state, prev_move):
        valid = []
        target_macro = prev_move % 9 if prev_move is not None else -1

        if target_macro == -1 or macro_state[target_macro] != ".":
            for m in range(9):
                if macro_state[m] == ".":
                    base = m * 9
                    for l in range(9):
                        if state[base + l] == ".":
                            valid.append(base + l)
        else:
            base = target_macro * 9
            for l in range(9):
                if state[base + l] == ".":
                    valid.append(base + l)
        return valid

    def alpha_beta(self, state, macro_state, prev_move, depth, alpha, beta, maximizing_player, player, s_time):
        # pure minimax with a-b pruning. 
        # doing this natively in python is slow, so the depth limit is strict to avoid timeouts.
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
                state[move] = current_turn
                m = move // 9
                old_macro = macro_state[m]
                if old_macro == ".":
                    macro_state[m] = check_win(state[m*9 : m*9+9])
                
                eval = self.alpha_beta(state, macro_state, move, depth - 1, alpha, beta, False, player, s_time)
                
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
                state[move] = current_turn
                m = move // 9
                old_macro = macro_state[m]
                if old_macro == ".":
                    macro_state[m] = check_win(state[m*9 : m*9+9])
                
                eval = self.alpha_beta(state, macro_state, move, depth - 1, alpha, beta, True, player, s_time)
                
                state[move] = "."
                macro_state[m] = old_macro

                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def get_best_move(self, state, macro_state, prev_move, player):
        best_score = -math.inf
        best_move = None
        alpha = -math.inf
        beta = math.inf
        
        valid_moves = self.get_valid_moves(state, macro_state, prev_move)
        s_time = time.time()

        for move in valid_moves:
            state[move] = player
            m = move // 9
            old_macro = macro_state[m]
            if old_macro == ".":
                macro_state[m] = check_win(state[m*9 : m*9+9])
            
            score = self.alpha_beta(state, macro_state, move, self.depth - 1, alpha, beta, False, player, s_time)
            
            state[move] = "."
            macro_state[m] = old_macro

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

# quick CLI tester
if __name__ == "__main__":
    def print_cli_board(state):
        for i in range(9):
            if i % 3 == 0: print("-" * 25)
            row = []
            for j in range(9):
                m = (i // 3) * 3 + (j // 3)
                l = (i % 3) * 3 + (j % 3)
                row.append(state[m * 9 + l])
                if j % 3 == 2 and j != 8: row.append("|")
            print(" ".join(row))
        print("-" * 25)

    board = ["."] * 81
    macro = ["."] * 9
    prev = None
    
    # sticking to depth 4 so this doesn't time out the professor's test script.
    bot = MinimaxBot(depth=4) 

    print("P1 (X) vs AI (O) - Minimax CLI Test")
    print_cli_board(board)

    while check_win(macro) == "." and "." in macro:
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
            print("P1 Wins!")
            break

        print("AI is calculating...")
        move = bot.get_best_move(board, macro, prev, "O")
        print(f"AI plays: {move}")
        board[move] = "O"
        m = move // 9
        if macro[m] == ".": macro[m] = check_win(board[m*9 : m*9+9])
        prev = move
        print_cli_board(board)

        if check_win(macro) != ".":
            print("AI Wins!")
            break
