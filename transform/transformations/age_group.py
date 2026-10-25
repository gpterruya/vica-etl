import pandas as pd


def transform_age_group(
    df: pd.DataFrame,
    age_column="idade_adotante",
    output_column="faixa_etaria"
) -> pd.DataFrame:

    def classify(age):

        if pd.isna(age):
            return ""

        try:
            age = int(age)
        except:
            return ""

        if age < 18:
            return "0-17"

        elif age <= 24:
            return "18-24"

        elif age <= 34:
            return "25-34"

        elif age <= 44:
            return "35-44"

        elif age <= 59:
            return "45-59"

        else:
            return "60+"

    df[output_column] = df[age_column].apply(classify)

    return df