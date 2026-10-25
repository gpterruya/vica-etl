import pandas as pd
import unicodedata
import re

COMMON_TYPOS = {
    "pequeno porte": "pequeno",
    "porte pequeno": "pequeno",
    "pequenino": "pequeno",
    "mini": "pequeno",
    "toy": "pequeno",
    "p": "pequeno",
    "pp": "pequeno",

    "medio porte": "medio",
    "porte medio": "medio",
    "médio porte": "medio",
    "porte médio": "medio",
    "m": "medio",

    "grande porte": "grande",
    "porte grande": "grande",
    "g": "grande",

    "gigante porte": "gigante",
    "porte gigante": "gigante",
    "gg": "gigante",

    "estimado: medio/garande": "medio/grande",
    "estimado: medio/grande": "medio/grande",
    "medio/grande": "medio/grande",
    "medio grande": "medio/grande",

    "pequeno/medio": "pequeno/medio",
    "medio/pequeno": "pequeno/medio",
    "gde": "grande",
    "media": "medio",
    "medido": "medio",
    "medii": "medio",
    "medo": "medio",
    "medoo": "medio",
    "mudo": "medio",
    "m edio": "medio",
    "m~edio": "medio",
    "peq": "pequeno",
    "peqeno": "pequeno",
    "peqeno": "pequeno",
    "peqeuno": "pequeno",
    "pequemo": "pequeno",
    "pequen": "pequeno",
    "pequena": "pequeno",
    "peaueno": "pequeno",
}

def normalize_text(text):
    return (
        unicodedata.normalize("NFKD", str(text))
        .encode("ascii", "ignore")
        .decode("utf-8")
    )

def transform_size(df: pd.DataFrame, column="porte") -> pd.DataFrame:

    # Unifica as colunas de porte, mesmo quando alguma estiver ausente
    df[column] = df.get(
        column,
        pd.Series(pd.NA, index=df.index, dtype="object")
    )

    if "pets.porte" in df.columns:
        df[column] = df[column].combine_first(df["pets.porte"])

    df = df.drop(
        columns=["pets.porte"],
        errors="ignore"
    )

    col = (
        df[column]
        .astype(str)
        .str.strip()
        .str.lower()
        .apply(normalize_text)
    )

    # limpa espaços extras
    col = col.str.replace(r"[-_]+", " ", regex=True)
    col = col.str.replace(r"\s+", " ", regex=True).str.strip()
    # normaliza conectores compostos
    col = col.str.replace(r"\s+e\s+", "/", regex=True)

    # corrige typos
    col = col.replace(COMMON_TYPOS)
    # corrige termos dentro de textos compostos
    for wrong, correct in COMMON_TYPOS.items():
        col = col.str.replace(wrong, correct, regex=False)

    mapping = {
        "pequeno": "Pequeno",
        "medio": "Médio",
        "grande": "Grande",
        "gigante": "Gigante",

        # compostos
        "medio/grande": "Grande",
        "pequeno/medio": "Médio",

        "": "",
        "nan": "",
        "none": "",
    }

    result = col.map(mapping)

    # heurística
    def infer_size(text):
        if not text:
            return ""

        # =========================
        # COMPOSTOS PRIMEIRO
        # =========================
        if "/" in text:

            if "grande" in text:
                return "Grande"

            if "medio" in text:
                return "Médio"

            if "pequeno" in text:
                return "Pequeno"

        # =========================
        # SIMPLES
        # =========================
        if any(x in text for x in ["pequeno", "mini", "micro", "toy"]):
            return "Pequeno"

        if "medio" in text:
            return "Médio"

        if "grande" in text:
            return "Grande"

        if "gigante" in text:
            return "Gigante"

        # =========================
        # PESO
        # =========================
        if "kg" in text:
            import re

            nums = re.findall(r"\d+", text)

            if nums:
                kg = int(nums[0])

                if kg <= 10:
                    return "Pequeno"
                elif kg <= 25:
                    return "Médio"
                elif kg <= 45:
                    return "Grande"
                else:
                    return "Gigante"

        return ""

    result = result.fillna(col.apply(infer_size))

    df[column] = result.fillna("")

    return df
