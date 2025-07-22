import streamlit as st
import snowflake.connector
from datetime import date

# Connect to Snowflake
@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        account=st.secrets["snowflake"]["account"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"]
    )

conn = get_connection()
cursor = conn.cursor()

st.title("Fathers Day Golf Tournament Manager")

# Tabs for UI
tab1, tab2 = st.tabs(["Add Player", "Add Score"])

# ------------------- Add Player -------------------
with tab1:
    st.subheader("Add New Player")

    first = st.text_input("First Name")
    last = st.text_input("Last Name")
    birthdate = st.date_input("Birthdate")
    handycap = st.number_input("Handicap", min_value=0.0, max_value=54.0, step=0.1)

    if st.button("Add Player"):
        cursor.execute("""
            INSERT INTO Players (First_Name, Last_Name, Birthdate, Handycap)
            VALUES (%s, %s, %s, %s)
        """, (first, last, birthdate, handycap))
        conn.commit()
        st.success(f"Player {first} {last} added!")

# ------------------- Add Score -------------------
with tab2:
    st.subheader("Add Score")

    # Load players to a dropdown
    cursor.execute("SELECT Player_ID, First_Name || ' ' || Last_Name FROM Players ORDER BY Last_Name")
    players = cursor.fetchall()
    player_dict = {name: pid for pid, name in players}

    selected_player = st.selectbox("Select Player", list(player_dict.keys()))
    round_date = st.date_input("Round Date", value=date.today())
    location = st.text_input("Location")
    score = st.number_input("Total Score", min_value=18, max_value=200, step=1)

    if st.button("Add Score"):
        player_id = player_dict[selected_player]
        cursor.execute("""
            INSERT INTO Scores (Player_ID, Round_Date, Location, Total_Score)
            VALUES (%s, %s, %s, %s)
        """, (player_id, round_date, location, score))
        conn.commit()
        st.success(f"Score for {selected_player} on {round_date} added!")

