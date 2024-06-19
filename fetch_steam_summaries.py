import steam_api
import pandas as pd
import sqlite3


def main():
  steam_api_client = steam_api.SteamAPI()

  path_db = "./data/steam_db.sqlite"
  connection = sqlite3.connect(path_db)

  create_table_query = """
    CREATE TABLE IF NOT EXISTS summaries (
        id TEXT PRIMARY KEY ON CONFLICT REPLACE,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        total_reviews INT,
        total_positive INT,
        total_negative INT
    ) WITHOUT ROWID
  """
  connection.execute(create_table_query)

  remaining_ids_query = """
    SELECT A.id
    FROM games A
    LEFT JOIN summaries B
      ON A.id = B.id
    WHERE total_reviews IS NULL
  """
  remaining_ids = pd.read_sql(remaining_ids_query, connection)["id"].to_list()

  summaries = steam_api_client.get_reviews_summaries(remaining_ids[0:5])

  df_summary = pd.DataFrame(summaries)
  df_summary.to_sql("summaries", connection, if_exists="append", index=False)


if __name__ == "__main__":
  main()
