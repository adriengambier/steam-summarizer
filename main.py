import pandas as pd
import streamlit as st
import sqlite3

st.title('Steam Reviews')

path_db = "./data/steam_db.sqlite"
connection = sqlite3.connect(path_db)

query = """
  SELECT A.id,
    TRIM(A.name) AS name
  FROM games A
  LEFT JOIN summaries B
    ON A.id = B.id
  WHERE A.name != ''
    AND B.total_reviews >= 100
  ORDER BY TRIM(A.name)
"""
df_games = pd.read_sql(query, connection)

option = st.selectbox("Select game", df_games["name"])
st.markdown(f"**You selected:** {option}")

id_selected = df_games[df_games["name"] == option]["id"].squeeze()
st.markdown(f"**You selected:** {id_selected}")
