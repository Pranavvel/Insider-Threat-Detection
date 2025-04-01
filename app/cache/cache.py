import pandas as pd
from io import StringIO
import redis
import logging

def cache_df(alias: str, df: pd.DataFrame) -> None:
    r = redis.Redis()
    res = r.set(alias, df.to_json())
    if res == True:
        logging.warning(f'Cached Dataframe {alias}')

def get_cached_df(alias: str) -> pd.DataFrame:
    r = redis.Redis()
    result = r.get(alias)
    if result is None:
        logging.error(f"No cached data found for alias {alias}")
        return pd.DataFrame()
    try:
        # Wrap the JSON string in StringIO before passing to pd.read_json
        return pd.read_json(StringIO(result.decode()))
    except ValueError as e:
        logging.error(f"Error decoding JSON for alias {alias}: {e}")
        return pd.DataFrame()


