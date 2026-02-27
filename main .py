import streamlit as st
from openai import OpenAI

api_key = st.secrets["OPENAI_API_KEY"].strip()
project_id = st.secrets["OPENAI_PROJECT_ID"].strip()
org_id = st.secrets["OPENAI_ORG_ID"].strip()

client = OpenAI(
    api_key=api_key,
    project=project_id,
    organization=org_id,
)

r = client.responses.create(
    model="gpt-4o-mini",
    input="תגיד שלום"
)

st.write(r.output_text)
