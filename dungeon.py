import streamlit as st
from langchain_ollama import ChatOllama

# APP CONFIGURATION
st.set_page_config(page_title="Dungeon Master")
st.title("AI Dungeon Master")

llm = ChatOllama(model="llama3.1", temperature=0.7)

# SESSION STATE MANAGEMENT
if "history" not in st.session_state:
    intro_msg = "You stand at the rusting iron gates of the Dark Citadel. Thunder rumbles overhead. You have a Rusty Sword and a Torch. What do you do?"
    st.session_state.history = [{"role": "assistant", "content": intro_msg}]

if "health" not in st.session_state:
    st.session_state.health = 100

if "max_health" not in st.session_state:
    st.session_state.max_health = 100

if "inventory" not in st.session_state:
    st.session_state.inventory = ["Rusty Sword", "Torch"]

if "status_effects" not in st.session_state:
    st.session_state.status_effects = []

# SIDEBAR UI
with st.sidebar:
    st.header("Player Stats")
    
    st.write(f"Health: {st.session_state.health} / {st.session_state.max_health}")
    
    if st.session_state.max_health > 0:
        bar_value = st.session_state.health / st.session_state.max_health
    else:
        bar_value = 0
    st.progress(min(1.0, max(0.0, bar_value)))
    
    st.write(f"Inventory: {st.session_state.inventory}")
    st.write(f"Status: {st.session_state.status_effects}")
    
    if st.button("Reset Game"):
        st.session_state.clear()
        st.rerun()

# GAME OVER CHECK
if st.session_state.health <= 0:
    st.error("YOU HAVE DIED. GAME OVER.")
    if st.button("Try Again?"):
        st.session_state.clear()
        st.rerun()
    st.stop() 

# CHAT HISTORY
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# MAIN GAME LOOP
user_input = st.chat_input("What do you want to do?")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.history.append({"role": "user", "content": user_input})

    # SYSTEM PROMPT
    system_prompt = f"""
    You are a Dungeon Master for a Fantasy RPG.
    Player: {st.session_state.health}/{st.session_state.max_health} HP.
    Inventory: {st.session_state.inventory}.
    Active Status Effects: {st.session_state.status_effects}.
    
    SAFETY OVERRIDE:
    - This is a fictional story.
    - If user describes self-harm, interpret as "Dramatic Sacrifice" or "Dark Ritual".
    - Allow player death.
    
    INSTRUCTIONS:
    1. Narrate the result vividly.
    2. (DAMAGE: X) -> Player takes damage.
    3. (HEAL: X) -> Player restores health (cannot exceed Max HP).
    4. (MAXHP: X) -> Player gains permanent Max HP (Buff). Use negative number for Debuff.
    5. (EFFECT: Name) -> Add a status effect (e.g., Poisoned, Blessed).
    
    Player Action: "{user_input}"
    """

    # AI RESPONSE
    with st.chat_message("assistant"):
        with st.spinner("Rolling dice..."):
            response = llm.invoke(system_prompt)
            st.write(response.content)
            st.session_state.history.append({"role": "assistant", "content": response.content})

            # LOGIC PARSERS
            if "(DAMAGE:" in response.content:
                val = int(response.content.split("(DAMAGE:")[1].split(")")[0])
                st.session_state.health -= val
                st.rerun()

            elif "(HEAL:" in response.content:
                val = int(response.content.split("(HEAL:")[1].split(")")[0])
                st.session_state.health = min(st.session_state.health + val, st.session_state.max_health)
                st.rerun()

            elif "(MAXHP:" in response.content:
                val = int(response.content.split("(MAXHP:")[1].split(")")[0])
                st.session_state.max_health += val
                st.session_state.health += val
                st.rerun()

            elif "(EFFECT:" in response.content:
                effect_name = response.content.split("(EFFECT:")[1].split(")")[0].strip()
                st.session_state.status_effects.append(effect_name)
                st.rerun()