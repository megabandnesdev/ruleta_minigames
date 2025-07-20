# Single Player Mode Documentation

## Overview

This implementation adds a new single player game mode to the existing roulette game, providing an alternative gameplay experience with 6 different game mode options.

## Features

### Single Player Options
The game now includes 6 single player game modes defined in `SINGLEPLAYER_OPTIONS`:
1. **Adventure Mode** - Story-driven gameplay
2. **Time Attack** - Speed-based challenges  
3. **Survival Mode** - Endurance gameplay
4. **Puzzle Challenge** - Logic-based puzzles
5. **Boss Rush** - Consecutive boss battles
6. **Training Mode** - Practice and learning

### Game Mode Switching
- Press **M** to switch between Roulette and Single Player modes
- The current mode is displayed at the bottom of the screen
- Game state is preserved when switching modes

### Single Player Selection Process
1. **Display**: Shows a 3x2 grid of all 6 game mode options
2. **Activation**: Press **SPACE** to start the selection process
3. **Selection Animation**: Options are highlighted sequentially for 5 seconds
4. **Random Selection**: After 5 seconds, one option is randomly selected
5. **Result Display**: The selected option is highlighted in green

## Controls

### Main Game Controls
- **M** - Switch between Roulette and Single Player modes
- **R** - Reset current game mode
- **ESC** - Toggle fullscreen/windowed mode
- **SPACE** - Start selection process (Single Player mode)

### Single Player Mode Controls
- **SPACE** - Start selection process
- **SPACE** (during result) - Continue or reset selection
- **Double SPACE** - Quick reset during selection or result

## Technical Implementation

### New Files Created
- `singleplayer_selector.py` - Main single player selection logic
- `imagenes/singleplayer/stageselect-mm6-empty-with-selection-720p.png` - Background spritesheet

### Modified Files
- `game_config.py` - Added single player configuration options
- `game_state.py` - Added game mode management
- `main.py` - Integrated single player mode with existing game loop

### Configuration
```python
# Single player mode options - 6 different alternatives
SINGLEPLAYER_OPTIONS = [
    "Adventure Mode",
    "Time Attack",
    "Survival Mode", 
    "Puzzle Challenge",
    "Boss Rush",
    "Training Mode"
]

# Single player selection timing
TIEMPO_SELECCION_SINGLEPLAYER = 5000  # 5 seconds for random selection
TIEMPO_MOSTRAR_OPCION = 200  # Time to show each option during cycling
```

## Background Spritesheet

The single player mode uses a spritesheet located at:
`imagenes/singleplayer/stageselect-mm6-empty-with-selection-720p.png`

### Spritesheet Layout
- **Size**: 1080x720 pixels (scaled to fit screen)
- **Grid**: 3x2 layout (6 sections total)
- **Section Size**: 360x360 pixels each
- **Format**: PNG with transparency support

### Option Positions
1. Adventure Mode: (0, 0)
2. Time Attack: (360, 0)  
3. Survival Mode: (720, 0)
4. Puzzle Challenge: (0, 360)
5. Boss Rush: (360, 360)
6. Training Mode: (720, 360)

## Testing

Run the test script to verify functionality:
```bash
python3 test_singleplayer.py
```

The test will:
- Display the single player selection interface
- Auto-start selection after 3 seconds
- Show the selection process and result
- Allow manual testing with SPACE key

## Usage Example

1. Start the game: `python3 main.py`
2. Press **M** to switch to Single Player mode
3. Press **SPACE** to start the selection process
4. Watch as options are highlighted for 5 seconds
5. See the final selection highlighted in green
6. Press **SPACE** to continue or **R** to reset

## Integration with Existing Code

The single player mode integrates seamlessly with the existing roulette game:
- Uses the same asset management system
- Follows the same game state pattern
- Maintains consistent visual styling
- Preserves all existing functionality

## Future Enhancements

Potential improvements for the single player mode:
- Custom background music for selection
- Animation effects during selection
- Sound effects for option cycling
- Expanded game mode descriptions
- Save/load functionality for mode preferences