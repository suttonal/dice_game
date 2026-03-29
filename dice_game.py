from flask import Flask, render_template, jsonify, request, session
import random
import json

app = Flask(__name__)
app.secret_key = 'yahtzee-secret-key-2024'

SCORE_CATEGORIES = [
    'ones', 'twos', 'threes', 'fours', 'fives', 'sixes',
    'three_of_a_kind', 'four_of_a_kind', 'full_house',
    'small_straight', 'large_straight', 'yahtzee', 'chance'
]

def calculate_score(category, dice):
    counts = [dice.count(i) for i in range(1, 7)]
    
    upper = {'ones': 1, 'twos': 2, 'threes': 3, 'fours': 4, 'fives': 5, 'sixes': 6}
    if category in upper:
        val = upper[category]
        return val * dice.count(val)
    
    if category == 'three_of_a_kind':
        return sum(dice) if any(c >= 3 for c in counts) else 0
    if category == 'four_of_a_kind':
        return sum(dice) if any(c >= 4 for c in counts) else 0
    if category == 'full_house':
        return 25 if (sorted(counts, reverse=True)[:2] == [3, 2] or any(c >= 5 for c in counts)) else 0
    if category == 'small_straight':
        unique = sorted(set(dice))
        straights = [{1,2,3,4}, {2,3,4,5}, {3,4,5,6}]
        return 30 if any(s.issubset(set(unique)) for s in straights) else 0
    if category == 'large_straight':
        unique = sorted(set(dice))
        return 40 if unique == [1,2,3,4,5] or unique == [2,3,4,5,6] else 0
    if category == 'yahtzee':
        return 50 if any(c == 5 for c in counts) else 0
    if category == 'chance':
        return sum(dice)
    return 0

def init_game():
    return {
        'dice': [1, 1, 1, 1, 1],
        'held': [False, False, False, False, False],
        'rolls_left': 3,
        'current_round': 1,
        'total_rounds': 13,
        'scores': {cat: None for cat in SCORE_CATEGORIES},
        'game_over': False,
        'rolled_this_turn': False
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/new_game', methods=['POST'])
def new_game():
    session['game'] = init_game()
    return jsonify(session['game'])

@app.route('/api/roll', methods=['POST'])
def roll():
    game = session.get('game', init_game())
    
    if game['game_over']:
        return jsonify({'error': 'Game over'}), 400
    if game['rolls_left'] <= 0:
        return jsonify({'error': 'No rolls left'}), 400
    
    for i in range(5):
        if not game['held'][i]:
            game['dice'][i] = random.randint(1, 6)
    
    game['rolls_left'] -= 1
    game['rolled_this_turn'] = True
    session['game'] = game
    
    # Calculate potential scores for all unscored categories
    potentials = {}
    for cat in SCORE_CATEGORIES:
        if game['scores'][cat] is None:
            potentials[cat] = calculate_score(cat, game['dice'])
    
    return jsonify({**game, 'potential_scores': potentials})

@app.route('/api/toggle_hold', methods=['POST'])
def toggle_hold():
    game = session.get('game')
    if not game:
        return jsonify({'error': 'No game'}), 400
    
    data = request.get_json()
    idx = data.get('index')
    
    if not game['rolled_this_turn']:
        return jsonify({'error': 'Must roll first'}), 400
    if game['rolls_left'] <= 0:
        return jsonify({'error': 'No rolls left to save for'}), 400
    if 0 <= idx < 5:
        game['held'][idx] = not game['held'][idx]
    
    session['game'] = game
    return jsonify(game)

@app.route('/api/score', methods=['POST'])
def score():
    game = session.get('game')
    if not game:
        return jsonify({'error': 'No game'}), 400
    
    data = request.get_json()
    category = data.get('category')
    
    if not game['rolled_this_turn']:
        return jsonify({'error': 'Must roll at least once'}), 400
    if category not in SCORE_CATEGORIES:
        return jsonify({'error': 'Invalid category'}), 400
    if game['scores'][category] is not None:
        return jsonify({'error': 'Already scored'}), 400
    
    game['scores'][category] = calculate_score(category, game['dice'])
    
    # Reset for next turn
    game['held'] = [False, False, False, False, False]
    game['rolls_left'] = 3
    game['rolled_this_turn'] = False
    game['current_round'] += 1
    
    if all(v is not None for v in game['scores'].values()):
        game['game_over'] = True
    
    session['game'] = game
    
    # Calculate totals
    upper_cats = ['ones', 'twos', 'threes', 'fours', 'fives', 'sixes']
    upper_score = sum(game['scores'][c] or 0 for c in upper_cats)
    bonus = 35 if upper_score >= 63 else 0
    lower_score = sum(game['scores'][c] or 0 for c in SCORE_CATEGORIES if c not in upper_cats)
    total = upper_score + bonus + lower_score
    
    return jsonify({**game, 'upper_score': upper_score, 'bonus': bonus, 'total': total})

@app.route('/api/get_state', methods=['GET'])
def get_state():
    game = session.get('game', init_game())
    session['game'] = game
    
    potentials = {}
    if game['rolled_this_turn']:
        for cat in SCORE_CATEGORIES:
            if game['scores'][cat] is None:
                potentials[cat] = calculate_score(cat, game['dice'])
    
    upper_cats = ['ones', 'twos', 'threes', 'fours', 'fives', 'sixes']
    upper_score = sum(game['scores'][c] or 0 for c in upper_cats)
    bonus = 35 if upper_score >= 63 else 0
    lower_score = sum(game['scores'][c] or 0 for c in SCORE_CATEGORIES if c not in upper_cats)
    total = upper_score + bonus + lower_score
    
    return jsonify({**game, 'potential_scores': potentials, 
                    'upper_score': upper_score, 'bonus': bonus, 'total': total})

if __name__ == '__main__':
    app.run(debug=True, port=5000)