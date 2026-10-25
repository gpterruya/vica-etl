import logging

from .transformations.birth_date import transform_birth_date
from .transformations.state import transform_state
from .transformations.city import transform_city
from .transformations.neighbourhood import transform_neighbourhood
from .transformations.age import transform_age
from .transformations.created_at import transform_created_at
from .transformations.species import transform_species
from .transformations.breed import transform_breed
from .transformations.size import transform_size
from .transformations.age_group import transform_age_group


def transform(df):
    logging.info("Transformando data de nascimento...")
    df = transform_birth_date(df)

    logging.info("Transformando idade...")
    df = transform_age(df)

    logging.info("Transformando estado...")
    df = transform_state(df)

    logging.info("Transformando cidade...")
    df = transform_city(df)

    logging.info("Transformando bairro...")
    df = transform_neighbourhood(df)

    logging.info("Transformando data de criação...")
    df = transform_created_at(df)

    logging.info("Transformando espécie...")
    df = transform_species(df)

    logging.info("Transformando raça...")
    df = transform_breed(df)

    logging.info("Transformando porte...")
    df = transform_size(df)

    logging.info("Transformando faixa etária...")
    df = transform_age_group(df)

    logging.info("Transformações concluídas.")

    return df