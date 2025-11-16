from .tic_tac_toe import create_tic_tac_toe_game, handle_tic_tac_toe_move

# Game registry - add new games here
GAME_HANDLERS = {
    'tic-tac-toe': {
        'create': create_tic_tac_toe_game,
        'handle_move': handle_tic_tac_toe_move
    }
}

def create_game(game_type):
    """Create a new game of the specified type"""
    if game_type in GAME_HANDLERS:
        return GAME_HANDLERS[game_type]['create']()
    return None

def handle_game_move(game_type, game_state, player_index, move_data):
    """Handle a move for the specified game type"""
    if game_type in GAME_HANDLERS:
        return GAME_HANDLERS[game_type]['handle_move'](game_state, player_index, move_data)
    return False, game_state