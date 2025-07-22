import streamlit as st
import itertools
from collections import Counter
import pandas as pd
import os

st.set_page_config(page_title="Monopoly GO! Roll Strategy Tool", layout="centered")
st.title("🎲 Monopoly GO! Roll Probability & Multiplier Tool")

# Introduction
st.markdown("""
This tool helps you calculate your chances of landing on specific tiles during events and suggests the best dice multiplier to use in **Monopoly GO!**.

👉 Select your target tiles (2–12 spaces away), and the app will show:
- **Landing probability**
- **Suggested multiplier**
- **Log your roll outcomes**
""")

# --- Dice probabilities ---
dice_rolls = list(itertools.product(range(1, 7), repeat=2))
roll_sums = [sum(roll) for roll in dice_rolls]
total_rolls = len(dice_rolls)
sum_counts = Counter(roll_sums)
probability_map = {total: count / total_rolls for total, count in sum_counts.items()}

# --- Multiplier logic (updated) ---
def refined_multiplier(prob):
    if prob >= 0.75:
        return ">100"
    elif prob >= 0.60:
        return "100"
    elif prob >= 0.50:
        return "50"
    elif prob >= 0.40:
        return "20"
    elif prob >= 0.30:
        return "10"
    elif prob >= 0.20:
        return "5"
    else:
        return "1"

# --- Session state defaults ---
if "reset_tiles" not in st.session_state:
    st.session_state.reset_tiles = False
if "tile_selector" not in st.session_state:
    st.session_state.tile_selector = [6, 7, 8]
if "log_df" not in st.session_state:
    st.session_state.log_df = pd.DataFrame(columns=["Roll", "Hit", "Multiplier", "Note"])

# --- Reset tile selections if needed ---
if st.session_state.reset_tiles:
    st.session_state.tile_selector = []
    st.session_state.reset_tiles = False

# --- Tile selection ---
st.subheader("🎯 Select your target tile distances (2 to 12 tiles ahead)")
tile_options = list(range(2, 13))
selected_tiles = st.multiselect(
    "Choose tile distances (e.g. 6, 8, 9)",
    tile_options,
    default=st.session_state.tile_selector,
    key="tile_selector"
)

# --- Calculate probability and suggested multiplier ---
if selected_tiles:
    prob = sum(probability_map.get(tile, 0) for tile in selected_tiles)
    suggestion = refined_multiplier(prob)
    st.success(f"🧮 **Landing Probability:** {round(prob * 100, 2)}%")
    st.info(f"🎯 **Suggested Multiplier:** x{suggestion}")
else:
    prob = 0
    suggestion = "1"
    st.warning("Please select at least one tile.")

# --- Logging section ---
st.subheader("📋 Log Your Roll Results")

# Multiplier select defaults
multiplier_options = ["1", "2", "5", "10", "20", "50", "100", ">100"]
suggested_index = multiplier_options.index(suggestion)

# Roll input
roll = st.selectbox("🎲 Roll outcome (2–12)", list(range(2, 13)))

# Auto-determine if hit
auto_hit = "Yes" if roll in selected_tiles else "No"

# --- Logging form ---
with st.form("log_form"):
    hit = st.radio("🎯 Did you hit a target tile?", ["Yes", "No"], index=0 if auto_hit == "Yes" else 1)
    multiplier = st.selectbox("🎲 Multiplier used", multiplier_options, index=suggested_index)
    note = st.text_input("📝 Notes (optional)")
    submit = st.form_submit_button("Log Entry")

# --- Handle log entry ---
if submit:
    new_row = {
        "Roll": roll,
        "Hit": hit,
        "Multiplier": multiplier,
        "Note": note
    }
    st.session_state.log_df = pd.concat([st.session_state.log_df, pd.DataFrame([new_row])], ignore_index=True)
    st.success("✅ Roll logged!")
    st.session_state.reset_tiles = True
    st.rerun()

# --- Display roll history ---
if not st.session_state.log_df.empty:
    st.write("🧾 Roll History:")
    st.dataframe(st.session_state.log_df)

    csv = st.session_state.log_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", data=csv, file_name="monopoly_roll_log.csv", mime="text/csv")

# Footer
st.markdown("---\nMade with 💡 for Monopoly GO! grinders.")
