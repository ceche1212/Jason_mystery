import time
from datetime import timedelta
import streamlit as st

st.set_page_config(page_title="Find the Killer", page_icon="🕵️", layout="centered")

# ----- Config -----
COOLDOWN_SECONDS = 30

# ----- Helpers -----
def normalize_name(name: str) -> str:
    return " ".join(name.strip().lower().split())

KILLER = normalize_name("Miranda Priestly")
HITMAN = normalize_name("Jeremy Bowers")

# ----- Session State -----
if "cooldown_until_ts" not in st.session_state:
    st.session_state.cooldown_until_ts = None  # epoch seconds
if "guess_text" not in st.session_state:
    st.session_state.guess_text = ""
if "last_wrong_guess" not in st.session_state:
    st.session_state.last_wrong_guess = ""

def cooldown_active() -> bool:
    ts = st.session_state.cooldown_until_ts
    return ts is not None and time.time() < ts

def start_cooldown():
    st.session_state.cooldown_until_ts = time.time() + COOLDOWN_SECONDS

def clear_cooldown():
    st.session_state.cooldown_until_ts = None

# ----- UI -----
st.title("Did you find the killer?")
st.write("Enter the full name (first and last).")

# If cooling down: show progress + disabled UI and auto-refresh each second
if cooldown_active():
    remaining = max(0, int(st.session_state.cooldown_until_ts - time.time()))
    elapsed = COOLDOWN_SECONDS - remaining
    pct = int(100 * elapsed / COOLDOWN_SECONDS)

    st.info("Wrong guess — please wait before trying again.")
    st.progress(pct, text=f"{remaining} seconds remaining…")

    st.image("rookie.png", caption="Dont Make waste my time", width='stretch')

    # Disabled-looking input + button
    st.text_input(
        "Your answer",
        key="guess_text",
        placeholder="Input the killer first name and last name",
        help="Example: Jane Doe",
        disabled=True,
    )
    st.button("Check", disabled=True)
    st.caption("The button is disabled until the cooldown ends.")

    # Auto-update countdown and then clear UI
    if remaining > 0:
        time.sleep(1)
        st.rerun()
    else:
        clear_cooldown()
        st.rerun()

else:
    # Normal form (active when not cooling down)
    with st.form("guess_form", clear_on_submit=False):
        st.session_state.guess_text = st.text_input(
            "Your answer",
            value=st.session_state.guess_text,
            placeholder="Input the killer first name and last name",
            help="Example: Jane Doe",
        )
        submitted = st.form_submit_button("Check")

    if submitted:
        name = normalize_name(st.session_state.guess_text)

        if not name:
            st.warning("Please enter a full name.")
        elif name == KILLER:
            st.success(
                "Congrats, you found the brains behind the murder! "
                "Everyone in Python City hails you as the greatest Python detective of all time. "
                "Time to break out the champagne!"
            )
            st.balloons()
            st.image("Miranda_Pristley_3.png", caption="Miranda Priestly", width='stretch')
        elif name == HITMAN:
            st.warning(
                "Congrats, you found the murderer! But wait—it seems that our killer was just a hitman, "
                "he is not the real culprit. Try querying the interview transcript of the murderer to find "
                "the real villain behind this crime."
            )
            st.image("jeremy_bowers.png", caption="Jeremy Bowers", width='stretch')
        else:
            st.error("Nope! This is not the killer.")
            st.session_state.last_wrong_guess = st.session_state.guess_text
            start_cooldown()
            st.rerun()

# Optional: last wrong guess for feedback
if st.session_state.last_wrong_guess:
    st.caption(f"Last guess: *{st.session_state.last_wrong_guess}*")

# Optional: tiny UX touch
st.caption("Tip: Matching is case-insensitive and ignores extra spaces.")