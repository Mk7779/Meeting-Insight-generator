import streamlit as st

st.set_page_config(page_title="My First Streamlit App")

st.title("🚀 My Streamlit Cloud App")
st.write("This app is deployed on Streamlit Cloud!")

name = st.text_input("Enter your name if mk" )
name = st.text_input("Enter your name if mk" )

if name:
    st.success(f"Hello, {name} 👋")
