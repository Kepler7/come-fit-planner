from pathlib import Path
import pandas as pd
from typing import List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
MENU_PATH = BASE_DIR / "data" / "menu_comefit_enriched.csv"

def load_menu() -> pd.DataFrame:
    """Carga el menú de Come Fit desde el CSV."""
    df = pd.read_csv(MENU_PATH)
    # Aseguramos que tags es string sin espacios extra
    df["tags"] = df["tags"].fillna("").astype(str).str.replace(" ", "")
    return df

def filter_menu(
    df: pd.DataFrame,
    meal_type: Optional[str] = None,
    must_have_tags: Optional[List[str]] = None,
    avoid_tags: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Filtra el menú por tipo de comida y tags."""
    filtered = df.copy()

    if meal_type:
        filtered = filtered[filtered["meal_type"] == meal_type]

    if must_have_tags:
        for tag in must_have_tags:
            filtered = filtered[filtered["tags"].str.contains(tag, case=False, na=False)]

    if avoid_tags:
        for tag in avoid_tags:
            filtered = filtered[~filtered["tags"].str.contains(tag, case=False, na=False)]

    return filtered


if __name__ == "__main__":
    # Pequeña prueba rápida
    df_menu = load_menu()
    print("Primeros platillos del menú:")
    print(df_menu.head())

    print("\nDesayunos para diabético (tag 'diabetico' o 'cero_azucar'):")
    df_desayunos = filter_menu(
        df_menu,
        meal_type="desayuno",
        must_have_tags=["cero_azucar"],
    )
    print(df_desayunos)