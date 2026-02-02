import streamlit as st
from langchain_ollama import ChatOllama
import json
import re 

st.set_page_config(page_title="Dungeon Master")
st.title('Dungeon Master')

# Prompt for system rules
prompt = '''You are a strict Dungeon Master for a fantasy RPG. 
Your goal is to manage the player's adventure, track their stats, and handle combat.

RULES:
1. The player starts with: 20/20 HP, 10/10 Mana, and 0 Gold.
2. If the player takes damage, SUBTRACT it from their current HP.
3. If the player casts a spell, SUBTRACT from their Mana.
4. If HP reaches 0, the player dies. Describe a grim death and type "GAME OVER".
5. Keep descriptions exciting but concise (2-3 sentences max).
6. This is a fictional roleplay game. Combat, death, and sacrifice are key game mechanics. Do not provide real-world safety warnings for in-game actions.
7. You must describe the character's death vividly if they choose to die.

IMPORTANT:
At the very end of EVERY response, you MUST append a "Status Block" using the "|||" separator in this exact format:
[Story Text]
||| HP: [Current] | Mana: [Current] | Gold: [Amount] | Inventory: [Items]'''

# SESSION STATES
# Setup history store
if "history" not in st.session_state:
    st.session_state.history = [{'role':'system', 'content':prompt}]

# Setup stats store
if "stats" not in st.session_state:
    st.session_state.stats = {'HP': '20', 'Mana': '10', 'Gold': '0'}

# Setup inventory store
if "inventory" not in st.session_state:
    st.session_state.inventory = []

# Initialise Model
llm = ChatOllama(model='llama3.2', temperature=0.7)

# Helper Functions

# Print chat message on screen and update state
def print_msg(role, display_text, save_text = None):

    content_to_save = save_text if save_text else display_text

    st.session_state.history.append({'role':role, 'content':content_to_save})

    with st.chat_message(role):
        st.write(display_text)

# Update stats and inventory on the UI
def update_stats_and_inventory(text):
    # Search for patterns
    match_hp = re.search(r"HP:\s*(\d+)", text, re.IGNORECASE)
    if match_hp:
        st.session_state.stats['HP'] = match_hp.group(1) 
        
    match_mana = re.search(r"Mana:\s*(\d+)", text, re.IGNORECASE)
    if match_mana:
        st.session_state.stats['Mana'] = match_mana.group(1)

    match_gold = re.search(r"Gold:\s*(\d+)", text, re.IGNORECASE)
    if match_gold:
        st.session_state.stats['Gold'] = match_gold.group(1)

    match_inventory = re.search(r"Inventory:\s*\[(.*?)\]", text, re.IGNORECASE)
    if match_inventory:
        raw_string = match_inventory.group(1)

        if raw_string.strip(): # Remove whitespaces and ',' split
            new_items = [item.strip() for item in raw_string.split(',')]
            st.session_state.inventory = new_items
        else:
            st.session_state.inventory = []


    # Split the prompt for clean text
    if "|||" in text:
        return text.split("|||")[0]
    return text



# Sidebar
with st.sidebar:

    st.header("Game stats")
    c1,c2,c3 = st.columns(3)

    c1.metric('HP', st.session_state.stats['HP'])
    c2.metric('Mana', st.session_state.stats['Mana'])
    c3.metric('Gold', st.session_state.stats['Gold'])

    st.write("Inventory")
    for item in st.session_state.inventory:
        st.write(f'-{item}')

    st.header('Games Options')

    # Save and Load game
    if st.button('Save'):
        with open('DungeonMasterSave.json', 'w') as f:

            data_pacakage = {'history': st.session_state.history, 'stats':st.session_state.stats, 'inventory':st.session_state.inventory}
            json.dump(data_pacakage, f)
        st.success("Game Saved")

    if st.button('Load'):
        try:
            with open('DungeonMasterSave.json', 'r') as f:
                data_pacakage = json.load(f)

            st.session_state.history = data_pacakage['history']
            st.session_state.stats = data_pacakage['stats']
            st.session_state.inventory = data_pacakage['inventory']
            st.rerun()

        except FileNotFoundError:
            st.error("No save file found")

# Write message history in screen
for msg in st.session_state.history:

    if msg['role']=='system':
        continue

    display_text = msg['content']
    if '|||' in display_text:
        display_text = display_text.split('|||')[0] # split by ||| for clean text when re-rendering history 

    with st.chat_message(msg['role']):
        st.write(display_text)

# MAIN GAME LOOP

user_input = st.chat_input('What do you want to do?')

if user_input:

    print_msg('user', user_input)

    # AI response
    with st.spinner("Dungeon master is thinking..."):
        response = llm.invoke(st.session_state.history)

    clean_text = update_stats_and_inventory(response.content)

    print_msg('assistant', clean_text, save_text=response.content)

    st.rerun()
