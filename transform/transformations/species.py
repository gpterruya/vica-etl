import pandas as pd
import unicodedata

def normalize_text(text):
    if pd.isna(text):
        return ""

    text = str(text)
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")

def transform_species(df: pd.DataFrame, column="espécie") -> pd.DataFrame:
    df[column] = df.get(
        column,
        pd.Series(pd.NA, index=df.index, dtype="object")
    )

    for alternative in ["especie", "pets.especie"]:
        if alternative in df.columns:
            df[column] = df[column].combine_first(df[alternative])

    df = df.drop(
        columns=["especie", "pets.especie"],
        errors="ignore"
    )

    col = (
        df[column]
        .astype(str)
        .str.strip()
        .str.lower()
        .apply(normalize_text)
    )

    mapping = {
        "cachorro": "Cachorro",
        "cao": "Cachorro",
        "cão": "Cachorro",
        "dog": "Cachorro",
        "gato": "Gato",
        "cat": "Gato",
        "felino": "Gato",
        "canino": "Cachorro",
        "felina": "Gato",
        "canina": "Cachorro",
    }

    result = col.map(mapping)

    result = result.fillna(
        col.apply(lambda x: "Cachorro" if "collie" in x else None)
    )
    result = result.fillna(
        col.apply(lambda x: "Cachorro" if "canin" in x else None)
    )
    result = result.fillna(
        col.apply(lambda x: "Cachorro" if "husky" in x else None)
    )

    df[column] = result.fillna("")
    return df