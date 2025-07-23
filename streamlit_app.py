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
    SELECT * FROM Current_And_Previous_Season_Scores
""")
scores_data = cursor.fetchall()
score_columns = [desc[0] for desc in cursor.description]

# Convert to DataFrame
scores_df = pd.DataFrame(scores_data, columns=score_columns)

# Display DataFrame with column headers
st.dataframe(scores_df, use_container_width=True)

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
        handicap = st.number_input("Handicap", min_value=0.0, max_value=54.0, step=0.1)
    
        sex = st.selectbox("Sex", ["Male", "Female"])
    
        if st.button("Add Player"):
            cursor.execute("""
                INSERT INTO Players (First_Name, Last_Name, Birthdate, Handicap, Sex)
                VALUES (%s, %s, %s, %s, %s)
            """, (first, last, birthdate, handicap, sex))
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
    
            # Hardcoded location
            location = "City Club Marietta"
    
            # Get selected player's sex
            player_id = player_dict[selected_player]
            cursor.execute("SELECT Sex FROM Players WHERE Player_ID = %s", (player_id,))
            player_sex = cursor.fetchone()[0]
    
            # Fetch available tee boxes for this location and sex
            cursor.execute("""
                SELECT Tee_Box
                FROM Course_Tee
                WHERE Location = %s AND Sex = %s
            """, (location, player_sex))
            tee_boxes = [row[0] for row in cursor.fetchall()]
    
            if tee_boxes:
                selected_tee_box = st.selectbox("Select Tee Box", tee_boxes)
            else:
                selected_tee_box = None
                st.warning("⚠️ No tee boxes found for this player’s sex and location.")
    
            score = st.number_input("Total Score", min_value=18, max_value=200, step=1)
    
            if st.button("Add Score"):
                if selected_tee_box:
                    cursor.execute("""
                        INSERT INTO Scores (Player_ID, Round_Date, Location, Tee_Box, Total_Score)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (player_id, round_date, location, selected_tee_box, score))
                    conn.commit()
                    st.success(f"✅ Score for {selected_player} at {location} on {round_date} added.")
                else:
                    st.error("❌ Cannot add score without selecting a valid tee box.")

else:
    st.info("🔒 To add a player or score, enter the correct password in the sidebar.")
