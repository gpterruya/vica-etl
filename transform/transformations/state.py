import pandas as pd
import unicodedata
import re

VALID_UFS = {
    "AC","AL","AP","AM","BA","CE","DF","ES","GO",
    "MA","MT","MS","MG","PA","PB","PR","PE","PI",
    "RJ","RN","RS","RO","RR","SC","SP","SE","TO"
}

STATE_NAME_TO_UF = {
    "ACRE": "AC",
    "ALAGOAS": "AL",
    "AMAPA": "AP",
    "AMAZONAS": "AM",
    "BAHIA": "BA",
    "CEARA": "CE",
    "DISTRITO FEDERAL": "DF",
    "ESPIRITO SANTO": "ES",
    "GOIAS": "GO",
    "MARANHAO": "MA",
    "MATO GROSSO": "MT",
    "MATO GROSSO DO SUL": "MS",
    "MINAS GERAIS": "MG",
    "PARA": "PA",
    "PARAIBA": "PB",
    "PARANA": "PR",
    "PERNAMBUCO": "PE",
    "PIAUI": "PI",
    "RIO DE JANEIRO": "RJ",
    "RIO GRANDE DO NORTE": "RN",
    "RIO GRANDE DO SUL": "RS",
    "RONDONIA": "RO",
    "RORAIMA": "RR",
    "SANTA CATARINA": "SC",
    "SAO PAULO": "SP",
    "SERGIPE": "SE",
    "TOCANTINS": "TO"
}

CITY_TO_UF = {
    "MANAUS": "AM",
    "SANTOS": "SP"
}



def normalize_text(value):
    if pd.isna(value):
        return None

    value = str(value).strip().upper()

    # remove acentos (PARANÁ -> PARANA)
    value = unicodedata.normalize('NFKD', value)
    value = ''.join([c for c in value if not unicodedata.combining(c)])

    # remove lixo tipo "PR - BRASIL"
    value = re.sub(r"[^A-Z\s]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()

    return value

def similarity_match(value, target):
    value_tokens = set(value.split())
    target_tokens = set(target.split())

    if not value_tokens or not target_tokens:
        return 0

    return len(value_tokens & target_tokens) / len(target_tokens)


def normalize_state(value):
    value = normalize_text(value)

    if not value:
        return pd.NA

    # 🚨 caso S.P / R.J / M.G etc
    # depois do replace(".","")
    value = value.replace(" ", "").replace(".", "")

    # 🚨 casos tipo SA, SP, RJ, MG etc
    if len(value) == 2:
        if value in VALID_UFS:
            return value

        # caso específico conhecido
        if value == "SA":
            return "SP"
        
        return pd.NA

    # 🚨 regra de qualidade: valores muito curtos são lixo
    if len(value) <= 1:
        return pd.NA

    # UF direta
    if value in VALID_UFS:
        return value

    # estado por nome
    if value in STATE_NAME_TO_UF:
        return STATE_NAME_TO_UF[value]

    # cidade
    if value in CITY_TO_UF:
        return CITY_TO_UF[value]

    # fallback contains
    for state_name, uf in STATE_NAME_TO_UF.items():
        if state_name in value:
            return uf

    if "PAULO" in value:
        return "SP"
    
    # fuzzy match leve para estados
    best_match = None
    best_score = 0

    for state_name, uf in STATE_NAME_TO_UF.items():
        score = similarity_match(value, state_name)

        if score > best_score:
            best_score = score
            best_match = uf

    # threshold (ajusta conforme qualidade dos dados)
    if best_score >= 0.6:
        return best_match

    return pd.NA


def transform_state(df: pd.DataFrame) -> pd.DataFrame:
    df["estado"] = df.get(
        "estado",
        pd.Series(pd.NA, index=df.index, dtype="object")
    )

    alternative = "adotantes.uf"
    if alternative in df.columns:
        df["estado"] = df["estado"].combine_first(df[alternative])

    df = df.drop(
        columns=["adotantes.uf"],
        errors="ignore"
    )

    df["estado"] = df["estado"].apply(normalize_state)

    return df