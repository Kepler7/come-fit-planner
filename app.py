import os
import streamlit as st
import base64

from core.meal_planner_agent import generate_menu_plan
from core.database import init_database, SessionLocal, MenuGenerated
from core.auth import register_user, login_user, is_logged_in, logout

st.set_page_config(page_title="Come Fit Planner", page_icon="🥗")

def load_bg_base64():
    bg_path = os.path.join("data", "fondo.png")
    if not os.path.exists(bg_path):
        return ""
    with open(bg_path, "rb") as img:
        return base64.b64encode(img.read()).decode()


bg_image = load_bg_base64()

st.markdown(f"""
<style>
.stApp {{
    background-image: url("data:image/png;base64,{bg_image}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
</style>
""", unsafe_allow_html=True)

init_database()


with st.sidebar:
    st.header("🍽️ Menú")

    if is_logged_in():
        st.success(f"Sesión iniciada como: {st.session_state.get('email')}")

        if st.button("Cerrar sesión"):
            logout()
            st.experimental_rerun()


    option = st.selectbox("Opciones", ["Iniciar sesión", "Registrarse", "Instagram", "WhatsApp"])

    if option == "Instagram":
        st.markdown("[Ir a Instagram](https://www.instagram.com/comesano_comefit)")
    elif option == "WhatsApp":
        st.markdown("[Contactar por WhatsApp](https://wa.me/5213349776792)")

    if option == "Registrarse":
        st.subheader("Crear cuenta")
        email = st.text_input("Correo")
        password = st.text_input("Contraseña", type="password")

        if st.button("Crear cuenta"):
            ok, msg = register_user(email, password)
            st.success(msg) if ok else st.error(msg)

    if option == "Iniciar sesión":
        st.subheader("Acceso")
        email = st.text_input("Correo", key="login_email")
        password = st.text_input("Contraseña", type="password", key="login_pass")
        
        if st.button("Entrar"):
            if login_user(email, password):
                st.success("Sesión iniciada")
                st.rerun()
            else:
                st.error("Credenciales incorrectas")

st.title("🍏 Generador de menú Come Fit")

total_calories = st.number_input("Calorías totales por día", min_value=1200, max_value=5000, value=2000)
objective = st.selectbox("Objetivo", ["Bajar de peso", "Mantener", "Subir masa"])
restrictions = st.text_input("Restricciones (opcional)")
allergies = st.text_input("Alergias (opcional)")
meals_per_day = st.selectbox("Comidas por día", [3, 4, 5])


if st.button("Generar menú Come Fit"):
    if not is_logged_in():
        st.warning("Debes iniciar sesión para generar tu menú.")
        st.stop()

    with st.spinner("Generando menú..."):
        try:
            plan_text = generate_menu_plan(
                total_calories=total_calories,
                objective=objective,
                restrictions=restrictions,
                allergies=allergies,
                meals_per_day=meals_per_day,
            )

            db = SessionLocal()
            new_menu = MenuGenerated(user_id=st.session_state["user_id"], menu_text=plan_text)
            db.add(new_menu)
            db.commit()
            db.close()

            st.subheader("Menú generado")
            st.markdown(plan_text)

        except Exception as e:
            st.error(f"Error: {e}")
