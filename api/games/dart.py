def create_dart_game():
    """Create a new Dart game state"""
    return {
        'players': [],
        'scores': [301, 301],  # Starting score for each player (countdown from 301)
        'current_round': 0,
        'darts_thrown': 0,  # Darts thrown in current turn (max 3 per turn)
        'turn': 0,
        'winner': None,
        'game_over': False,
        'round_history': []  # History of throws for display
    }

def validate_dart_throw(throw_value):
    """
    Validate a dart throw value
    Returns: (valid: bool, score: int)
    
    Throw value format:
    - Single number 0-20: regular hit (0 = miss)
    - 'D1' to 'D20': double (2x score)
    - 'T1' to 'T20': triple (3x score)
    - '25': single bull (25 points)
    - 'DB': double bull / bullseye (50 points)
    """
    try:
        # Handle bullseye
        if throw_value == 'DB':
            return True, 50
        if throw_value == '25':
            return True, 25
        
        # Handle doubles
        if isinstance(throw_value, str) and throw_value.startswith('D'):
            num = int(throw_value[1:])
            if 1 <= num <= 20:
                return True, num * 2
            return False, 0
        
        # Handle triples
        if isinstance(throw_value, str) and throw_value.startswith('T'):
            num = int(throw_value[1:])
            if 1 <= num <= 20:
                return True, num * 3
            return False, 0
        
        # Handle regular numbers
        num = int(throw_value)
        if 0 <= num <= 20:
            return True, num
        
        return False, 0
    except (ValueError, TypeError, IndexError):
        return False, 0

def handle_dart_move(game, player_index, throw_data):
    """
    Handle a dart throw in the game
    
    Parameters:
    - game: Current game state
    - player_index: Player making the throw (0 or 1)
    - throw_data: The dart throw value (number, 'D#', 'T#', '25', 'DB')
    
    Returns:
    - (success: bool, updated_game: dict)
    """
    if game['game_over']:
        return False, game
    
    if game['turn'] != player_index:
        return False, game
    
    # Validate throw
    valid, score = validate_dart_throw(throw_data)
    if not valid:
        return False, game
    
    # Calculate new score for player
    current_score = game['scores'][player_index]
    new_score = current_score - score
    
    # Check for bust (score goes below 0 or exactly 1)
    # In standard darts, you must reach exactly 0 and can't go below 0
    # Also, you can't finish on 1 (no way to hit exactly 1 with a double)
    if new_score < 0 or new_score == 1:
        # Bust - score reverts, turn ends
        game['darts_thrown'] = 0
        game['turn'] = 1 - game['turn']
        game['round_history'].append({
            'player': player_index,
            'throw': throw_data,
            'score': score,
            'result': 'bust',
            'remaining': current_score
        })
        return True, game
    
    # Valid throw - update score
    game['scores'][player_index] = new_score
    game['darts_thrown'] += 1
    
    # Record the throw
    game['round_history'].append({
        'player': player_index,
        'throw': throw_data,
        'score': score,
        'result': 'hit',
        'remaining': new_score
    })
    
    # Check for win (reached exactly 0)
    if new_score == 0:
        game['game_over'] = True
        game['winner'] = player_index
        game['darts_thrown'] = 0
        return True, game
    
    # Check if turn is over (3 darts thrown)
    if game['darts_thrown'] >= 3:
        game['darts_thrown'] = 0
        game['turn'] = 1 - game['turn']
        game['current_round'] += 1 if game['turn'] == 0 else 0
    
    return True, game
