import streamlit as st
import pandas as pd
import mysql.connector

# Connect to the MySQL database
def get_connection():
    return mysql.connector.connect(
        host="localhost",  
        user="root",       
        password="",       
        database="tennis"  
    )

# Query helper function
def execute_query(query, params=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params or ())
    result = cursor.fetchall()
    conn.close()
    return pd.DataFrame(result)

# Streamlit app
st.balloons()
st.image("C:/Users/rahul/Downloads/tennis-7932067_1280.webp")
st.title("Tennis Competitor Dashboard")

menu = ["Homepage Dashboard", "Search and Filter Competitors", "Competitor Details Viewer", "Country-Wise Analysis", "Leaderboards"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Homepage Dashboard":
    st.header("Summary Statistics")

    # Total number of competitors
    total_competitors_query = "SELECT COUNT(*) AS total FROM competitors"
    total_competitors = execute_query(total_competitors_query)["total"].iloc[0]

    # Number of countries represented
    countries_query = "SELECT COUNT(DISTINCT country) AS countries FROM competitors"
    total_countries = execute_query(countries_query)["countries"].iloc[0]

    # Highest points scored by a competitor
    highest_points_query = "SELECT MAX(points) AS max_points FROM competitor_rankings"
    highest_points = execute_query(highest_points_query)["max_points"].iloc[0]

    st.subheader(f"**Total Competitors:** {total_competitors}")
    st.subheader(f"**Countries Represented:** {total_countries}")
    st.subheader(f"**Highest Points Scored:** {highest_points}")

elif choice == "Search and Filter Competitors":
    st.header("Search and Filter Competitors")

    # Search by name
    search_name = st.sidebar.text_input("Search by Name")

    # Filter by rank range, country, or points threshold
    rank_range = st.sidebar.slider("Rank Range", 1, 1000, (1, 100))
    selected_country = st.sidebar.text_input("Filter by Country")
    points_threshold = st.sidebar.number_input("Minimum Points", min_value=0, step=50, value=0)

    query = """
        SELECT c.name, c.country, cr.rank, cr.points
        FROM competitors c
        JOIN competitor_rankings cr ON c.competitor_id = cr.competitor_id
        WHERE (c.name LIKE %s OR %s = '')
        AND cr.rank BETWEEN %s AND %s
        AND (c.country = %s OR %s = '')
        AND cr.points >= %s
    """

    params = (f"%{search_name}%", search_name, rank_range[0], rank_range[1], selected_country, selected_country, points_threshold)
    competitors = execute_query(query, params)

    st.dataframe(competitors)

elif choice == "Competitor Details Viewer":
    st.header("Competitor Details Viewer")
    


    competitor_name = st.sidebar.text_input("Enter Competitor Name")

    if competitor_name:
        details_query = """
            SELECT c.name, c.country, cr.rank, cr.movement, cr.competitions_played, cr.points
            FROM competitors c
            JOIN competitor_rankings cr ON c.competitor_id = cr.competitor_id
            WHERE c.name = %s
        """
        competitor_details = execute_query(details_query, (competitor_name,))

        if not competitor_details.empty:
            st.write(competitor_details.T)
        else:
            st.write("Competitor not found.")

elif choice == "Country-Wise Analysis":
    st.header("Country-Wise Analysis")

    country_analysis_query = """
        SELECT c.country, COUNT(*) AS total_competitors, AVG(cr.points) AS average_points
        FROM competitors c
        JOIN competitor_rankings cr ON c.competitor_id = cr.competitor_id
        GROUP BY c.country order by total_competitors desc
    """
    country_data = execute_query(country_analysis_query)
    st.dataframe(country_data)

elif choice == "Leaderboards":
    st.header("Leaderboards")

    # Top-ranked competitors
    top_ranked_query = """
        SELECT c.name, c.country, cr.rank, cr.points
        FROM competitors c
        JOIN competitor_rankings cr ON c.competitor_id = cr.competitor_id
        ORDER BY cr.rank ASC
        LIMIT 10
    """
    top_ranked = execute_query(top_ranked_query)

    st.subheader("Top-Ranked Competitors")
    st.dataframe(top_ranked)

    # Competitors with the highest points
    highest_points_query = """
        SELECT c.name, c.country, cr.rank, cr.points
        FROM competitors c
        JOIN competitor_rankings cr ON c.competitor_id = cr.competitor_id
        ORDER BY cr.points DESC
        LIMIT 10
    """
    highest_points = execute_query(highest_points_query)

    st.subheader("Competitors with Highest Points")
    st.dataframe(highest_points)
