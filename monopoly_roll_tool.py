import streamlit as st
import itertools
from collections import Counter
import pandas as pd

# --- Page setup ---
st.set_page_config(page_title="Monopoly GO! Roll Strategy Tool", layout="wide")
st.title("🎲 Monopoly GO! Roll Probability & Multiplier Tool")

# --- Cached dice probability map ---
@st.cache_data
def get_probability_map():
    dice_rolls = list(itertools.product(range(1, 7), repeat=2))
    sum_counts = Counter(sum(r) for r in dice_rolls)
    return {s: c / len(dice_rolls) for s, c in sum_counts.items()}

probability_map = get_probability_map()

# --- Multiplier logic ---
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
    else:
        return "1"

# --- Initialize session state ---
if "log_df" not in st.session_state:
    st.session_state.log_df = pd.DataFrame(columns=["Roll", "Hit", "Multiplier", "Note"])
if "tiles" not in st.session_state:
    st.session_state.tiles = []
if "prob" not in st.session_state:
    st.session_state.prob = 0.0
if "suggestion" not in st.session_state:
    st.session_state.suggestion = "1"

# --- Tile Input and Manual Trigger ---
st.subheader("🎯 Target Tile Distance Setup")
with st.form("tile_form"):
    tile_input = st.text_input("Enter target distances (comma-separated, e.g. 2,3,7)", value="")

    calc_btn = st.form_submit_button("🔄 Calculate Probability")

    if calc_btn:
        try:
            tiles = sorted({
                int(x.strip())
                for x in tile_input.split(",")
                if x.strip().isdigit() and 2 <= int(x) <= 12
            })
        except:
            tiles = []

        st.session_state.tiles = tiles
        st.session_state.prob = sum(probability_map.get(t, 0) for t in tiles)
        st.session_state.suggestion = refined_multiplier(st.session_state.prob)

# --- Probability Display ---
st.subheader("📊 Probability & Multiplier")
if st.session_state.tiles:
    st.success(f"🧮 Landing Probability: {st.session_state.prob * 100:.2f}%")
    st.info(f"🎯 Suggested Multiplier: x{st.session_state.suggestion}")
else:
    st.warning("Please enter tile numbers between 2–12 above and press 'Calculate'.")

# --- Roll & Log Section ---
st.subheader("📝 Roll Logging")

roll = st.selectbox("🎲 Roll outcome (2–12)", list(range(2, 13)))
auto_hit = roll in st.session_state.tiles
hit = st.radio(
    "🎯 Did you hit your target tile?",
    ["Yes", "No"],
    index=0 if auto_hit else 1,
    horizontal=True
)

note_options = [""] + sorted([
    "Chance", "Chance to Railroad-Bankrupt Heist", "Chance to Railroad-Large Heist",
    "Chance to Railroad-Mega Heist", "Chance to Railroad-Small Heist",
    "Chance to Railroad-Shutdown-Blocked", "Chance to Railroad-Shutdown-Success",
    "Community Chest", "Corner", "Jail-Fail", "Jail-Success",
    "Pick-Up", "Railroad-Bankrupt Heist", "Railroad-Large Heist",
    "Railroad-Mega Heist", "Railroad-Small Heist",
    "Railroad-Shutdown-Blocked", "Railroad-Shutdown-Success",
    "Shield", "Tax Tile", "Utilities",
])

# --- Log entry form ---
with st.form("log_form", clear_on_submit=True):
    multiplier_options = ["1", "2", "5", "10", "20", "50", "100", ">100"]
    multiplier = st.selectbox("🎲 Multiplier used", multiplier_options, index=multiplier_options.index(st.session_state.suggestion))
    note = st.selectbox("📝 Note (optional)", note_options, index=0)
    submit = st.form_submit_button("Log Entry")

if submit:
    new_row = {"Roll": roll, "Hit": hit, "Multiplier": multiplier, "Note": note}
    st.session_state.log_df = pd.concat(
        [st.session_state.log_df, pd.DataFrame([new_row])],
        ignore_index=True
    )
    st.success("✅ Roll logged locally!")

# --- Display log history and CSV download ---
if not st.session_state.log_df.empty:
    with st.expander("🧾 Roll History", expanded=True):
        st.dataframe(st.session_state.log_df)

        @st.cache_data
        def make_csv(df):
            return df.to_csv(index=False).encode("utf-8")

        csv = make_csv(st.session_state.log_df)
        st.download_button("📥 Download CSV", data=csv, file_name="monopoly_roll_log.csv", mime="text/csv")

st.markdown("---\nMade with 💡 for Monopoly GO! grinders.")
