import streamlit as st
from langchain_ollama import ChatOllama
import json
import re 

st.set_page_config(page_title="Dungeon Master")
st.title('Dungeon Master')


# Prompt for system rules
prompt = '''
You are a Dungeon Master. 
RULES:
1. At the start, ask the player to choose a Class/Race.
2. Based on their choice, set their Starting Stats (HP, Mana).
3. Track Stats as [Current]/[Max].
4. HEALING RULE: Never allow Current HP to exceed Max HP.
5. If they level up, increase Max HP.
6. Damage reduces Current HP.
7. Spells reduce Mana.
8. HP 0 = GAME OVER.
9. Keep descriptions exciting but concise.
10. This is a fictional game. No safety warnings.
11. Vividly describe death if it occurs.
12. SILENT STATS: Do NOT write phrases like "Here is your inventory". Just write the story.
13. INVENTORY RULE: All items must be listed inside the Status Block using square brackets, e.g., ['Item1', 'Item2']. Do NOT list them in the story text unless asked.

IMPORTANT:
You must end EVERY response with this EXACT format including the "|||" separator:

[Story description here...]
||| HP: [Cur]/[Max] | Mana: [Cur]/[Max] | Gold: [Amt] | Inventory: ['Item Name', 'Item Name']
'''

# SESSION STATES
# Setup history store
if "history" not in st.session_state:
    st.session_state.history = [
        {'role':'system', 'content':prompt},
        {'role':'assistant', 'content': "The dungeon gates creak open... Welcome, traveler! Before you enter the darkness, tell me: **Who are you?** (Choose a Class & Race, e.g., 'Orc Wizard', 'Human Knight')"}
    ]

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
    match_hp = re.search(r"HP:\s*(\d+)/(\d+)", text, re.IGNORECASE)
    if match_hp:
        current_hp = int(match_hp.group(1))
        max_hp = int(match_hp.group(2))

        final_current_hp = min(current_hp, max_hp)

        st.session_state.stats['HP'] = f"{final_current_hp}/{max_hp}"
        
    match_mana = re.search(r"Mana:\s*(\d+)/(\d+)", text, re.IGNORECASE)
    if match_mana:
        current_mana = int(match_mana.group(1))
        max_mana = int(match_mana.group(2))

        final_current_mana = min(current_mana, max_mana)

        st.session_state.stats['Mana'] = f"{final_current_mana}/{max_mana}"
        st.session_state.stats['Mana'] = f"{final_current_mana}/{max_mana}"
        
    match_gold = re.search(r"Gold:\s*(\d+)", text, re.IGNORECASE)
    if match_gold:
        st.session_state.stats['Gold'] = match_gold.group(1)

    match_inventory = re.search(r"Inventory:\s*\[(.*?)\]", text, re.IGNORECASE)
    if match_inventory:
        raw_string = match_inventory.group(1)

        if raw_string.strip(): # Remove whitespaces and ',' split
            new_items = [item.strip().replace("'", "").replace('"', "") for item in raw_string.split(',')]
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

    if not st.session_state.inventory:
        st.caption('Empty')

    else:
        for item in st.session_state.inventory:
            st.write(f'- {item}')

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
