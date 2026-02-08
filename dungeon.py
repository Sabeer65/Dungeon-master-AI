import streamlit as st
from langchain_ollama import ChatOllama
import json
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
You are a Dungeon Master running an immersive, narrative-driven fantasy RPG.

ROLE:
- You are a STORYTELLER, not a game engine. 
- Do NOT output dice rolls, math calculations, or phrases like "Rolling for initiative" or "Skill check passed".
- Decide outcomes based on the player's class, stats, and logical narrative consequences.

GAME FLOW:
1. NARRATIVE FIRST: Write the story description.
   - Be descriptive, atmospheric, and engaging.
   - Describe combat viscerally (e.g., "The goblin's blade grazes your ribs," not "You take 5 damage").
   - If the player chose a Class/Race, customize the narration (e.g., Orcs are strong, Wizards are wise).
   
2. SEPARATOR: You MUST end the story with exactly this separator: ***JSON***

3. DATA: Immediately after the separator, output a SINGLE line of valid JSON.

DATA RULES (CRITICAL):
- **Damage/Healing:** Update the JSON stats to match the story. If you wrote that the player was hit, lower the HP in the JSON.
- **Visuals:** Provide a prompt for an image generator. Use "null" for mundane scenes.

JSON STRUCTURE:
{
    "stats": {
        "hp": "Current/Max",
        "mana": "Current/Max",
        "gold": 0
    },
    "inventory": ["Item Name", "Item Name"],
    "visual": "Description of the CURRENT scene for an image generator (or null)"
}

Example Turn:
User: I attack the wolf.
AI: You lunge forward, driving your steel into the beast's flank. It yelps and snaps at you, tearing into your leather armor with jagged teeth. Pain flares in your shoulder.
***JSON***
{"stats": {"hp": "25/30", "mana": "5/5", "gold": 10}, "inventory": ["Longsword"], "visual": "A wolf snapping at a warrior in a forest"}

IMPORTANT:
* Write the json block everytime without fail
* Do not stop generating until json is completed.
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

# Setup Image Store
if 'current_image' not in st.session_state:
    st.session_state.current_image = None

# Initialise Model
llm = ChatOllama(model='llama3.2', temperature=0.5)

# Helper Functions


def generate_image(prompt_text):

    API_TOKEN = os.getenv("HF_API_KEY")

    if not API_TOKEN:
        st.error("Error: HF_API_TOKEN not found in .env")
        return None

    API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    payload = {"inputs": f"fantasy art, dnd style, high quality, {prompt_text}"}

    try:
        print(f"Generating image for: {prompt_text}") # DEBUG LINE
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            print("Image generated successfully!") # DEBUG LINE
            return response.content
        else:
            # This prints the error to your terminal so you can read it
            print(f"Error {response.status_code}: {response.text}") 
            st.error(f"Image Gen Failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"Connection Error: {e}")
        st.error(f"Connection Error: {e}")
        return None

def stream_turn(llm, messages):
    text_placeholder = st.empty()
    full_response = ""
    json_part = ""
    story_part = ""

    for chunk in llm.stream(messages):
        full_response += chunk.content

        print(chunk.content, end="", flush=True) # DEBUG LINE

        if '***JSON***' in full_response:
            parts = full_response.split('***JSON***') 
            story_part = parts[0]
            
            if len(parts) > 1:
                json_part = parts[1]
        else:
            story_part = full_response
    
        text_placeholder.markdown(story_part + "▌")
    
    text_placeholder.markdown(story_part)

    print("\n--- END OF TURN ---\n") # DEBUG LINE

    return story_part, json_part

def process_turn_data(json_str):

    try:
        data = json.loads(json_str)

        stats = data.get('stats', {})
        inventory = data.get('inventory', [])
        visual_prompt = data.get('visual', None)

        new_hp = stats.get('hp')
        new_mana = stats.get('mana')
        new_gold = stats.get('gold')

        if new_hp: st.session_state.stats['HP'] = new_hp
        if new_mana: st.session_state.stats['Mana'] = new_mana
        if new_gold is not None: st.session_state.stats['Gold'] = str(new_gold)

        st.session_state.inventory = inventory

        image_byte = None
        if visual_prompt and visual_prompt != "null":
            with st.spinner(f"Visualising: {visual_prompt}"):
                image_byte = generate_image(visual_prompt)

    except Exception as e:
        st.warning(f'Dungeon master got distracted. Stats might not update this turn: {e}')
        return None
    
    return image_byte

# SIDEBAR
with st.sidebar:

    st.header("Visuals")

    if st.session_state.current_image:
        image = Image.open(io.BytesIO(st.session_state.current_image))
        st.image(image, caption="Current Scene", use_container_width=True)
    else:
        st.info("No image generated yet")
        
    st.divider() 

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
    if '***JSON***' in display_text:
        display_text = display_text.split('***JSON***')[0] 

    with st.chat_message(msg['role']):
        st.write(display_text)

# MAIN GAME LOOP

user_input = st.chat_input('What do you want to do?')

if user_input:

    st.session_state.history.append({'role':'user', 'content':user_input})
    with st.chat_message('user'):
        st.write(user_input)

    # AI response

    story_text, json_str = stream_turn(llm, st.session_state.history)

    new_image = None

    if json_str:
        new_image = process_turn_data(json_str)
    
    if new_image:
            st.session_state.current_image = new_image

    full_log = story_text + '***JSON***' + json_str
    st.session_state.history.append({'role':'assistant', 'content':full_log})

    st.rerun()