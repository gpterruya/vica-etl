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


def normalize_neighborhood(value):
    value = normalize_text(value)

    if not value:
        return pd.NA

    # 🚨 caso CEP (8 dígitos)
    if value.isdigit() and len(value) == 8:
        return pd.NA

    # 🚨 número puro (qualquer tamanho)
    if value.isdigit():
        return pd.NA

    # 🚨 muito curto (tipo "A")
    if len(value) <= 2:
        return pd.NA

    return value

def transform_neighbourhood(df: pd.DataFrame, column="bairro") -> pd.DataFrame:
    df[column] = df.get(
        column,
        pd.Series(pd.NA, index=df.index, dtype="object")
    )

    alternative = "adotantes.bairro"
    if alternative in df.columns:
        df[column] = df[column].combine_first(df[alternative])

    df = df.drop(
        columns=["adotantes.bairro"],
        errors="ignore"
    )

    df[column] = df[column].apply(normalize_neighborhood)
    return df