import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MENU_PATH = os.path.join(DATA_DIR, "menu_comefit_enriched.csv")


def load_menu():
    print("Cargando CSV desde:", MENU_PATH)
    df = pd.read_csv(MENU_PATH)

    if "tags" in df.columns:
        df["tags"] = df["tags"].fillna("").apply(lambda x: [t.strip() for t in str(x).split(",") if t.strip()])

    return df


def filter_menu(df, meal_type=None, must_have_tags=None, avoid_tags=None):
    """
    Filtro real basado en:
    - meal_type (columna en CSV)
    - must_have_tags (lista)
    - avoid_tags (lista)
    """

    filtered = df.copy()

    if meal_type:
        filtered = filtered[filtered["meal_type"] == meal_type]

    if must_have_tags:
        for tag in must_have_tags:
            filtered = filtered[filtered["tags"].apply(lambda t: tag in t)]

    if avoid_tags:
        for tag in avoid_tags:
            filtered = filtered[filtered["tags"].apply(lambda t: tag not in t)]

    return filtered



