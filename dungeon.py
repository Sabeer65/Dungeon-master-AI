import streamlit as st
from langchain_ollama import ChatOllama
import json
import re 
import requests
import io 
from PIL import Image
import os 
from dotenv import load_dotenv

st.set_page_config(page_title="Dungeon Master")
st.title('Dungeon Master')

load_dotenv()

# Prompt for system rules
prompt = '''
You are a Dungeon Master running a turn-based fantasy RPG.

ROLE:
- You narrate the world, control all NPCs, enemies, and outcomes.
- The player controls ONLY their decisions and dialogue.

GAME FLOW:
1. If the player has not chosen a Class and Race, ask them to choose one.
2. Once chosen, silently initialize stats based on Class/Race.
3. Each response advances the story by ONE meaningful step.
4. Always end by prompting the player for their next action.

STATS RULES:
- Stats must always be shown as Current/Max.
- HP must never exceed Max HP.
- Mana must never exceed Max Mana.
- If HP reaches 0, the character is dead. Do not prevent this.
- Level-ups may increase Max HP or Max Mana.
- Gold is a single integer.

INVENTORY RULES:
- Inventory must be shown as a Python-style list: ['Item A', 'Item B'].
- Only include items the player actually has.
- Empty inventory must be shown as [].

VISUAL RULES:
- Decide if the scene deserves an image.
- If the scene introduces a NEW area, monster, item, or dramatic moment:
  - Write a single, static visual description suitable for image generation.
- If the scene is mundane (talking, walking, inventory, simple actions):
  - Write exactly: None
- Do NOT use camera language (no “camera”, “zoom”, “angle”, “shot”).

OUTPUT FORMAT (MANDATORY):
You must ALWAYS end your response with this EXACT structure:

||| VISUAL: <description OR None> |||
HP: X/Y | Mana: A/B | Gold: N | Inventory: ['Item1', 'Item2']

IMPORTANT:
- Do NOT explain rules.
- Do NOT announce stats with phrases like “Here are your stats”.
- Do NOT include anything after the status line.
- Never break or reword the format.

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


def generate_image(prompt_text):

    API_TOKEN = os.getenv("HF_API_KEY")

    if not API_TOKEN:
        st.error("Error: HF_API_TOKEN not found in .env")
        return None

    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    payload = {"inputs": f"fantasy art, dnd style, high quality, {prompt_text}"}

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Image Gen Failed:  {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection Error{e}")
        return None

# Print chat message on screen and update state
def print_msg(role, display_text, save_text = None, image_data = None):

    content_to_save = save_text if save_text else display_text

    st.session_state.history.append({'role':role, 'content':content_to_save})

    with st.chat_message(role):
        st.write(display_text)
    
    if image_data:
        image = Image.open(io.BytesIO(image_data))
        st.image(image, caption = "Visualising the scene")

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

    match_visual = re.search(r"VISUAL:\s*(.*?)\s*\|\|\|", text, re.IGNORECASE)
    image_data = None

    if match_visual:
        visual_prompt = match_visual.group(1).strip()

        if visual_prompt and "None" not in visual_prompt:
            with st.spinner(f'Generating Image {visual_prompt}'):
                image_data = generate_image(visual_prompt)

    # Split the prompt for clean text
    if "|||" in text:
        clean_text = text.split("|||")[0]
    return clean_text, image_data


# SIDEBAR
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

    clean_text, new_image_bytes = update_stats_and_inventory(response.content)

    print_msg('assistant', clean_text, save_text=response.content, image_data=new_image_bytes)