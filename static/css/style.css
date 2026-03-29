// ---- CONFIG ----
const UPPER = ['ones','twos','threes','fours','fives','sixes'];
const LOWER = ['three_of_a_kind','four_of_a_kind','full_house','small_straight','large_straight','yahtzee','chance'];

const LABELS = {
    ones: 'Ones', twos: 'Twos', threes: 'Threes', fours: 'Fours', fives: 'Fives', sixes: 'Sixes',
    three_of_a_kind: 'Three of a Kind', four_of_a_kind: 'Four of a Kind',
    full_house: 'Full House', small_straight: 'Sm. Straight',
    large_straight: 'Lg. Straight', yahtzee: 'Yahtzee!', chance: 'Chance'
};
const HINTS = {
    ones: 'Sum of 1s', twos: 'Sum of 2s', threes: 'Sum of 3s',
    fours: 'Sum of 4s', fives: 'Sum of 5s', sixes: 'Sum of 6s',
    three_of_a_kind: 'Sum all', four_of_a_kind: 'Sum all',
    full_house: '25 pts', small_straight: '30 pts',
    large_straight: '40 pts', yahtzee: '50 pts', chance: 'Sum all'
};

// ---- STATE ----
let gameState = null;

// ---- SVG DICE ----
function dieFace(value) {
    const dotColor = '#1a1a1a';
    const dots = {
        1: [[25,25]],
        2: [[12,12],[38,38]],
        3: [[12,12],[25,25],[38,38]],
        4: [[12,12],[38,12],[12,38],[38,38]],
        5: [[12,12],[38,12],[25,25],[12,38],[38,38]],
        6: [[12,12],[38,12],[12,25],[38,25],[12,38],[38,38]]
    };
    const positions = dots[value] || dots[1];
    const circles = positions.map(([cx, cy]) =>
        `<circle cx="${cx}" cy="${cy}" r="4.5" fill="${dotColor}"/>`
    ).join('');
    return `<svg viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">${circles}</svg>`;
}

// ---- RENDER DICE ----
function renderDice(state) {
    const row = document.getElementById('diceRow');
    const hints = document.getElementById('holdHints');
    const canHold = state.rolled_this_turn && state.rolls_left > 0 && !state.game_over;
    hints.style.display = canHold ? 'block' : 'none';

    row.innerHTML = state.dice.map((val, i) => {
        const held = state.held[i];
        const holdable = canHold;
        const rolling = !held && state.just_rolled;
        return `
        <div class="die-wrap ${holdable ? 'holdable' : ''} ${held ? 'held' : ''} ${rolling ? 'rolling' : ''}" 
             id="die${i}" onclick="${holdable ? `toggleHold(${i})` : ''}">
            <div class="die">${dieFace(val)}</div>
            <div class="hold-label ${held ? 'on' : 'off'}">${held ? 'HELD' : 'HELD'}</div>
        </div>`;
    }).join('');
}

// ---- RENDER ROLL BUTTON ----
function renderRollBtn(state) {
    const btn = document.getElementById('rollBtn');
    const disabled = state.rolls_left <= 0 || state.game_over;
    btn.disabled = disabled;

    const labels = {3: 'ROLL', 2: 'RE-ROLL', 1: 'LAST ROLL'};
    document.querySelector('.btn-roll-text').textContent = labels[state.rolls_left] || 'ROLL';

    // Pips
    for (let i = 0; i < 3; i++) {
        const pip = document.getElementById(`pip${i}`);
        pip.classList.toggle('active', i < state.rolls_left);
    }
    const label = document.getElementById('rollsLabel');
    const r = state.rolls_left;
    label.textContent = r === 0 ? 'NO ROLLS LEFT' : `${r} ROLL${r !== 1 ? 'S' : ''} LEFT`;
}

// ---- RENDER SCORECARD ----
function renderScorecard(state, potentials = {}) {
    document.getElementById('roundNum').textContent = Math.min(state.current_round, 13);

    renderGroup('upperRows', UPPER, state, potentials);
    renderGroup('lowerRows', LOWER, state, potentials);

    // Bonus bar
    const upperScore = UPPER.reduce((s, c) => s + (state.scores[c] || 0), 0);
    const pct = Math.min(100, (upperScore / 63) * 100);
    document.getElementById('bonusBarFill').style.width = pct + '%';
    document.getElementById('bonusVal').textContent = `${upperScore} / 63`;
    const bonusEl = document.getElementById('bonusScore');
    if (upperScore >= 63) {
        bonusEl.textContent = '+35';
        bonusEl.className = 'score-cell bonus-score locked';
    } else {
        bonusEl.textContent = '—';
        bonusEl.className = 'score-cell bonus-score empty';
    }

    // Total
    const bonus = upperScore >= 63 ? 35 : 0;
    const lowerScore = LOWER.reduce((s, c) => s + (state.scores[c] || 0), 0);
    document.getElementById('totalScore').textContent = upperScore + bonus + lowerScore;
}

function renderGroup(containerId, cats, state, potentials) {
    const container = document.getElementById(containerId);
    container.innerHTML = cats.map(cat => {
        const scored = state.scores[cat] !== null && state.scores[cat] !== undefined;
        const potential = !scored && potentials[cat] !== undefined;
        const available = !scored && state.rolled_this_turn && !state.game_over;

        let cellContent = '—';
        let cellClass = 'empty';

        if (scored) {
            cellContent = state.scores[cat];
            cellClass = 'locked';
        } else if (potential) {
            cellContent = potentials[cat] > 0 ? `+${potentials[cat]}` : '0';
            cellClass = potentials[cat] > 0 ? 'potential' : 'zero';
        }

        return `
        <div class="score-row ${scored ? 'scored' : ''} ${available ? 'available' : ''} ${potential && !scored ? 'preview' : ''}"
             onclick="${available ? `scoreCategory('${cat}')` : ''}">
            <div>
                <div class="score-name">${LABELS[cat]}</div>
                ${!scored ? `<div class="score-hint">${HINTS[cat]}</div>` : ''}
            </div>
            <div></div>
            <div class="score-cell ${cellClass}">${cellContent}</div>
        </div>`;
    }).join('');
}

// ---- API CALLS ----
async function newGame() {
    const res = await fetch('/api/new_game', { method: 'POST' });
    gameState = await res.json();
    gameState.just_rolled = false;
    document.getElementById('gameOverModal').style.display = 'none';
    render();
}

async function rollDice() {
    if (!gameState || gameState.rolls_left <= 0 || gameState.game_over) return;
    
    // Animate unhelds
    for (let i = 0; i < 5; i++) {
        if (!gameState.held[i]) {
            const el = document.getElementById(`die${i}`);
            if (el) { el.classList.remove('rolling'); void el.offsetWidth; el.classList.add('rolling'); }
        }
    }

    const res = await fetch('/api/roll', { method: 'POST' });
    const data = await res.json();
    gameState = { ...data, just_rolled: true };
    
    setTimeout(() => render(), 50);
}

async function toggleHold(index) {
    if (!gameState || !gameState.rolled_this_turn || gameState.rolls_left <= 0) return;
    const res = await fetch('/api/toggle_hold', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ index })
    });
    gameState = { ...(await res.json()), just_rolled: false };
    
    // Recalculate potentials from last roll (kept in current state)
    const potRes = await fetch('/api/get_state');
    const fullState = await potRes.json();
    render(fullState.potential_scores);
}

async function scoreCategory(category) {
    if (!gameState || !gameState.rolled_this_turn) return;
    const res = await fetch('/api/score', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ category })
    });
    const data = await res.json();
    gameState = { ...data, just_rolled: false };
    render();

    if (data.game_over) showGameOver(data);
}

// ---- RENDER ----
function render(potentials = null) {
    if (!gameState) return;
    renderDice(gameState);
    renderRollBtn(gameState);
    
    if (potentials === null && gameState.rolled_this_turn) {
        fetch('/api/get_state').then(r => r.json()).then(s => {
            renderScorecard(gameState, s.potential_scores || {});
        });
    } else {
        renderScorecard(gameState, potentials || {});
    }
}

// ---- GAME OVER ----
function showGameOver(data) {
    const upper = UPPER.reduce((s, c) => s + (data.scores[c] || 0), 0);
    const bonus = upper >= 63 ? 35 : 0;
    const lower = LOWER.reduce((s, c) => s + (data.scores[c] || 0), 0);
    const total = upper + bonus + lower;

    document.getElementById('modalScore').textContent = total;
    
    let rating;
    if (total >= 350) rating = 'Legendary — Pure Dice Mastery';
    else if (total >= 300) rating = 'Excellent — Outstanding Play';
    else if (total >= 250) rating = 'Great — Above Average';
    else if (total >= 200) rating = 'Good — Solid Performance';
    else if (total >= 150) rating = 'Average — Room to Improve';
    else rating = 'Keep Practicing — Better Luck Next Time';
    
    document.getElementById('modalRating').textContent = rating;
    document.getElementById('gameOverModal').style.display = 'flex';
}

// ---- INIT ----
window.addEventListener('load', async () => {
    const res = await fetch('/api/get_state');
    const data = await res.json();
    gameState = { ...data, just_rolled: false };
    render(data.potential_scores);
    
    // If fresh session, start a new game
    if (gameState.current_round === 1 && !gameState.rolled_this_turn) {
        // Game already initialized
    }
});
