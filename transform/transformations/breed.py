import pandas as pd
import unicodedata
from rapidfuzz import process

COMMON_TYPOS = {
    "begal": "beagle",
    "bewer": "biewer",
    "biwer": "biewer",
    "blue he": "blue heeler",
    "bluehe": "blue heeler",
    "blue heller": "blue heeler",
    "blue heller dog": "blue heeler",
    "boder": "border collie",
    "booldog": "bulldog",
    "booldog frances": "bulldog frances",
    "booldog francês": "bulldog frances",
    "buldog frances": "bulldog frances",
    "buldog francês": "bulldog frances",
    "bulldog frances flufli": "bulldog frances",
    "bulldog francês flufli": "bulldog frances",
    "booldog frances flufli": "bulldog frances",
    "booldog francês flufli": "bulldog frances",
    "bulldog frances fluffy": "bulldog frances",
    "bulldog francês fluffy": "bulldog frances",
    "buldogue frances": "bulldog frances",
    "buldogue francês": "bulldog frances",
    "buldogue feances": "bulldog frances",
    "buldogue feances": "bulldog frances",
    "bulldog feances": "bulldog frances",
    "buldog feances": "bulldog frances",
    "bull dog": "bulldog",
    "bull dog frances": "bulldog frances",
    "bull dog francês": "bulldog frances",
    "bull terrier": "Bull Terrier",
    "bulldog fances": "bulldog frances",
    "buldog fances": "bulldog frances",
    "bull dog fances": "bulldog frances",
    "bulldog france": "bulldog frances",
    "buldog france": "bulldog frances",
    "bull dog france": "bulldog frances",
    "bullfog": "bulldog",
    "bullfog frances": "bulldog frances",
    "bullfog francês": "bulldog frances",
    "bullldog": "bulldog",
    "bullldog frances": "bulldog frances",
    "bullldog francês": "bulldog frances",
    "cabe corso": "cane corso",
    "cani corso": "cane corso",
    "canec corso": "cane corso",
    "cao crista chines": "chinese crested",
    "cao cristao chines": "chinese crested",
    "cao cristã chines": "chinese crested",
    "cavalier": "cavalier king charles spaniel",
    "king charles": "cavalier king charles spaniel",
    "cavalier king": "cavalier king charles spaniel",
    "chiuaua": "chihuahua",
    "chiuhuahua": "chihuahua",
    "chiwawa": "chihuahua",
    "chiuaha": "chihuahua",
    "chocher": "pinscher",
    "coker": "cocker",
    "coton de tulear": "coton de tulear",
    "coton tulear": "coton de tulear",
    "coton": "coton de tulear",
    "crd": "srd",
    "Dachshound": "dachshund",
    "dachshound": "dachshund",
    "dalmata": "dalmata",
    "dash": "dachshund",
    "dash..": "dachshund",
    "dashshund": "dachshund",
    "dashund": "dachshund",
    "dach": "dachshund",
    "dogue alemao": "dogue alemao",
    "dog alemão": "dogue alemao",
    "dog alemao": "dogue alemao",
    "great dane": "dogue alemao",
    "dunsh": "dachshund",
    "dunshund": "dachshund",
    "exotic bully micro": "american bully",
    "exotic bully": "american bully",
    "micro bully": "american bully",
    "bully micro": "american bully",
    "fox paulistana": "fox paulistinha",
    "golden britanico": "golden retriever",
    "hotvaler": "rottweiler",
    "ihasaapso": "lhasa apso",
    "ihasa apso": "lhasa apso",
    "jack russel": "jack russell terrier",
    "jack russell": "jack russell terrier",
    "labradudley": "labradoodle",
    "lebre italiano": "galgo italiano",
    "lebrel italiano": "galgo italiano",
    "lulu": "spitz alemao",
    "lulu da pomerania": "spitz alemao",
    "shitzu": "shih tzu",
    "shi tzu": "shih tzu",
    "lulu da pimerania": "spitz alemao",
    "malamute da alaska": "alaskan malamute",
    "malamute do alasca": "alaskan malamute",
    "malamute do alaska": "alaskan malamute",
    "malamutti do alaska": "alaskan malamute",
    "maltes": "maltes",
    "mix de dachshund": "",
    "mix pastor alemao": "",
    "mix de pastor alemao": "",
    "pastor belga de malinois": "pastor belga malinois",
    "pastor belga malinos": "pastor belga malinois",
    "pastor branco": "",
    "pequenes": "pequines",
    "pibull": "pitbull",
    "pitbool": "pitbull",
    "pitbul": "pitbull",
    "pittbull": "pitbull",
    "pode toy": "poodle",
    "poodle toy (aproximadamente 12 meses)": "poodle",
    "putbull": "pitbull",
    "rd": "srd",
    "red heeler": "blue heeler",
    "rsb": "srd",
    "rsd": "srd",
    "salsicha": "dachshund",
    "schaunazer": "schnauzer",
    "scootish terrier": "scottish terrier",
    "sd": "srd",
    "sdr": "srd",
    "sed": "srd",
    "sem raca": "srd",
    "sharpei": "shar pei",
    "shar-pei": "shar pei",
    "sharpey": "shar pei",
    "shiba": "shiba inu",
    "shiba-inu": "shiba inu",
    "shiba inu": "shiba inu",
    "shiba inuu": "shiba inu",
    "shiba inuo": "shiba inu",
    "shibainu": "shiba inu",
    "shitisu": "shih tzu",
    "shitisu": "shih tzu",
    "shitzu": "shih tzu",
    "shit su": "shih tzu",
    "shih-tzu": "shih tzu",
    "shih tzu": "shih tzu",
    "shihtzu": "shih tzu",
    "shiht su": "shih tzu",
    "shiva": "shiba inu",
    "shiztsu": "shih tzu",
    "spitz japones": "spitz japones",
    "spitz japones": "spitz japones",
    "japanese spitz": "spitz japones",
    "sporting luca terrier": "sporting lucas terrier",
    "sporting lucas terrier": "sporting lucas terrier",
    "lucas terrier": "sporting lucas terrier",
    "sptiz": "spitz alemao",
    "srf": "srd",
    "srrd": "srd",
    "srs": "srd",
    "staffordshire bull": "staffordshire bull terrier",
    "staffordshire bull terrier": "staffordshire bull terrier",
    "starffordshire bull terrier": "staffordshire bull terrier",
    "staffordshire terrier": "staffordshire bull terrier",
    "stanforde hine": "staffordshire bull terrier",
    "taxas heeler": "texas heeler",
    "texas heeler": "texas heeler",
    "texa heeler": "texas heeler",
    "texaz heeler": "texas heeler",
    "weimaraner": "weimaraner",
    "weimaran": "weimaraner",
    "weimara": "weimaraner",
    "waimaraner": "weimaraner",
    "weimarer": "weimaraner",
    "weimaranen": "weimaraner",
    "west terrier": "west highland white terrier",
    "westie": "west highland white terrier",
    "west highland": "west highland white terrier",
    "west highland terrier": "west highland white terrier",
    "west highland white": "west highland white terrier",
    "west highland white terrier": "west highland white terrier",
    "westy": "west highland white terrier",
    "whippet": "whippet",
    "wippet": "whippet",
    "whipet": "whippet",
    "whipett": "whippet",
    "uippet": "whippet",
    "yorkshire biewer": "biewer terrier",
    "yorkshire bewer": "biewer terrier",
    "yorkshire biwer": "biewer terrier",
    "biewer yorkshire": "biewer terrier",
    "biewer york": "biewer terrier",
}

KNOWN_BREEDS = [
    "Labrador",
    "Golden Retriever",
    "Pastor Alemão",
    "Poodle",
    "Bulldog",
    "Shih Tzu",
    "Yorkshire",
    "Beagle",
    "Rottweiler",
    "Husky Siberiano",
    "Persa",
    "Siamês",
    "Maine Coon",
    "Akita",
    "Basset Hound",
    "American Bully",
    "Bernese Mountain Dog",
    "Biewer Terrier",
    "Border Collie",
    "Boston Terrier",
    "Boxer",
    "Bull Terrier",
    "Cane Corso",
    "Chinese Crested",
    "Cavalier King Charles Spaniel",
    "Chihuahua",
    "Pinscher",
    "Chow Chow",
    "Cocker Spaniel",
    "Coton de Tulear",
    "Dachshund",
    "Dálmata",
    "Doberman",
    "Dogue Alemão",
    "Fila Brasileiro",
    "Flat-Coated Retriever",
    "Foxhound",
    "Fox Paulistinha",
    "Fox Terrier",
    "Galgo Italiano",
    "Lhasa Apso",
    "Jack Russell Terrier",
    "Labradoodle",
    "Spitz Alemão",
    "Alaskan Malamute",
    "Maltês",
    "Pastor Australiano",
    "Pastor Belga",
    "Pastor Belga Malinois",
    "Pastor de Shetland",
    "Pelado Mexicano",
    "Pequinês",
    "Pointer Inglês",
    "Pug",
    "Blue Heeler",
    "Samoieda",
    "São Bernardo",
    "Schnauzer",
    "Scottish Terrier",
    "Shar-Pei",
    "Shiba Inu",
    "Spitz Japonês",
    "Sporting Lucas Terrier",
    "Staffordshire Bull Terrier",
    "Texas Heeler",
    "Weimaraner",
    "West Highland White Terrier",
    "Whippet",
]

AMBIGUOUS_TERMS = {
    "bull",
    "terrier",
    "pastor",
    "retriever",
    "bully",
}

MIX_SEPARATORS = [
    "/",
    "\\",
    ",",
    " e ",
    " com ",
    " - ",
    ";",
    "|",
]

def is_mixed_breed(text):
    if not text:
        return False

    text = text.lower()

    return (
        any(sep in text for sep in MIX_SEPARATORS)
        or "mix" in text
        or "misto" in text
        or "cruza" in text
        or "cruzamento" in text
    )

def normalize_for_match(text):
    return normalize_text(text).lower().replace(" ", "")

def fuzzy_match(text):
    if not text:
        return None

    normalized_text = normalize_for_match(text)

    if normalized_text in AMBIGUOUS_TERMS:
        return None

    choices = {normalize_for_match(b): b for b in KNOWN_BREEDS}

    match, score, _ = process.extractOne(
        normalized_text,
        choices.keys()
    )

    if score >= 75:
        return choices[match]

    return None

def normalize_text(text):
    if pd.isna(text):
        return ""

    text = str(text)
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")

def transform_breed(df: pd.DataFrame, column="raça") -> pd.DataFrame:

    # Unifica as colunas de raça existentes, sem falhar se alguma estiver ausente
    df[column] = df.get(
        column,
        pd.Series(pd.NA, index=df.index, dtype="object")
    )

    for alternative in ["raca", "pets.raca"]:
        if alternative in df.columns:
            df[column] = df[column].combine_first(df[alternative])

    df = df.drop(
        columns=["raca", "pets.raca"],
        errors="ignore"
    )

    col = (
        df[column]
        .astype(str)
        .str.strip()
        .str.lower()
        .apply(normalize_text)
    )

    # remove conteúdo entre parênteses
    col = col.str.replace(r'\s*\(.*?\)', '', regex=True).str.strip()

    # remove informações de idade/tempo
    col = col.str.replace(
        r'\baproximadamente\s*\d+\s*(anos?|meses?)\b',
        '',
        regex=True
    ).str.strip()

    col = col.str.replace(
        r'\b\d+\s*(anos?|meses?)\b',
        '',
        regex=True
    ).str.strip()

    # agora segue o resto
    col = col.str.replace(r'^[,.\s]+$', '', regex=True)
    col = col.where(~col.str.contains(r'\d'), None)
    col = col.where(col.str.len() >= 2, None)

    # limpa termos extras primeiro
    col = col.str.replace(r'\bflufli\b', '', regex=True)
    col = col.str.replace(r'\bfluffy\b', '', regex=True)

    col = col.str.replace(r"[-_]+", " ", regex=True)
    # normaliza espaços antes do replace
    col = col.str.replace(r'\s+', ' ', regex=True).str.strip()

    # só agora corrige typos
    col = col.replace(COMMON_TYPOS)

    # ==============================
    # MAPEAMENTO DIRETO
    # ==============================
    mapping = {
        "srd": "SRD",
        "vira lata": "SRD",
        "vira-lata": "SRD",
        "sem raca definida": "SRD",
        "sem raça definida": "SRD",
        "nao informado": "",
        "": "",

        "labrador": "Labrador",
        "golden retriever": "Golden Retriever",
        "pastor alemao": "Pastor Alemão",
        "poodle": "Poodle",
        "bulldog": "Bulldog",
        "shih tzu": "Shih Tzu",
        "yorkshire": "Yorkshire",
        "beagle": "Beagle",
        "rottweiler": "Rottweiler",
        "husky": "Husky Siberiano",
        "husky siberiano": "Husky Siberiano",

        "persa": "Persa",
        "siames": "Siamês",
        "maine coon": "Maine Coon",
        "akita": "Akita",
        "bascet": "Basset Hound",
        "basset": "Basset Hound",
        "basset hound": "Basset Hound",
        "bassett": "Basset Hound",
        "border collie": "Border Collie",
        "boiadeiro de berna": "Bernese Mountain Dog",
        "bulldog frances": "Bulldog Francês",
        "boston": "Boston Terrier",
        "boston terrier": "Boston Terrier",
        "boxer": "Boxer",
        "cane corso": "Cane Corso",
        "chinese crested": "Chinese Crested",
        "cavalier king charles spaniel": "Cavalier King Charles Spaniel",
        "chihuahua": "Chihuahua",
        "pinscher": "Pinscher",
        "chow": "Chow Chow",
        "chow chow": "Chow Chow",
        "cocker": "Cocker Spaniel",
        "cocker spaniel": "Cocker Spaniel",
        "coton de tulear": "Coton de Tulear",
        "dachshund": "Dachshund",
        "dalmata": "Dálmata",
        "doberman": "Doberman",
        "dogue alemao": "Dogue Alemão",
        "american bully": "American Bully",
        "fila brasileiro": "Fila Brasileiro",
        "flat coated": "Flat-Coated Retriever",
        "flat coated retriever": "Flat-Coated Retriever",
        "fox hound": "Foxhound",
        "foxhound": "Foxhound",
        "fox paulistinha": "Fox Paulistinha",
        "fox terrier": "Fox Terrier",
        "galgo italiano": "Galgo Italiano",
        "lhasa apso": "Lhasa Apso",
        "jack russell terrier": "Jack Russell Terrier",
        "labradoodle": "Labradoodle",
        "spitz alemao": "Spitz Alemão",
        "alaskan malamute": "Alaskan Malamute",
        "maltes": "Maltês",
        "pastor australiano": "Pastor Australiano",
        "pastor belga": "Pastor Belga",
        "pastor belga malinois": "Pastor Belga Malinois",
        "pastor de shetland": "Pastor de Shetland",
        "pelado mexicano": "Pelado Mexicano",
        "pequines": "Pequinês",
        "pointer ingles": "Pointer Inglês",
        "pug": "Pug",
        "blue heeler": "Blue Heeler",
        "samoeda": "Samoieda",
        "sao bernardo": "São Bernardo",
        "schnauzer": "Schnauzer",
        "scottish terrier": "Scottish Terrier",
        "shar pei": "Shar-Pei",
        "shiba inu": "Shiba Inu",
        "spitz japones": "Spitz Japonês",
        "sporting lucas terrier": "Sporting Lucas Terrier",
        "staffordshire bull terrier": "Staffordshire Bull Terrier",
        "texas heeler": "Texas Heeler",
        "weimaraner": "Weimaraner",
        "west highland white terrier": "West Highland White Terrier",
        "whippet": "Whippet",
        "biewer terrier": "Biewer Terrier",
    }

    result = col.map(mapping)

    # ==============================
    # HEURÍSTICA (contains)
    # ==============================
    def infer_breed(text):
        if pd.isna(text):
            return None

        text = str(text).strip().lower()

        if not text:
            return None
        
        if "srd" in text or "vira" in text:
            return "SRD"
        
        if is_mixed_breed(text):
            return ""

        if "labrador" in text:
            return "Labrador"
        if "golden" in text:
            return "Golden Retriever"
        if "pastor alemao" in text:
            return "Pastor Alemão"
        if "poodle" in text:
            return "Poodle"
        if "bull terrier" in text:
            return "Bull Terrier"
        if (
            ("bulldog" in text or "bull dog" in text or "buldogue" in text or "buldog" in text)
            and (
                "frances" in text
                or "francês" in text
                or "feances" in text
                or "fances" in text
                or "france" in text
            )
        ):
            return "Bulldog Francês"

        if "bulldog" in text or "bull dog" in text or "buldogue" in text or "buldog" in text:
            return "Bulldog"
        if "shih" in text:
            return "Shih Tzu"
        if (
            ("yorkshire" in text or "york" in text)
            and ("biewer" in text or "bewer" in text or "biwer" in text)
        ):
            return "Biewer Terrier"
        if "york" in text:
            return "Yorkshire"
        if "beagle" in text:
            return "Beagle"
        if "rott" in text:
            return "Rottweiler"
        if "husky" in text:
            return "Husky Siberiano"

        if "persa" in text:
            return "Persa"
        if "siam" in text:
            return "Siamês"
        if "maine" in text:
            return "Maine Coon"
        
        if "american bully" in text:
            return "American Bully"

        if "bully xl" in text:
            return "American Bully"

        if "pit bull" in text or "pitbull" in text:
            return "Pit Bull"
        
        if "border" in text or "boder" in text:
            return "Border Collie"
        if "boston" in text:
            return "Boston Terrier"
        if "boxer" in text:
            return "Boxer"
        if "cane corso" in text or "corso" in text:
            return "Cane Corso"
        if "chinese crested" in text or "crista chines" in text:
            return "Chinese Crested"
        if (
            "cavalier" in text
            or "king charles" in text
            or "charles spaniel" in text
        ):
            return "Cavalier King Charles Spaniel"
        if "chihuahua" in text or "chiuahua" in text or "chiwawa" in text:
            return "Chihuahua"
        if "pinscher" in text:
            return "Pinscher"
        if "chow" in text:
            return "Chow Chow"
        if "cocker" in text:
            return "Cocker Spaniel"
        if "coton" in text or "tulear" in text:
            return "Coton de Tulear"
        if "dalmata" in text:
            return "Dálmata"
        if "doberman" in text:
            return "Doberman"
        if "dogue alemao" in text or "great dane" in text:
            return "Dogue Alemão"
        if "exotic bully" in text or "micro bully" in text:
            return "American Bully"
        if "fila brasileiro" in text:
            return "Fila Brasileiro"
        if "flat coated" in text:
            return "Flat-Coated Retriever"
        if "fox hound" in text or "foxhound" in text:
            return "Foxhound"
        if "fox paulistinha" in text:
            return "Fox Paulistinha"
        if "fox terrier" in text:
            return "Fox Terrier"
        if "galgo italiano" in text:
            return "Galgo Italiano"
        if "lhasa apso" in text:
            return "Lhasa Apso"
        if "jack russell" in text:
            return "Jack Russell Terrier"
        if "labradoodle" in text:
            return "Labradoodle"
        if "spitz japones" in text:
            return "Spitz Japonês"
        if "spitz alemao" in text:
            return "Spitz Alemão"
        if "alaskan malamute" in text or "malamute da alaska" in text:
            return "Alaskan Malamute"
        if "maltes" in text:
            return "Maltês"
        if "pastor australiano" in text:
            return "Pastor Australiano"
        if "pastor belga malinois" in text or "pastor belga de malinois" in text:
            return "Pastor Belga Malinois"
        if "pastor belga" in text:
            return "Pastor Belga"
        if "pastor de shetland" in text:
            return "Pastor de Shetland"
        if "pelado mexicano" in text:
            return "Pelado Mexicano"
        if "pequines" in text:
            return "Pequinês"
        if "pointer ingles" in text:
            return "Pointer Inglês"
        if "pug" in text:
            return "Pug"
        if "blue heeler" in text:
            return "Blue Heeler"
        if "samoeda" in text:
            return "Samoieda"
        if "sao bernardo" in text:
            return "São Bernardo"
        if "schnauzer" in text:
            return "Schnauzer"
        if "scottish terrier" in text:
            return "Scottish Terrier"
        if "shar pei" in text:
            return "Shar-Pei"
        if "shiba" in text:
            return "Shiba Inu"
        if "sporting lucas terrier" in text or "lucas terrier" in text:
            return "Sporting Lucas Terrier"
        if (
            "staffordshire" in text
            or "stafford" in text
            or "stanforde" in text
        ):
            return "Staffordshire Bull Terrier"
        if "weimaran" in text or "weimarer" in text:
            return "Weimaraner"
        if (
            "west highland" in text
            or "westie" in text
            or "west terrier" in text
            or "westy" in text
        ):
            return "West Highland White Terrier"
        if "whippet" in text or "wippet" in text:
            return "Whippet"
            

        return None

    result = result.fillna(col.apply(infer_breed))
    result = result.fillna(col.apply(fuzzy_match))

    # mantém vazio se não souber
    df[column] = result.fillna("")

    return df
