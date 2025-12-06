import os
import streamlit as st

if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]


from core.meal_planner_agent import generate_menu_plan

st.set_page_config(page_title="Come Fit Planner", page_icon="🥗", layout="centered")

st.title("Come Fit - Planificador de Menú Diario 🥗")

st.markdown(
    """
Bienvenido al planificador de menú de **Come Fit**.

Ingresa tus objetivos, calorías y restricciones, y te propondremos opciones de menú usando **solo nuestros platillos**.
"""
)

# --- Selección de objetivo ---
objective = st.selectbox(
    "¿Cuál es tu objetivo?",
    ["déficit calórico", "mantenimiento", "volumen"],
    index=0,
)

# --- Calorías por día ---
total_calories = st.number_input(
    "Calorías objetivo por día (aproximado)",
    min_value=800,
    max_value=4000,
    value=1600,
    step=50,
)

# --- Número de comidas ---
meals_per_day = st.selectbox(
    "Número de comidas al día",
    [3, 4],
    index=0,
    help="Por ahora usamos desayuno, comida y cena. Más adelante podemos agregar colaciones.",
)

st.subheader("Restricciones nutricionales (elige lo que aplique)")

col1, col2 = st.columns(2)

with col1:
    r_control_calorico = st.checkbox("Control calórico / Déficit", value=True)
    r_bajo_sodio = st.checkbox("Bajo en sodio")
    r_cero_azucar = st.checkbox("Cero azúcar / Apto diabéticos")

with col2:
    r_cero_gluten = st.checkbox("Cero gluten")
    r_post_op = st.checkbox("Post-operatorio")
    r_otros = st.text_input(
        "Otros tags (opcional, separados por coma)",
        help="Ejemplo: vegano,bajo_calorias",
    )

restrictions = []
if r_control_calorico:
    restrictions.append("control_calorico")
if r_bajo_sodio:
    restrictions.append("bajo_sodio")
if r_cero_azucar:
    restrictions.append("cero_azucar")
if r_cero_gluten:
    restrictions.append("cero_gluten")
if r_post_op:
    restrictions.append("post_operatorio")
if r_otros.strip():
    extras = [t.strip() for t in r_otros.split(",") if t.strip()]
    restrictions.extend(extras)

st.subheader("Alergias o cosas que quieres evitar")

c_no_lacteos = st.checkbox("Evitar lácteos")
c_no_gluten = st.checkbox("Evitar gluten (además del tag)")
c_no_nuez = st.checkbox("Evitar nueces / frutos secos")
c_otros = st.text_input(
    "Otros tags a evitar (opcional, separados por coma)",
    help="Ejemplo: alto_grasa",
)

allergies = []
if c_no_lacteos:
    allergies.append("lacteo")
if c_no_gluten:
    allergies.append("gluten")
if c_no_nuez:
    allergies.append("nuez")
if c_otros.strip():
    extras_avoid = [t.strip() for t in c_otros.split(",") if t.strip()]
    allergies.extend(extras_avoid)

st.markdown("---")

if st.button("Generar menú Come Fit"):
    with st.spinner("Generando tu menú personalizado..."):
        try:
            plan_text = generate_menu_plan(
                total_calories=total_calories,
                objective=objective,
                restrictions=restrictions,
                allergies=allergies,
                meals_per_day=meals_per_day,
            )

            st.subheader("Opciones de menú sugeridas")
            st.markdown(plan_text)

            st.info(
                "Estas son sugerencias basadas en el menú de Come Fit y tus objetivos. "
                "Puedes ajustar junto con nuestro equipo según tus necesidades específicas."
            )
        except Exception as e:
            st.error(f"Ocurrió un error al generar el menú: {e}")
