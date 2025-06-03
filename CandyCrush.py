import streamlit as st
import random
import time
from streamlit.components.v1 import html

st.set_page_config(page_title="Candy Crush Mini", layout="centered", page_icon="🍬")

# Custom CSS for animations and styling
st.markdown("""
<style>
@keyframes fadeIn {
    from {opacity: 0;}
    to {opacity: 1;}
}

@keyframes bounce {
    0%, 100% {transform: translateY(0);}
    50% {transform: translateY(-10px);}
}

@keyframes shake {
    0%, 100% {transform: translateX(0);}
    25% {transform: translateX(-5px);}
    75% {transform: translateX(5px);}
}

.candy-button {
    font-size: 2rem;
    padding: 0.5rem;
    margin: 0.1rem;
    border-radius: 10px;
    border: 2px solid transparent;
    transition: all 0.3s ease;
    animation: fadeIn 0.5s ease-out;
}

.candy-button:hover {
    transform: scale(1.1);
    box-shadow: 0 0 15px rgba(255,255,255,0.5);
}

.selected {
    border: 2px solid #FFD700 !important;
    box-shadow: 0 0 15px #FFD700;
    animation: bounce 0.5s infinite alternate;
}

.matched {
    animation: fadeIn 0.5s, shake 0.5s;
}

.score-display {
    font-size: 1.5rem;
    font-weight: bold;
    color: #FF6B6B;
    text-align: center;
    margin: 1rem 0;
}

.header {
    text-align: center;
    color: #FF6B6B;
    margin-bottom: 1rem;
}

.restart-btn {
    background-color: #FF6B6B !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 20px !important;
    padding: 0.5rem 1rem !important;
}

.footer {
    text-align: center;
    margin-top: 2rem;
    color: #666;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# Game configuration
CANDIES = ['🍒', '🍋', '🍇', '🍬', '🍭', '🧁']
CANDY_COLORS = {
    '🍒': '#FF6B6B',
    '🍋': '#FFD166',
    '🍇': '#A64AC9',
    '🍬': '#F77F00',
    '🍭': '#06D6A0',
    '🧁': '#FF9FF3'
}
ROWS, COLS = 8, 8
INITIAL_SCORE = 0
TARGET_SCORE = 100

# Initialize game state
if "grid" not in st.session_state:
    st.session_state.grid = [[random.choice(CANDIES) for _ in range(COLS)] for _ in range(ROWS)]
if "selected" not in st.session_state:
    st.session_state.selected = []
if "score" not in st.session_state:
    st.session_state.score = INITIAL_SCORE
if "moves" not in st.session_state:
    st.session_state.moves = 0
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "processing" not in st.session_state:
    st.session_state.processing = False
if "effect_positions" not in st.session_state:
    st.session_state.effect_positions = []
if "effect_type" not in st.session_state:
    st.session_state.effect_type = ""

# Swap candies
def swap(pos1, pos2):
    r1, c1 = pos1
    r2, c2 = pos2
    st.session_state.grid[r1][c1], st.session_state.grid[r2][c2] = st.session_state.grid[r2][c2], st.session_state.grid[r1][c1]

# Enhanced match detection
def find_matches():
    matched = set()
    grid = st.session_state.grid
    
    # Horizontal matches
    for r in range(ROWS):
        for c in range(COLS - 2):
            if grid[r][c] == grid[r][c+1] == grid[r][c+2]:
                candy_type = grid[r][c]
                left = c
                right = c + 2
                while left > 0 and grid[r][left-1] == candy_type:
                    left -= 1
                while right < COLS - 1 and grid[r][right+1] == candy_type:
                    right += 1
                matched.update([(r, col) for col in range(left, right+1)])
    
    # Vertical matches
    for c in range(COLS):
        for r in range(ROWS - 2):
            if grid[r][c] == grid[r+1][c] == grid[r+2][c]:
                candy_type = grid[r][c]
                top = r
                bottom = r + 2
                while top > 0 and grid[top-1][c] == candy_type:
                    top -= 1
                while bottom < ROWS - 1 and grid[bottom+1][c] == candy_type:
                    bottom += 1
                matched.update([(row, c) for row in range(top, bottom+1)])
    
    return matched

# Apply gravity
def apply_gravity():
    for c in range(COLS):
        col = [st.session_state.grid[r][c] for r in range(ROWS)]
        col = [candy for candy in col if candy != ""]
        missing = ROWS - len(col)
        new_col = [random.choice(CANDIES) for _ in range(missing)] + col
        for r in range(ROWS):
            st.session_state.grid[r][c] = new_col[r]

# Handle game state changes
def process_game_state():
    if st.session_state.processing:
        if st.session_state.effect_type == "match":
            # Clear matched candies after showing effect
            for r, c in st.session_state.effect_positions:
                st.session_state.grid[r][c] = ""
            st.session_state.effect_positions = []
            apply_gravity()
            
            # Check for new matches
            new_matches = find_matches()
            if new_matches:
                st.session_state.effect_positions = list(new_matches)
                st.session_state.effect_type = "match"
                st.session_state.score += len(new_matches) * 10
            else:
                st.session_state.processing = False
                if st.session_state.score >= TARGET_SCORE:
                    st.session_state.game_over = True
                    st.balloons()

# Render the game board
def render_board():
    for r in range(ROWS):
        cols = st.columns(COLS)
        for c in range(COLS):
            candy = st.session_state.grid[r][c]
            if (r, c) in st.session_state.effect_positions and st.session_state.effect_type == "match":
                candy = "✨"  # Show sparkle effect for matched candies
            
            key = f"{r}_{c}"
            button_label = f"{candy}" if candy else " "
            
            # Determine button style
            button_style = ""
            if (r, c) in st.session_state.selected:
                button_style = "selected"
            elif (r, c) in st.session_state.effect_positions:
                button_style = "matched"
            
            # Create a custom button
            candy_color = CANDY_COLORS.get(st.session_state.grid[r][c], "#FFFFFF") if candy != "✨" else "#FFD700"
            button_html = f"""
            <button class="candy-button {button_style}" 
                    onclick="window.parent.document.getElementById('{key}').click()"
                    style="background-color: {candy_color};">
                {button_label}
            </button>
            """
            cols[c].markdown(button_html, unsafe_allow_html=True)
            
            # Hidden button for actual click handling
            if cols[c].button(button_label, key=key):
                handle_click(r, c)

# Handle candy selection
def handle_click(r, c):
    if st.session_state.game_over or st.session_state.processing:
        return
        
    if len(st.session_state.selected) < 2:
        st.session_state.selected.append((r, c))
    
    if len(st.session_state.selected) == 2:
        st.session_state.moves += 1
        (r1, c1), (r2, c2) = st.session_state.selected
        
        # Check if adjacent
        if abs(r1 - r2) + abs(c1 - c2) == 1:
            swap((r1, c1), (r2, c2))
            matches = find_matches()
            
            if matches:
                st.session_state.score += len(matches) * 10
                st.session_state.effect_positions = list(matches)
                st.session_state.effect_type = "match"
                st.session_state.processing = True
            else:
                # No match, swap back
                swap((r1, c1), (r2, c2))
        
        st.session_state.selected = []

# Scoreboard with progress bar
def render_scoreboard():
    progress = min(st.session_state.score / TARGET_SCORE, 1.0)
    st.markdown(f"""
    <div class="score-display">
        🏆 Score: {st.session_state.score} / {TARGET_SCORE} &nbsp; | &nbsp; 
        🎯 Moves: {st.session_state.moves}
    </div>
    <div style="margin: 0.5rem 0;">
        <progress value="{progress}" max="1" style="width: 100%; height: 10px; border-radius: 5px;"></progress>
    </div>
    """, unsafe_allow_html=True)

# Game over screen
def render_game_over():
    st.success(f"🎉 Congratulations! You reached the target score of {TARGET_SCORE} in {st.session_state.moves} moves!")
    if st.button("🎮 Play Again", key="play_again"):
        reset_game()

# Reset game state
def reset_game():
    st.session_state.grid = [[random.choice(CANDIES) for _ in range(COLS)] for _ in range(ROWS)]
    st.session_state.selected = []
    st.session_state.score = INITIAL_SCORE
    st.session_state.moves = 0
    st.session_state.game_over = False
    st.session_state.processing = False
    st.session_state.effect_positions = []
    st.session_state.effect_type = ""

# Main game layout
st.markdown("""
<div class="header">
    <h1 style="margin-bottom: 0;">🍬 Candy Crush Mini 🍭</h1>
    <p style="margin-top: 0.5rem; font-size: 1.1rem;">Match 3 or more candies to score points!</p>
</div>
""", unsafe_allow_html=True)

render_scoreboard()

if st.session_state.game_over:
    render_game_over()
else:
    process_game_state()
    render_board()

# Footer and controls
st.markdown("---")
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("""
    <div class="footer">
        <p>Match 3 or more candies of the same type to score points.<br>
        Click on adjacent candies to swap them.</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    if st.button("🔄 Restart Game", key="restart", help="Start a new game", use_container_width=True):
        reset_game()