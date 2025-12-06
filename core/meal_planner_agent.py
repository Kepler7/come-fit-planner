# core/meal_planner_agent.py
from __future__ import annotations

from typing import List, Dict, Any
from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.groq import Groq
from agno.models.openai import OpenAIChat
from agno.tools import tool

from core.menu_loader import load_menu, filter_menu
from core.planner import precompute_daily_suggestions  # <-- NUEVO IMPORT

# Cargamos variables de entorno
load_dotenv()

# Cargamos el menú una sola vez
MENU_DF = load_menu()


@tool()
def get_menu_options(
    meal_type: str,
    required_tags: str = "",
    avoid_tags: str = "",
) -> List[Dict[str, Any]]:
    """
    Devuelve los platillos de Come Fit filtrados por:
    - meal_type: desayuno, comida, cena, comida_cena, bebida, combo
    - required_tags: lista separada por comas, ej: "cero_azucar,cero_gluten"
    - avoid_tags: lista separada por comas, ej: "nuez,lacteos"
    """
    must_have = [t.strip() for t in required_tags.split(",") if t.strip()]
    avoid = [t.strip() for t in avoid_tags.split(",") if t.strip()]

    filtered = filter_menu(
        MENU_DF,
        meal_type=meal_type,
        must_have_tags=must_have if must_have else None,
        avoid_tags=avoid if avoid else None,
    )

    # Convertimos a una lista de dicts sencillos
    records = filtered.to_dict(orient="records")
    return records


def build_meal_planner_agent() -> Agent:
    """
    Crea el agente nutriólogo de Come Fit que sabe usar get_menu_options.
    """
    #model = OpenAIChat(id="gpt-4o-mini")  # puedes cambiar el modelo si quieres

    agent = Agent(
        model=Groq(id="llama-3.3-70b-versatile"),
        instructions=(
            "Eres un nutriólogo del restaurante Come Fit.\n\n"
            "Tu tarea es proponer MENÚS DIARIOS usando exclusivamente los platillos "
            "devueltos por la herramienta get_menu_options o por las sugerencias precalculadas "
            "que te dará el sistema.\n\n"
            "Recibirás: calorías objetivo, objetivo (déficit, mantenimiento o volumen), "
            "número de comidas al día y restricciones como 'cero_azucar', 'cero_gluten', "
            "'post_operatorio', etc.\n\n"
            "El sistema también te dará una lista de sugerencias por tipo de comida "
            "(desayuno, comida y cena), con calorías aproximadas calculadas para acercarse "
            "a las calorías objetivo por comida. Puedes combinar MÁS DE UN platillo en "
            "la misma comida (por ejemplo: omelet + pan francés en desayuno) para acercarte "
            "mejor al objetivo de calorías.\n\n"
            "Cuando el objetivo es DÉFICIT CALÓRICO, prefiere:\n"
            "- Dar más calorías en desayuno y comida.\n"
            "- Mantener una cena más ligera.\n"
            "No intentes compensar todo el déficit en la cena con un platillo enorme.\n\n"
            "Genera entre 1 y 3 opciones de menú diario. Cada opción debe mostrar:\n"
            "- Desayuno: uno o dos platillos (o más si tiene sentido) con sus calorías aproximadas.\n"
            "- Comida: uno o dos platillos.\n"
            "- Cena: idealmente más ligera en déficit.\n"
            "- Total aproximado de calorías sumando todos los platillos.\n\n"
            "Responde SIEMPRE en español y muestra los menús de forma clara y ordenada. "
            "Si alguna comida queda un poco arriba o abajo del objetivo, explícalo brevemente."
        ),
        tools=[get_menu_options],
        markdown=True,
    )
    return agent


def generate_menu_plan(
    total_calories: int,
    objective: str,
    restrictions: List[str],
    allergies: List[str],
    meals_per_day: int = 3,
) -> str:
    """
    Función de alto nivel que usaremos desde Streamlit.
    Ahora incluye una precálculo clásico de sugerencias por comida
    para acercarse a las calorías objetivo.
    """
    agent = build_meal_planner_agent()

    # 1) Precalcular sugerencias por tipo de comida basadas en calorías
    precomputed = precompute_daily_suggestions(
        total_calories=total_calories,
        meals_per_day=meals_per_day,
        restrictions=restrictions,
        allergies=allergies,
        objective=objective,
    )

    # Lo convertimos a un texto legible para el modelo
    suggestions = precomputed["suggestions"]
    per_meal_targets = precomputed["per_meal_targets"]
    distribution = precomputed["distribution"]

    suggestions_text_parts = []
    suggestions_text_parts.append(
        "Distribución sugerida de calorías por comida "
        f"(según el objetivo '{objective}'):\n"
    )

    for mt, frac in distribution.items():
        suggestions_text_parts.append(
            f"- {mt}: ~{frac*100:.0f}% del total "
            f"({per_meal_targets[mt]:.0f} kcal aprox.)"
        )

    suggestions_text_parts.append("\nSugerencias precalculadas por tipo de comida:")

    for meal_type, items in suggestions.items():
        suggestions_text_parts.append(f"\n- {meal_type.upper()}:")
        if not items:
            suggestions_text_parts.append("  (No se encontraron platillos con esas restricciones.)")
            continue
        for it in items:
            name = it.get("name", "Platillo")
            cals = it.get("calories", "N/D")
            price = it.get("price", "N/D")
            suggestions_text_parts.append(
                f"  • {name} (~{cals} kcal, precio aprox: {price})"
            )

    suggestions_text = "\n".join(suggestions_text_parts)
    restrictions_str = ",".join(restrictions) if restrictions else ""
    allergies_str = ",".join(allergies) if allergies else ""

    user_message = (
        f"Tengo el objetivo de '{objective}' con un total aproximado de "
        f"{total_calories} kcal al día.\n"
        f"Quiero {meals_per_day} comidas al día (desayuno, comida y cena).\n"
        f"Restricciones (tags que debes respetar): {restrictions_str or 'ninguna específica'}.\n"
        f"Alergias o cosas a evitar (tags): {allergies_str or 'ninguna'}.\n\n"
        "En déficit calórico, da preferencia a concentrar más calorías en desayuno y comida, "
        "dejando la cena más ligera. Puedes combinar varios platillos en una misma comida.\n\n"
        "El sistema ya hizo un precálculo clásico de opciones que se acercan a las calorías "
        "objetivo por comida. Aquí están las sugerencias:\n\n"
        f"{suggestions_text}\n\n"
        "Usa principalmente estas sugerencias para construir entre 1 y 3 opciones de menú diario "
        f"que se acerquen lo más posible a {total_calories} kcal en total. "
        "Si lo consideras útil, puedes complementar con otros platillos usando la herramienta "
        "get_menu_options, siempre respetando las restricciones."
    )


    run = agent.run(user_message)

    # Dependiendo de la versión de agno, puede ser .content o string
    try:
        return run.content
    except AttributeError:
        return str(run)


if __name__ == "__main__":
    # Prueba rápida desde la terminal:
    example_plan = generate_menu_plan(
        total_calories=1600,
        objective="déficit calórico",
        restrictions=["control_calorico"],
        allergies=["nuez"],  # aquí podrías usar algún tag que quieras evitar
        meals_per_day=3,
    )
    print(example_plan)
