# 🛒 AI E-Commerce Chatbot (SQL + LLM)

An **AI-powered e-commerce chatbot for flipkart** that understands natural language queries and answers them by dynamically generating **SQL queries** over a product database.

This project combines **LLMs, SQL, semantic routing, and web-scraped data** to deliver accurate, context-aware product recommendations.

---

## 🚀 Features

- 🔍 **Natural Language to SQL**
  - Ask questions like:
    - *“Show shoes under 500”*
    - *“Top 3 Puma shoes sorted by rating”*
    - *“Cheapest shoes with rating above 4”*

- 🧠 **LLM-Driven SQL Generation**
  - Uses an LLM (via Groq API) to generate SQL queries dynamically.

- 🧭 **Semantic Routing**
  - Automatically routes user queries to:
    - **SQL engine** (for product search)
    - **FAQ engine** (for platform-related questions)

- 🗄️ **SQLite Database**
  - Product data stored locally in `db.sqlite`
  - Efficient querying using Pandas + SQLite

- 🧹 **Web Scraping Pipeline**
  - Scraped real Flipkart product data using Selenium
  - Cleaned and converted CSV → SQLite

- 💬 **Conversational Responses**
  - Outputs human-readable answers with:
    - Product name
    - Price
    - Discount
    - Rating
    - Direct product link

---

## 🧩 Tech Stack

- **Python**
- **SQLite**
- **Pandas**
- **Selenium**
- **Groq LLM API**
- **Semantic Router**
- **Streamlit** (UI)
- **Git & GitHub**

---

## 📂 Project Structure

```
Business_Project2/
│
├── app/
│   ├── main.py          # Streamlit app entry point
│   ├── router.py        # Semantic routing (FAQ vs SQL)
│   ├── sql.py           # LLM → SQL generation + execution
│   ├── faq.py           # FAQ handling
│   ├── db.sqlite        # Product database
│   └── resources/
│       └── faq_data.csv
│
├── web-scrapping/
│   ├── flipkart_data_extraction.ipynb
│   ├── csv_to_sqlite.ipynb
│   ├── flipkart_products.csv
│   └── failed_links.csv
│
├── .gitignore
├── README.md
└── requirements.txt
```
```
🧪 Example Queries
* show shoes under 500
* top 3 puma shoes under 2000
* cheapest shoes with rating above 4
* best shoes under 1000
* nike shoes under 5000 with rating above 4.5
```
```
▶️ How to Run Locally

1️⃣ Clone the repository
      git clone https://github.com/princeVerma73/ai-ecommerce-chatbot.git
      cd ai-ecommerce-chatbot
2️⃣ Install dependencies
      pip install -r requirements.txt
3️⃣ Set environment variables
      GROQ_API_KEY=your_api_key_here
      GROQ_MODEL=llama-3.3-70b-versatile
4️⃣ Run the app
      streamlit run app/main.py
```
```
👤 Author
Prince Verma
📧 Aspiring Data Scientist | GenAI Enthusiast
🔗 GitHub: princeVerma73
```


