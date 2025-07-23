
# Annual Father's Day Golf Tournament Manager App

This Streamlit app provides an interactive platform for managing and displaying golf scores, calculating handicaps, and maintaining a leaderboard. The backend is fully powered by **Snowflake**, ensuring robust data storage and performance for real-time updates.

---

## 🧠 Features

- Input players and scores via a Streamlit form.
- Tee box selection is dynamically filtered based on player sex and course.
- Handicap index is calculated from the last 3 rounds.
- Course handicap is derived using USGA formula.
- Leaderboard reflects lowest net score for each player in the current year.
- Dynamic age calculation for players.
- Clean UI with a GitHub-hosted banner and Snowflake branding.

---

## 🏌️ Handicap and Score Calculations

### Handicap Index (for each player)
- Use the last **3 scores**.
- For each score: calculate **Score Differential**:
  
\[\text{Score Differential} = (\text{Total Score} - \text{Course Rating}) \times (113 / \text{Slope Rating})\]
- Take the **average of the lowest 2** differentials (or the available ones if less than 2).
- Round to 1 decimal place.

### Course Handicap
- \[\text{Course Handicap} = \text{Handicap Index} \times (\text{Slope Rating} / 113)\]
- Round to nearest whole number.

### Net Score
- \[\text{Net Score} = \text{Total Score} - \text{Course Handicap}\]

---

## 🏆 Leaderboard

- Shows each player's **lowest Net Score** for the **current year**.
- Columns displayed:
  - First Name
  - Last Name
  - Net Score

---

## ❄️ Snowflake Backend

All tables and views are managed in Snowflake:

### Primary Tables

- **PLAYERS**
- **COURSE**
- **COURSE_TEE**
- **SCORES**

### Key Views

- **PLAYERS_ENRICHED**: Adds Age and dynamic Handicap to Players.
- **LEADERBOARD_CURRENT_YEAR**: Shows leaderboard for the current year.

> Note: Tee information is linked via `TEE_ID`, which relates to both Player's sex and Course name.

---

## 🖼️ Visual Elements

- App includes a golf-themed banner between leaderboard and player sections.
- Footer acknowledges "Powered by Snowflake" with official icon.
- Annual family tournament picture.

---
## 🔐 Data Entry Access

To ensure data integrity in a publicly accessible app, only authorized users are allowed to add players and scores. This is accomplished by prompting for a **Data Entry Access Password** before any data entry operations can be performed.

### How it Works

- The password prompt is displayed when the user attempts to access the **"Add Player"** or **"Add Score"** tabs.
- Only users who enter the correct password can view and use the data entry forms.
- The password is securely stored in the app configuration.

### Sample Implementation

```python
# Simple password protection
DATA_ENTRY_PASSWORD = st.secrets["data_entry_password"]  # Set this in .streamlit/secrets.toml

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    password = st.text_input("Enter Data Entry Access Password", type="password")
    if password == DATA_ENTRY_PASSWORD:
        st.session_state.authenticated = True
        st.success("Access granted.")
    elif password:
        st.error("Incorrect password.")
else:
    # Show data entry form here
    ...
```

### Add to Secrets

added to the scerets toml in Streamlit.

---

## 🔧 Setup

1. Clone this repo
2. Configure Snowflake credentials and tables
3. Run `streamlit run app.py`

---

## 📁 File Structure

- `app.py` — Streamlit UI logic
- `images/` — Visual assets
- `README.md` — This documentation

---

## 📣 Acknowledgements

This app is proudly powered by [Snowflake](https://www.snowflake.com/).

![Snowflake](https://raw.githubusercontent.com/nrschaaf/fathers_day_golf/main/images/Snowflake_Logo.png)

