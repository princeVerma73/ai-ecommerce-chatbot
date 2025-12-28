from semantic_router import Route
from semantic_router.routers import SemanticRouter
from semantic_router.encoders import HuggingFaceEncoder
# # it means You are NOT calling the website.
# Model comes from Hugging Face’s model hub
# Not because it calls the website every time
from semantic_router.index import LocalIndex
from pathlib import Path
from semantic_router import Route

import shutil

# Define index path FIRST
index_save_dir = Path(__file__).parent / ".semantic_router"

# Now safe to delete old cache
shutil.rmtree(index_save_dir, ignore_errors=True)

# Recreate folder
index_save_dir.mkdir(exist_ok=True)

# Encoder: Converts text → vectors
encoder = HuggingFaceEncoder(
    name="sentence-transformers/all-MiniLM-L6-v2"
)

# Stores embeddings locally
index = LocalIndex(
    name="my_local_index",
    save_dir=index_save_dir
)


# Define routes
faq = Route(
    name="FAQ",
    utterances=[
        "What is the return policy of the products?",
        "Do I get discount with the HDFC credit card?",
        "How can I track my order?",
        "What payment methods are accepted?",
        "How long does it take to process a refund?",
        "What should I do if I receive a damaged product?",
        "What is your policy on defective products?",
    ],
)

sql = Route(
    name="sql",
    utterances=[
        "shoes",
        "top shoes",
        "best shoes",
        "nike shoes",
        "puma shoes",
        "shoes under price",
        "shoes with rating",
        "sorted by rating",
        "shoe recommendations",
        "search products",
        "product query",
    ]
)


routes = [faq, sql]

# Manually populate index
# (Required for your library version)
all_utterances = []
route_mapping = []

for route in routes:
    for utterance in route.utterances:
        all_utterances.append(utterance)
        route_mapping.append(route.name)

# Create embeddings
embeddings = encoder(all_utterances)

# Add to index (IMPORTANT)
index.add(
    embeddings=embeddings,
    utterances=all_utterances,
    routes=route_mapping
)

# Build semantic router
router = SemanticRouter(
    routes=routes,
    encoder=encoder,
    index=index,
    top_k=1,
)

# Test
if __name__ == "__main__":
    print(router("What is your policy on defective products?").name)
    print(router("Pink puma shoes in price range 5000 to 10000").name)
