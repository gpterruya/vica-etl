import pandas as pd
import unicodedata
import re


def normalize_text(value):
    if pd.isna(value):
        return None

    value = str(value).strip().upper()

    # remove acento
    value = unicodedata.normalize('NFKD', value)
    value = ''.join(c for c in value if not unicodedata.combining(c))

    # remove caracteres estranhos
    value = re.sub(r"[^A-Z\s]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()

    return value


def normalize_city(value):
    value = normalize_text(value)

    if not value:
        return pd.NA

    # 🚨 REGRA 1: se for número puro → lixo
    if value.isdigit():
        return pd.NA

    # 🚨 REGRA 2: muito curto → lixo (tipo "A", "B")
    if len(value) <= 2:
        return pd.NA

    return value

def transform_city(df: pd.DataFrame, column="cidade") -> pd.DataFrame:
    df[column] = df.get(
        column,
        pd.Series(pd.NA, index=df.index, dtype="object")
    )

    alternative = "adotantes.cidade"
    if alternative in df.columns:
        df[column] = df[column].combine_first(df[alternative])

    df = df.drop(
        columns=["adotantes.cidade"],
        errors="ignore"
    )

    df[column] = df[column].apply(normalize_city)
    return df