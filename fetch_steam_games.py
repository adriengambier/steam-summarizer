import steam_api
import sqlite3
import pandas as pd


def main():
  steam_api_client = steam_api.SteamAPI()

  path_db = "./data/steam_db.sqlite"
  connection = sqlite3.connect(path_db)

  create_table_query = """
    CREATE TABLE IF NOT EXISTS games (
        id TEXT PRIMARY KEY ON CONFLICT IGNORE,
        name TEXT
    ) WITHOUT ROWID
  """
  connection.execute(create_table_query)

  games = steam_api_client.get_all_games()
  df_games = pd.DataFrame(games)
  df_games = df_games.rename(columns={"appid": "id"})

  df_games.to_sql("games", connection, if_exists="append", index=False)

  connection.close()


if __name__ == "__main__":
  main()
