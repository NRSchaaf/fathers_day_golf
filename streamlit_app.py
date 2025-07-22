import streamlit as st
import snowflake.connector
import pandas as pd
from datetime import date

# ------------------ Setup ------------------ #
st.set_page_config(page_title="Fathers Day Golf Manager", layout="wide")

# ------------------ Connect to Snowflake ------------------ #
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

# ------------------ Password Gate ------------------ #
expected_password = st.secrets["app"]["entry_password"]
st.sidebar.header("🔐 Data Entry Access")
entered_password = st.sidebar.text_input("Enter password", type="password")
unlocked = entered_password == expected_password
if unlocked:
    st.sidebar.success("✅ Access granted")
else:
    st.sidebar.info("Viewing only. Enter password to enable data entry.")

# ------------------ Display Players ------------------ #
st.title("⛳ Annual Father's Day Golf Tournament")
st.subheader("👥 Players")

cursor.execute("SELECT * FROM PLAYERS_ENRICHED ORDER BY Last_Name")
rows = cursor.fetchall()
colnames = [desc[0] for desc in cursor.description]

players_df = pd.DataFrame(rows, columns=colnames)

st.dataframe(players_df, use_container_width=True)

# ------------------ Display Scores ------------------ #
st.subheader("📊 Scores")

cursor.execute("""
    SELECT 
        s.Score_ID,
        p.First_Name || ' ' || p.Last_Name AS Player,
        s.Round_Date,
        s.Location,
        s.Total_Score
    FROM Scores s
    JOIN Players p ON s.Player_ID = p.Player_ID
    ORDER BY s.Round_Date DESC
""")
scores_df = cursor.fetchall()
score_cols = [desc[0] for desc in cursor.description]
st.dataframe(data=scores_df, use_container_width=True, column_config=dict(zip(score_cols, score_cols)))

# ------------------ Tabs for Data Entry ------------------ #
if unlocked:
    tab1, tab2 = st.tabs(["➕ Add Player", "📝 Add Score"])

    with tab1:
        st.subheader("➕ Add New Player")

        first = st.text_input("First Name")
        last = st.text_input("Last Name")
        birthdate = st.date_input(
            "Birthdate",
            min_value=date(1900, 1, 1),
            max_value=date.today()
        )
        handycap = st.number_input("Handicap", min_value=0.0, max_value=54.0, step=0.1)

        if st.button("Add Player"):
            cursor.execute("""
                INSERT INTO Players (First_Name, Last_Name, Birthdate, Handycap)
                VALUES (%s, %s, %s, %s)
            """, (first, last, birthdate, handycap))
            conn.commit()
            st.success(f"✅ Player {first} {last} added.")

    with tab2:
        st.subheader("📝 Add Score")

        # Load players for dropdown
        cursor.execute("SELECT Player_ID, First_Name || ' ' || Last_Name AS Full_Name FROM Players ORDER BY Last_Name")
        player_list = cursor.fetchall()
        player_dict = {name: pid for pid, name in player_list}

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
            st.success(f"✅ Score for {selected_player} on {round_date} added.")

else:
    st.info("🔒 To add a player or score, enter the correct password in the sidebar.")
