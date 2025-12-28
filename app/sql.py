from groq import Groq
import os
import re #regular expression
import sqlite3
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

GROQ_MODEL=os.getenv("GROQ_MODEL")
db_path=Path(__file__).parent / "db.sqlite"
client_sql=Groq()

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




def generate_sql_query(question):
    chat_completion = client_sql.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": sql_prompt,
            },
            {
                "role": "user",
                "content": question,
            }
        ],
        model=os.environ['GROQ_MODEL'],
        temperature=0.2,
        max_tokens=1024
    )
    return chat_completion.choices[0].message.content


def run_query(query):
    if query.strip().upper().startswith('SELECT'):
        with sqlite3.connect(db_path) as conn:
            df=pd.read_sql_query(query, conn)
            return df

def sql_chain(question):
    sql_response = generate_sql_query(question)

    pattern = r"<SQL>(.*?)</SQL>"
    matches = re.findall(pattern, sql_response, re.DOTALL)

    if len(matches) == 0:
        print("LLM OUTPUT:", sql_response)
        return "Sorry, LLM is not able to generate a query for your question"

    sql_query = matches[0].strip()
    print("SQL QUERY:", sql_query)

    response = run_query(sql_query)
    if response is None or response.empty:
        return "No products found."

    response = response.head(5) #max. to reduce context_length_exceeded
    context = response.to_dict(orient="records")
    answer = data_comprehension(question, context)
    return answer


comprehension_prompt ="""You are an expert in understanding the context of the question and replying based on the data pertaining to the question provided. 
You will be provided with QUESTION: and DATA:. The data will be in the form of an array or a dataframe or dict. 
Reply based on only the data provided as Data for answering the question asked as Question. 
Do not write anything like 'Based on the data' or any other technical words. Just a plain simple natural language response.
The Data would always be in context to the question asked. For example is the question is “What is the average rating?” and data is “4.3”, then answer should be “The average rating for the product is 4.3”.
So make sure the response is curated with the question and data. Make sure to note the column names to have some context, if needed, for your response.
There can also be cases where you are given an entire dataframe in the Data: field. Always remember that the data field contains the answer of the question asked. 
All you need to do is to always reply in the following format when asked about a product:
Produt title, price in indian rupees, discount, and rating, and then product link. Take care that all the products are listed in list format, one line after the other. Not as a paragraph.
For example:
1. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>
2. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>
3. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>
"""

def data_comprehension(question,context):
    chat_completion = client_sql.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": comprehension_prompt,
            },
            {
                "role": "user",
                "content": f"QUESTION: {question} DATA: {context}",
            }
        ],
        model=os.environ['GROQ_MODEL'],
        temperature=0.2,
        #max_tokens=1024
    )
    return chat_completion.choices[0].message.content



if __name__ == "__main__":
    #question = " All NIKE shoes with rating higher than 4.8"
    question="Give me PUMA shoes with rating higher than 4.5 and more than 30% discount"
    # sql_query = generate_sql_query(question)
    # print(sql_query)
    answer = sql_chain(question)
    print(answer)
    #query = "SELECT * from product where brand LIKE '%nike%'and price > 5000 and price < 10000"
    # df = run_query(query)
    # pass