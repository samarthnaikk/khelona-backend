def check_winner(board):
    """Check if there's a winner in Tic Tac Toe"""
    # Check rows, columns, and diagonals
    lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
        [0, 4, 8], [2, 4, 6]              # diagonals
    ]
    
    for line in lines:
        if board[line[0]] and board[line[0]] == board[line[1]] == board[line[2]]:
            return board[line[0]], line
    
    # Check for tie
    if all(cell != '' for cell in board):
        return 'tie', []
    
    return None, []

def create_tic_tac_toe_game():
    """Create a new Tic Tac Toe game state"""
    return {
        'players': [], 
        'board': ['']*9, 
        'turn': 0, 
        'winner': None, 
        'game_over': False, 
        'winning_line': []
    }

def handle_tic_tac_toe_move(game, player_index, move_index):
    """Handle a move in Tic Tac Toe game"""
    if game['game_over'] or game['board'][move_index] != '':
        return False, game
    
    # Make the move
    game['board'][move_index] = 'X' if player_index == 0 else 'O'
    
    # Check for winner
    winner, winning_line = check_winner(game['board'])
    if winner:
        game['game_over'] = True
        game['winner'] = winner
        game['winning_line'] = winning_line
    else:
        game['turn'] = 1 - game['turn']
    
    return True, game