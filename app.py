import os
import streamlit as st
import base64

# -----------------------------
#  FONDO DE LA APLICACIÓN
# -----------------------------
def set_background(image_file):
    try:
        with open(image_file, "rb") as f:
            data = f.read()
        encoded = base64.b64encode(data).decode()

        css = f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ No se encontró el fondo. Verifica la ruta: 'data/fondo.png'")

set_background("data/fondo.png")


# -----------------------------
#  CARGAR GROQ API KEY
# -----------------------------
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]


# -----------------------------
#  CONFIGURACIÓN DE LA APP
# -----------------------------
st.set_page_config(
    page_title="Come Fit Planner",
    page_icon="🥗",
    layout="centered"
)

from core.meal_planner_agent import generate_menu_plan


# -----------------------------
#  LOGO Y TÍTULO
# -----------------------------
col_logo, col_title = st.columns([2, 5])

with col_logo:
    try:
        st.image("data/logo.png", width=120)
    except:
        st.warning("⚠️ No se encontró 'data/logo.png'")

with col_title:
    st.title("Come Fit - Planificador de Menú Diario 🥗")


st.markdown("""
Bienvenido al planificador de menú de **Come Fit**.

Ingresa tus objetivos, calorías y restricciones, y te propondremos opciones de menú usando **solo nuestros platillos**.
""")


# -----------------------------
#  FORMULARIO
# -----------------------------

objective = st.selectbox(
    "¿Cuál es tu objetivo?",
    ["déficit calórico", "mantenimiento", "volumen"]
)

total_calories = st.number_input(
    "Calorías objetivo por día (aproximado)",
    min_value=800,
    max_value=4000,
    value=1600,
    step=50
)

meals_per_day = st.selectbox(
    "Número de comidas al día",
    [3, 4],
    index=0
)

st.subheader("Restricciones nutricionales")

col1, col2 = st.columns(2)

with col1:
    r_control_calorico = st.checkbox("Control calórico / Déficit", value=True)
    r_bajo_sodio = st.checkbox("Bajo en sodio")
    r_cero_azucar = st.checkbox("Cero azúcar / Apto diabéticos")

with col2:
    r_cero_gluten = st.checkbox("Cero gluten")
    r_post_op = st.checkbox("Post-operatorio")
    r_otros = st.text_input("Otros tags (separados por coma)")

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
    restrictions.extend([t.strip() for t in r_otros.split(",") if t.strip()])


# -----------------------------
#  ALERGIAS
# -----------------------------
st.subheader("Alergias o cosas a evitar")

c_no_lacteos = st.checkbox("Evitar lácteos")
c_no_gluten = st.checkbox("Evitar gluten")
c_no_nuez = st.checkbox("Evitar nueces / frutos secos")
c_otros = st.text_input("Otros a evitar (separados por coma)")

allergies = []
if c_no_lacteos:
    allergies.append("lacteo")
if c_no_gluten:
    allergies.append("gluten")
if c_no_nuez:
    allergies.append("nuez")
if c_otros.strip():
    allergies.extend([t.strip() for t in c_otros.split(",") if t.strip()])


# -----------------------------
#  ÍCONOS CLICKEABLES
# -----------------------------
st.markdown("### Contáctanos")

whatsapp_url = "https://wa.me/5213349776792"
instagram_url = "https://www.instagram.com/comesano_comefit"

st.markdown(
    f"""
    <a href="{whatsapp_url}" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="40">
    </a>
    <a href="{instagram_url}" target="_blank" style="margin-left:15px;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png" width="40">
    </a>
    """,
    unsafe_allow_html=True
)


# -----------------------------
#  GENERAR MENÚ
# -----------------------------
st.markdown("¿Ya generaste tu menú?")

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

            st.info("Sugerencias basadas en el menú Come Fit.")
        except Exception as e:
            st.error(f"Error al generar el menú: {e}")
