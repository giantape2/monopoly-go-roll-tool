import streamlit as st
import itertools
from collections import Counter

st.set_page_config(page_title="Monopoly GO! Roll Strategy Tool", layout="centered")

st.title("🎲 Monopoly GO! Roll Probability & Multiplier Tool")

# Intro
st.markdown("""
This tool helps you calculate your chances of landing on specific tiles during events and suggests the best dice multiplier to use in **Monopoly GO!**.

👉 Simply choose the tiles you're targeting (2–12 spaces away), and you'll see your:
- **Probability of landing**
- **Suggested dice multiplier**
""")

# Dice roll outcome probabilities
dice_rolls = list(itertools.product(range(1, 7), repeat=2))
roll_sums = [sum(roll) for roll in dice_rolls]
total_rolls = len(dice_rolls)
sum_counts = Counter(roll_sums)
probability_map = {total: count / total_rolls for total, count in sum_counts.items()}

# Multiplier suggestion logic
def refined_multiplier(prob):
    if prob >= 0.60:
        return ">100"
    elif prob >= 0.50:
        return "100"
    elif prob >= 0.40:
        return "50"
    elif prob >= 0.30:
        return "20"
    elif prob >= 0.20:
        return "10"
    elif prob >= 0.10:
        return "5"
    elif prob >= 0.05:
        return "2"
    else:
        return "1"

# User selects target tiles
st.subheader("🎯 Select your target tile distances (2 to 12 tiles ahead)")
tile_options = list(range(2, 13))
selected_tiles = st.multiselect("Choose tile distances (e.g. 6, 8, 9)", tile_options, default=[6, 7, 8])

# Calculate probability
if selected_tiles:
    prob = sum(probability_map.get(tile, 0) for tile in selected_tiles)
    suggestion = refined_multiplier(prob)
    st.success(f"🧮 **Landing Probability:** {round(prob * 100, 2)}%")
    st.info(f"🎯 **Suggested Multiplier:** x{suggestion}")
else:
    st.warning("Please select at least one tile.")

# Footer
st.markdown("""
---
Made with 💡 for Monopoly GO! strategy players.
""")
