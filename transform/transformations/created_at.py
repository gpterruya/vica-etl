import pandas as pd

def transform_created_at(df: pd.DataFrame, column="created_at") -> pd.DataFrame:
    dt = pd.to_datetime(df[column], errors="coerce", utc=True)
    dt = dt.dt.tz_convert(None)

    # sobrescreve a própria coluna já no formato que o Looker aceita
    df[column] = dt.dt.strftime("%Y-%m-%d")

    return df