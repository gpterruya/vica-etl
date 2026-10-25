import pandas as pd
from datetime import datetime


def calculate_age(birth_date):
    if pd.isna(birth_date):
        return pd.NA

    if not isinstance(birth_date, (pd.Timestamp, datetime)):
        return pd.NA

    today = datetime.now()

    age = today.year - birth_date.year

    # 🔥 ajuste se ainda não fez aniversário
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1

    # 🚨 sanity check (dados ruins)
    if age < 0 or age > 120:
        return pd.NA

    return age


def transform_age(df: pd.DataFrame, column_birth="data de nascimento", column_age="idade_adotante") -> pd.DataFrame:
    df[column_age] = df[column_birth].apply(calculate_age)
    return df