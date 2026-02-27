import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["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"])

response = client.responses.create(
    model="gpt-4o-mini",
    input="תגיד שלום"
)

st.write(response.output_text)
