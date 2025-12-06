# core/planner.py
from __future__ import annotations

from typing import List, Dict, Any, Literal
from core.menu_loader import load_menu, filter_menu


MealType = Literal["desayuno", "comida", "cena"]


def _choose_closest_by_calories(df, target_calories: float, max_options: int = 5):
    """
    Elige hasta max_options platillos con calorías más cercanas al objetivo.
    Si no hay calorías en el DF, devuelve algunos platillos sin ordenar.
    """
    if "calories" not in df.columns or df.empty:
        return df.head(max_options).to_dict(orient="records")

    df_cal = df.dropna(subset=["calories"])
    if df_cal.empty:
        # No hay calorías definidas, devolvemos algunos primeros
        return df.head(max_options).to_dict(orient="records")

    df_cal = df_cal.copy()
    df_cal["diff"] = (df_cal["calories"] - target_calories).abs()
    df_sorted = df_cal.sort_values("diff")
    return df_sorted.head(max_options).to_dict(orient="records")


def _get_meal_distribution(objective: str) -> Dict[MealType, float]:
    """
    Devuelve el porcentaje de calorías por comida según el objetivo.
    Los porcentajes deben sumar ~1.0.
    """
    obj = objective.lower()

    # Valores aproximados, puedes afinarlos
    if "déficit" in obj or "deficit" in obj:
        # más fuerte en la mañana y mediodía, cena ligera
        return {
            "desayuno": 0.35,
            "comida": 0.40,
            "cena": 0.25,
        }
    elif "volumen" in obj:
        # un poco más balanceado pero cargado a comida
        return {
            "desayuno": 0.30,
            "comida": 0.40,
            "cena": 0.30,
        }
    else:
        # mantenimiento u otros
        return {
            "desayuno": 0.30,
            "comida": 0.40,
            "cena": 0.30,
        }


def precompute_daily_suggestions(
    total_calories: int,
    meals_per_day: int,
    restrictions: List[str],
    allergies: List[str],
    objective: str,
) -> Dict[str, Any]:
    """
    Calcula sugerencias de platillos por tipo de comida, intentando
    aproximarse a las calorías objetivo por comida, con una distribución
    distinta para desayuno/comida/cena según el objetivo.
    """

    df = load_menu()

    meal_types: List[MealType] = ["desayuno", "comida", "cena"]
    distribution = _get_meal_distribution(objective)

    per_meal_targets: Dict[MealType, float] = {
        mt: total_calories * distribution[mt] for mt in meal_types
    }

    def _filter_for_meal(meal_type: MealType):
        # Filtrar por tipo de comida + restricciones + alergias
        must_have = restrictions or []
        avoid = allergies or []
        base = filter_menu(
            df,
            meal_type=meal_type,
            must_have_tags=must_have if must_have else None,
            avoid_tags=avoid if avoid else None,
        )
        return base

    suggestions: Dict[str, List[Dict[str, Any]]] = {}

    for mt in meal_types:
        base_df = _filter_for_meal(mt)
        target = per_meal_targets[mt]
        chosen = _choose_closest_by_calories(base_df, target, max_options=5)
        suggestions[mt] = chosen

    return {
        "total_calories": total_calories,
        "meals_per_day": len(meal_types),
        "per_meal_targets": per_meal_targets,
        "suggestions": suggestions,
        "distribution": distribution,
    }

