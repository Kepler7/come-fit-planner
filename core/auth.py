import streamlit as st
from core.database import SessionLocal, User
from sqlalchemy.exc import IntegrityError


def register_user(email, password):
    db = SessionLocal()
    try:
        user = User(email=email, password=password)
        db.add(user)
        db.commit()
        return True, "Cuenta creada con éxito"
    except IntegrityError:
        db.rollback()
        return False, "Ese correo ya está registrado"
    finally:
        db.close()


def login_user(email, password):
    db = SessionLocal()
    user = db.query(User).filter_by(email=email, password=password).first()
    db.close()

    if user:
        st.session_state["logged"] = True
        st.session_state["user_id"] = user.id
        st.session_state["email"] = user.email
        return True
    return False


def is_logged_in():
    return st.session_state.get("logged", False)


def logout():
    for key in ["logged", "user_id", "email"]:
        st.session_state.pop(key, None)

