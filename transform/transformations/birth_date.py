import pandas as pd
from datetime import datetime


def parse_date(value):
    if pd.isna(value):
        return pd.NaT

    # 1. Já é datetime
    if isinstance(value, (pd.Timestamp, datetime)):
        parsed = value.to_pydatetime()

        if parsed.replace(tzinfo=None) > datetime.now():
            return pd.NaT

        return parsed

    value = str(value).strip()

    if not value or value == "!":
        return pd.NaT

    # 2. Número serial do Excel
    if value.isdigit():
        try:
            parsed = pd.to_datetime(
                float(value),
                unit="d",
                origin="1899-12-30"
            ).to_pydatetime()

            if parsed > datetime.now():
                return pd.NaT

            return parsed
        except (ValueError, TypeError, OverflowError):
            return pd.NaT

    # 3. Formatos ISO e timestamp
    try:
        parsed = pd.to_datetime(
            value,
            format="ISO8601",
            errors="raise"
        ).to_pydatetime()

        if parsed.replace(tzinfo=None) > datetime.now():
            return pd.NaT

        return parsed
    except (ValueError, TypeError, OverflowError):
        pass

    # 4. Formato brasileiro: dd/mm/yy ou dd/mm/yyyy
    try:
        day, month, year = value.split("/")

        day = int(day)
        month = int(month)
        year = int(year)

        if year < 100:
            year += 1900 if year > 29 else 2000
        elif year < 1000:
            year += 1000

        if year < 1900 or year > 2100:
            return pd.NaT

        parsed = datetime(year, month, day)

        if parsed > datetime.now():
            return pd.NaT

        return parsed
    except (ValueError, TypeError):
        return pd.NaT


def transform_birth_date(df: pd.DataFrame) -> pd.DataFrame:
    col = "data de nascimento"

    if col not in df.columns:
        df[col] = pd.NA

    for alternative in [
        "data nascimento",
        "data_nasc",
        "adotantes.data_nascimento",
    ]:
        if alternative in df.columns:
            df[col] = df[col].combine_first(df[alternative])

    df = df.drop(
        columns=[
            "data nascimento",
            "data_nasc",
            "adotantes.data_nascimento",
        ],
        errors="ignore",
    )

    df[col] = df[col].replace("!", pd.NA)
    df[col] = df[col].apply(parse_date)

    return df