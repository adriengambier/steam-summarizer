import pandas as pd
import streamlit as st
import sqlite3
from thefuzz import fuzz
import streamlit_antd_components as sac

st.set_page_config("steam-summarizer", page_icon="Steam_icon_logo.svg")

st.image("Steam_icon_logo.svg", width=80)
st.title('Steam Reviews')

GAME_PER_PAGE = 5
MAX_RESULTS = 25


@st.cache_resource
def init_connection():
  path_db = "./data/steam_db.sqlite"
  connection = sqlite3.connect(path_db)

  return connection


@st.cache_data
def get_games() -> pd.DataFrame:

  query = """
    SELECT A.id,
      TRIM(A.name) AS name
    FROM games A
    WHERE A.name != ''
    ORDER BY TRIM(A.name)
  """
  df_games = pd.read_sql(query, connection)

  return df_games


connection = init_connection()

st.session_state["games"] = get_games()


def reset_game_suggestions():
  # Reset list of propositions
  if "game_selected" in st.session_state:
    del st.session_state["game_selected"]
  st.session_state.page_idx = 1


def list_names():
  reset_game_suggestions()
  user_input = st.session_state["user_input"].lower()
  df_games = st.session_state["games"]

  df_games = df_games.loc[
      df_games['name'].str.contains(user_input, case=False), ["name", "id"]]
  df_games["ratio"] = df_games["name"].apply(
      lambda x: fuzz.ratio(user_input, x.lower()))

  st.session_state.results = df_games.sort_values(
      by="ratio", ascending=False)[["name", "id"]].iloc[0:MAX_RESULTS]


st.text_input("Search for a game",
              placeholder="Hades, Half-Life, ...",
              on_change=list_names,
              key="user_input")

# User enters a name & no game selected
if (len(st.session_state["user_input"])
    > 0) & (st.session_state.get("game_selected") is None):
  page_idx = st.session_state.page_idx

  game_selected = sac.chip(items=[
      sac.ChipItem(label=name, icon="controller")
      for name in st.session_state.results["name"].iloc[GAME_PER_PAGE *
                                                        (page_idx -
                                                         1):GAME_PER_PAGE *
                                                        page_idx]
  ],
                           direction='vertical',
                           size='md',
                           key="game_selected")
  page_idx = sac.pagination(align='center',
                            key="page_idx",
                            page_size=GAME_PER_PAGE,
                            total=min(MAX_RESULTS,
                                      len(st.session_state.results["name"])))

if st.session_state.get("game_selected") is not None:
  st.button(":arrow_left: Back", on_click=reset_game_suggestions)
  st.markdown(f"Selected game : {st.session_state.game_selected}")
