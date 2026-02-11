# Dungeon Master AI

Dungeon Master AI is an AI-powered interactive storytelling application inspired by tabletop role-playing games such as Dungeons & Dragons. The system acts as a dynamic game master, generating story progression, character interactions, and scenario outcomes based on player input.

This project focuses on combining AI-driven narrative generation with structured game mechanics to simulate an engaging role-playing experience.

## Project Overview

Dungeon Master AI allows users to:

- Create a character (class, race, and basic attributes)
- Engage in interactive story progression
- Make decisions that influence narrative outcomes
- Experience AI-generated descriptions and events

The application is designed to run locally and emphasizes structured prompts, controlled outputs, and consistent game logic rather than purely free-form storytelling.

## Key Features

- AI-Generated Storytelling: Dynamically generates narrative responses based on player actions.
- Character Creation System: Supports player-defined class and race selection.
- Structured Output Handling: Uses controlled response formats to maintain game stability.
- Image Prompt Integration: Generates visual prompts based on character description.
- Fully Local Execution: Designed to run without external deployment infrastructure.

## Repository Structure

- `dunegon.py` – Core application logic and AI interaction handling.
- `requirements.txt` – Lists project dependencies.
- `README.md` – Project documentation.

## Installation

```bash
git clone https://github.com/Sabeer65/Dungeon-master-AI.git
cd Dungeon-master-AI
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
streamlit run dungeon.py
```

Steps:

1. Create a character by selecting class and race.
2. Begin the adventure.
3. Enter actions or decisions in natural language.
4. Receive AI-generated story progression and outcomes.

## Core System Design

The application combines:

- Prompt Engineering to control narrative direction
- Structured data parsing to maintain game state
- Rule-based logic to simulate consequences
- Dynamic description generation for immersive storytelling

The goal is to balance creative AI responses with predictable and manageable gameplay mechanics.

## Current Limitations

- Game rules are loosely enforced and not strictly bound to official rulebooks.
- Inventory interactions are primarily text-based.
- Character visuals may change between generations due to prompt variability.
- Error handling can be improved for edge cases and connectivity failures.

## Future Improvements

### Visual Enhancements

- Character Consistency: Implement fixed descriptions and controlled seed usage to prevent visual inconsistencies across generations.
- Dynamic Description Updates: Automatically modify image prompts based on the user’s selected class or race to reflect character changes accurately.

### Game Mechanics Improvements

- Interactive Inventory System: Convert inventory lists into interactive controls that allow players to actively use items (e.g., consuming a potion restores health).
- Stat-Based Consequences: Enforce meaningful attribute effects, including triggering a game-over sequence when health reaches zero.

### AI Intelligence Improvements

- Rulebook-Based Retrieval (RAG): Integrate a rulebook file into the system so the AI references structured gameplay rules instead of relying solely on generated responses.
- Strict Structured Output Mode: Implement advanced parsing and validation to prevent crashes caused by improperly formatted AI responses.

### Workflow and Professional Development

- Git Branching Strategy: Adopt feature-branch workflows instead of editing directly on the main branch to improve development safety.
- Improved Error Handling: Add user-friendly fallback messages when AI responses fail or connectivity issues occur.
- Mobile Layout Optimization: Improve sidebar organization and visual layout for better usability on smaller screens.

## Learning Outcomes

This project demonstrates:

- Advanced prompt engineering techniques
- State management in interactive AI applications
- Structured output parsing and validation
- Combining narrative AI with rule-based mechanics

## License

This project is open-source and intended for educational and experimental purposes.

