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
    
# ------------------ Page/App Title ------------------ #
st.title("⛳ Annual Father's Day Golf Tournament ⛳")

# ------------------ Display Leaderboard ------------------ #
st.subheader("🏆 Leaderboard")

cursor.execute("SELECT * FROM LEADERBOARD")
leaderboard_data = cursor.fetchall()
leaderboard_columns = [desc[0] for desc in cursor.description]

leaderboard_df = pd.DataFrame(leaderboard_data, columns=leaderboard_columns)

# Display only desired columns (no ROUND_DATE)
columns_to_display = ["FIRST_NAME", "LAST_NAME", "LOWEST_NET_SCORE"]
filtered_leaderboard_df = leaderboard_df[columns_to_display]

# Optional: Sort by score
filtered_leaderboard_df = filtered_leaderboard_df.sort_values(by="LOWEST_NET_SCORE")

st.dataframe(filtered_leaderboard_df, use_container_width=True)

# ------------------ Commemorative Photo ------------------ #
st.image("https://raw.githubusercontent.com/nrschaaf/fathers_day_golf/main/images/2025-06-14_Fathers_Day.jpg", use_container_width=True)

# ------------------ Display Players ------------------ #
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
            cursor.execute("SELECT PLAYER_ID, First_Name || ' ' || Last_Name AS Full_Name FROM PLAYERS ORDER BY Last_Name")
            player_list = cursor.fetchall()
            player_dict = {name: pid for pid, name in player_list}
        
            selected_player = st.selectbox("Select Player", list(player_dict.keys()))
            player_id = player_dict[selected_player]
        
            # Get player sex
            cursor.execute("SELECT Sex FROM PLAYERS WHERE PLAYER_ID = %s", (player_id,))
            player_sex = cursor.fetchone()[0]
        
            # Load course names
            cursor.execute("SELECT DISTINCT course_name FROM COURSE ORDER BY course_name")
            courses = [row[0] for row in cursor.fetchall()]
            selected_course = st.selectbox("Select Course", courses)
        
            # Get Course_ID for selected course
            cursor.execute("SELECT Course_ID FROM COURSE WHERE course_name = %s", (selected_course,))
            course_id = cursor.fetchone()[0]
        
            # Get available tee boxes for course and sex
            cursor.execute("""
                SELECT Tee_ID, Tee_Box
                FROM COURSE_TEE
                WHERE Course_ID = %s AND Tee_Box_Sex = %s
                ORDER BY Tee_Box
            """, (course_id, player_sex))
            tee_rows = cursor.fetchall()
            if not tee_rows:
                st.warning("No tee boxes available for this course and player sex.")
                selected_tee_id = None
            else:
                tee_dict = {row[1]: row[0] for row in tee_rows}
                selected_tee_box = st.selectbox("Select Tee Box", list(tee_dict.keys()))
                selected_tee_id = tee_dict[selected_tee_box]
        
            round_date = st.date_input("Round Date", value=date.today())
            score = st.number_input("Total Score", min_value=18, max_value=200, step=1)
        
            if st.button("Add Score"):
                if selected_tee_id is None:
                    st.error("Please select a valid Tee Box before submitting.")
                else:
                    cursor.execute("""
                        INSERT INTO SCORES (PLAYER_ID, ROUND_DATE, TOTAL_SCORE, TEE_ID)
                        VALUES (%s, %s, %s, %s)
                    """, (player_id, round_date, score, selected_tee_id))
                    conn.commit()
                    st.success(f"✅ Score for {selected_player} at {selected_course} on {round_date} added.")

else:
    st.info("🔒 To add a player or score, enter the correct password in the sidebar.")

# ------------------ Tabs for Data Entry ------------------ #
col1, col2 = st.columns([0.5, 5])

with col1:
    st.markdown("<small>Powered by </small>", unsafe_allow_html=True)

with col2:
    st.image("https://raw.githubusercontent.com/nrschaaf/fathers_day_golf/main/images/Snowflake_Logo.png", width=80)  # Adjust size as needed
