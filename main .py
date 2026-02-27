import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

response = client.responses.create(
    model="gpt-4o-mini",
    input="תגיד שלום"
)

st.write(response.output_text)
