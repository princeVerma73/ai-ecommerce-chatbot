import streamlit as st
from groq import Groq
import re
import sqlite3
import pandas as pd
from pathlib import Path
import shutil

# =============================
# GROQ CONFIG (STREAMLIT SAFE)
# =============================
client_sql = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)

MODEL = st.secrets["GROQ_MODEL"]

# =============================
# SQLITE SETUP (CRITICAL FIX)
# =============================
# Repo DB (read-only, must exist in app/)
REPO_DB_PATH = Path(__file__).parent / "db.sqlite"

# Writable DB location on Streamlit Cloud
TMP_DB_PATH = Path("/tmp/db.sqlite")

# Copy DB once at runtime
if not TMP_DB_PATH.exists():
    shutil.copy(REPO_DB_PATH, TMP_DB_PATH)

db_path = str(TMP_DB_PATH)

# =============================
# SQL PROMPT
# =============================
sql_prompt = """
You are an expert in understanding database schemas and generating SQL queries.

<schema>
table: product

fields:
product_link - string
title - string
brand - string
price - integer
discount - float
avg_rating - float
total_ratings - integer
</schema>

IMPORTANT RULES:
- Use ONLY the columns listed in the schema.
- NEVER use availability, stock, in_stock, status.
- If user asks about availability, ignore that condition.
- Brand search must be case-insensitive using LOWER(brand) LIKE '%value%'.
- Never use ILIKE.
- Always generate a SINGLE SQL query.
- Always use SELECT *.
- Wrap SQL inside <SQL></SQL> tags.

Interpret vague terms as follows:
- "highly rated" means avg_rating >= 4.2
- "best" means avg_rating >= 4.0
- "budget" means price <= 1000
- "cheap" means price <= 500
- "top" means ORDER BY avg_rating DESC
- If no number is given, always LIMIT 5
"""

# =============================
# GENERATE SQL FROM LLM
# =============================
def generate_sql_query(question: str) -> str:
    response = client_sql.chat.completions.create(
        messages=[
            {"role": "system", "content": sql_prompt},
            {"role": "user", "content": question},
        ],
        model=MODEL,
        temperature=0.2,
        max_tokens=1024,
    )
    return response.choices[0].message.content

# =============================
# RUN SQLITE QUERY
# =============================
def run_query(query: str):
    if query.strip().upper().startswith("SELECT"):
        with sqlite3.connect(db_path) as conn:
            return pd.read_sql_query(query, conn)

# =============================
# SQL CHAIN
# =============================
def sql_chain(question: str) -> str:
    sql_response = generate_sql_query(question)

    matches = re.findall(r"<SQL>(.*?)</SQL>", sql_response, re.DOTALL)

    if not matches:
        return "Sorry, I couldn't understand your query."

    sql_query = matches[0].strip()

    df = run_query(sql_query)
    if df is None or df.empty:
        return "No products found."

    context = df.head(5).to_dict(orient="records")
    return data_comprehension(question, context)

# =============================
# DATA COMPREHENSION
# =============================
comprehension_prompt = """
You are an expert in understanding the context of the question and replying based on the data provided.

Rules:
- Answer ONLY from the data.
- Do NOT use technical words.
- List products in numbered format.
- Each line must include: title, price in INR, discount, rating, and product link.
"""

def data_comprehension(question, context):
    response = client_sql.chat.completions.create(
        messages=[
            {"role": "system", "content": comprehension_prompt},
            {
                "role": "user",
                "content": f"QUESTION: {question} DATA: {context}",
            },
        ],
        model=MODEL,
        temperature=0.2,
    )
    return response.choices[0].message.content
