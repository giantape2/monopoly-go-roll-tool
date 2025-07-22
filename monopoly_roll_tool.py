import streamlit as st
import itertools
from collections import Counter
import pandas as pd

# --- Page setup ---
st.set_page_config(page_title="Monopoly GO! Roll Strategy Tool", layout="centered")
st.title("🎲 Monopoly GO! Roll Probability & Multiplier Tool")

# --- Dice probabilities ---
dice_rolls = list(itertools.product(range(1,7), repeat=2))
sum_counts = Counter(sum(r) for r in dice_rolls)
total_rolls = len(dice_rolls)
probability_map = {s: c/total_rolls for s, c in sum_counts.items()}

def refined_multiplier(prob):
    if prob >= 0.75: return ">100"
    elif prob >= 0.60: return "100"
    elif prob >= 0.50: return "50"
    elif prob >= 0.40: return "20"
    elif prob >= 0.30: return "10"
    elif prob >= 0.20: return "5"
    else: return "1"

# --- Session state for log ---
if "log_df" not in st.session_state:
    st.session_state.log_df = pd.DataFrame(columns=["Roll","Hit","Multiplier","Note"])
if "note_select" not in st.session_state:
    st.session_state.note_select = ""

# --- Manual tile entry ---
tile_input = st.text_input("🎯 Enter target distances (comma-separated, e.g. 2,3,7)")
tiles = sorted({int(x.strip()) for x in tile_input.split(",")
                if x.strip().isdigit() and 2 <= int(x) <= 12})

if tiles:
    prob = sum(probability_map.get(t,0) for t in tiles)
    suggestion = refined_multiplier(prob)
    st.success(f"🧮 Landing Probability: {prob*100:.2f}%")
    st.info(f"🎯 Suggested Multiplier: x{suggestion}")
else:
    prob, suggestion = 0, "1"
    st.warning("Please enter at least one valid tile distance (2–12).")

# --- Note options (alphabetical) ---
note_options = sorted([
    "Chance",
    "Chance to Railroad-Heist",
    "Chance to Railroad-Shutdown",
    "Community Chest",
    "Corner",
    "Jail",
    "Pick-Up",
    "Railroad-Heist",
    "Railroad-Shutdown",
    "Shield",
    "Tax Tile",
    "Utilities",
])

# --- Logging form ---
with st.form("log_form"):
    roll = st.selectbox("🎲 Roll outcome (2–12)", list(range(2,13)))
    auto_hit = "Yes" if roll in tiles else "No"
    hit = st.radio("🎯 Did you hit a target tile?", ["Yes","No"],
                   index=0 if auto_hit=="Yes" else 1)
    multiplier_options = ["1","2","5","10","20","50","100",">100"]
    multiplier = st.selectbox("🎲 Multiplier used", multiplier_options,
                              index=multiplier_options.index(suggestion))
    note = st.selectbox("📝 Note", note_options, key="note_select")
    submit = st.form_submit_button("Log Entry")

if submit:
    new_row = {"Roll": roll, "Hit": hit, "Multiplier": multiplier, "Note": note}
    st.session_state.log_df = pd.concat(
        [st.session_state.log_df, pd.DataFrame([new_row])],
        ignore_index=True
    )
    st.success("✅ Roll logged!")
    # Clear note selection
    st.session_state.note_select = ""
    # Clear the tile input field
    st.experimental_rerun()

# --- Display roll history ---
if not st.session_state.log_df.empty:
    st.write("🧾 Roll History:")
    st.dataframe(st.session_state.log_df)
    csv = st.session_state.log_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", data=csv,
                       file_name="monopoly_roll_log.csv",
                       mime="text/csv")

st.markdown("---\nMade with 💡 for Monopoly GO! grinders.")
