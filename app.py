"""
app.py — Flask web server for Floral Ultimate Tic-Tac-Toe (Minimax AI)
"""

import uuid
from flask import Flask, jsonify, request, render_template
import minimax_ttt

app = Flask(__name__, template_folder='.')
app.secret_key = 'floral-ttt-secret'

# Global dictionary to store active games
games = {}

def format_state(board, macro, prev_move, turn):
    """Translates the python backend state into the JSON the frontend expects."""
    terminal = minimax_ttt.check_win(macro)
    terminal = None if terminal == "." else terminal

    active_macro = None
    if prev_move is not None:
        m = prev_move % 9
        if macro[m] == ".":
            active_macro = m

    bot = minimax_ttt.MinimaxBot()
    valid_moves = bot.get_valid_moves(board, macro, prev_move) if not terminal else []

    return {
        "cells": [c if c != "." else None for c in board],
        "macro": [m if m != "." else None for m in macro],
        "turn": turn,
        "prev_move": prev_move,
        "active_macro": active_macro,
        "valid_moves": valid_moves,
        "terminal": terminal
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/new_game', methods=['POST'])
def new_game():
    data = request.json or {}
    human_sym = data.get('human_symbol', 'X')
    depth = int(data.get('depth', 5))

    game_id = str(uuid.uuid4())
    board = ["."] * 81
    macro = ["."] * 9

    games[game_id] = {
        "board": board,
        "macro": macro,
        "prev_move": None,
        "human_sym": human_sym,
        "ai_sym": "O" if human_sym == "X" else "X",
        "depth": depth,
        "turn": "X" # X (Rose) always moves first
    }

    # If Human chose Daisy (O), the AI plays first as Rose (X)
    if human_sym == "O":
        bot = minimax_ttt.MinimaxBot(depth=depth)
        ai_move = bot.get_best_move(board, macro, None, "X")
        board[ai_move] = "X"
        macro[ai_move // 9] = minimax_ttt.check_win(board[(ai_move//9)*9 : (ai_move//9)*9+9])
        games[game_id]["prev_move"] = ai_move
        games[game_id]["turn"] = "O"

    state_dict = format_state(
        games[game_id]["board"], 
        games[game_id]["macro"], 
        games[game_id]["prev_move"], 
        games[game_id]["turn"]
    )
    
    return jsonify({"game_id": game_id, "state": state_dict})

@app.route('/api/move', methods=['POST'])
def make_move():
    data = request.json or {}
    game_id = data.get('game_id')
    pos = int(data.get('pos', -1))

    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    board = game["board"]
    macro = game["macro"]
    human_sym = game["human_sym"]
    ai_sym = game["ai_sym"]

    # --- 1. Process Human Move ---
    board[pos] = human_sym
    m = pos // 9
    if macro[m] == ".":
        macro[m] = minimax_ttt.check_win(board[m*9 : m*9+9])
    prev_move = pos

    # Check if the human just won the game
    if minimax_ttt.check_win(macro) != ".":
        state_dict = format_state(board, macro, prev_move, ai_sym)
        return jsonify({"state": state_dict})

    # --- 2. Process AI Move ---
    bot = minimax_ttt.MinimaxBot(depth=game["depth"])
    ai_move = bot.get_best_move(board, macro, prev_move, ai_sym)

    if ai_move is not None:
        board[ai_move] = ai_sym
        m = ai_move // 9
        if macro[m] == ".":
            macro[m] = minimax_ttt.check_win(board[m*9 : m*9+9])
        prev_move = ai_move

    # Save state
    game["prev_move"] = prev_move
    game["turn"] = human_sym

    state_dict = format_state(board, macro, prev_move, human_sym)
    return jsonify({"state": state_dict})

if __name__ == '__main__':
    print("\n  Floral Ultimate Tic-Tac-Toe Server Running!")
    print("  Open http://127.0.0.1:5000 in your browser\n")
    app.run(debug=True, port=5000)