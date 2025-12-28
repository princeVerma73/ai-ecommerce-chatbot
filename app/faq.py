import pandas as pd
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()  # for .env file


#to access file path
faqs_path=Path(__file__).parent / "resources/faq_data.csv"
chroma_client=chromadb.Client()
collection_name_faq='faqs'
#groq_client=Groq()
def get_groq_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))



ef=embedding_functions.SentenceTransformerEmbeddingFunction(   # Converts questions → vectors
    model_name='sentence-transformers/all-MiniLM-L6-v2',       # means Used for semantic matching
)

# What happens inside: Ingest FAQ Data
# Read CSV
# Questions → documents
# Answers → metadata
# Generate unique IDs
# Store into ChromaDB
def ingest_faq_data(path):
    if collection_name_faq not in [c.name for c in chroma_client.list_collections()]:
        print("Ingesting FAQ data into Chromadb...")
        collection=chroma_client.get_or_create_collection(
            name=collection_name_faq,
            embedding_function=ef
        )
        df=pd.read_csv(path)
        docs=df['question'].to_list() #all the questions will go in docs
        metadata=[{'answer':ans} for ans in df['answer'].to_list()] #all the questions of .csv file will go in metadata
        ids=[f"id_{i}" for i in range(len(docs))]

        collection.add(
            documents=docs,
            metadatas=metadata,
            ids=ids
        )
        print(f"FAQ Data successfully ingested into Chroma collectiion:{collection_name_faq}")
    else: # exist after ingest data
        print(f"Collection {collection_name_faq} already exists!")



# Converts query → vector
# Finds top 2 most similar FAQ questions
# Returns their answers as context
def get_relevant_qa(query):
    collection=chroma_client.get_collection(name=collection_name_faq)
    result=collection.query(
        query_texts=[query],
        n_results=2
    )
    return result


# User Question
# → ChromaDB (semantic search)
# → Relevant answers (context)
# → LLM
# → Final answer
def faq_chain(query):
    groq_client = get_groq_client()
    result = get_relevant_qa(query)
    context = " ".join(
        r.get("answer", "") for r in result["metadatas"][0]
    )
    answer = generate_answer(query, context, groq_client)
    return answer


def generate_answer(query,context,groq_client): # tell the LLM
    prompt=f'''
    You are a customer support chatbot for an e-commerce company.
    Answer using ONLY the information provided in the context.
    
    Rules:
    - Always respond in first person plural (we / our).
    - If the question can be answered with Yes or No, START your answer with "Yes," or "No,".
    - After Yes/No, add a short helpful explanation if relevant.
    - If multiple options are present in the context, mention all of them.
    - Do NOT invent information.
    - If the answer is not found in the context, say "I don't know."
    
    QUESTION: {query}
    
    CONTEXT: {context}
    
    '''
    # LLM Call (Groq)
    # LLM does NOT search
    # LLM only formats answer using  context
    chat_completion=groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=os.environ['GROQ_MODEL'],
    )

    return chat_completion.choices[0].message.content




if __name__ == '__main__':
    ingest_faq_data(faqs_path)
    #query="what's your policy on defective products?"
    query="How long does it take to process a refund?"
    # result=get_relevant_qa(query)
    # print(result)
    answer=faq_chain(query)
    print(answer)

    # One - Line Flow
    # Query → ChromaDB(meaning search) → Context → LLM → Answer
