import streamlit as st
from openai import OpenAI

api_key = st.secrets["OPENAI_API_KEY"].strip()
st.write("key prefix:", api_key[:7])
st.write("len:", len(api_key))
st.write("has newline:", "\n" in api_key)

client = OpenAI(api_key=api_key)

r = client.responses.create(model="gpt-4o-mini", input="תגיד שלום")
st.write(r.output_text)
