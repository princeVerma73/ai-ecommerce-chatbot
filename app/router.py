from semantic_router import Route
from semantic_router.routers import SemanticRouter
from semantic_router.encoders import HuggingFaceEncoder
from semantic_router.index import LocalIndex
from pathlib import Path

# -----------------------------
# Persistent index directory
# -----------------------------
index_save_dir = Path("/tmp/semantic_router")
index_save_dir.mkdir(exist_ok=True)

# -----------------------------
# Encoder (HF model)
# -----------------------------
encoder = HuggingFaceEncoder(
    name="sentence-transformers/all-MiniLM-L6-v2"
)

# -----------------------------
# Local index (persistent)
# -----------------------------
index = LocalIndex(
    name="my_local_index",
    save_dir=index_save_dir
)

# -----------------------------
# Define routes
# -----------------------------
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

# -----------------------------
# Build index ONLY ONCE
# -----------------------------
if index.count() == 0:
    all_utterances = []
    route_mapping = []

    for route in routes:
        for utterance in route.utterances:
            all_utterances.append(utterance)
            route_mapping.append(route.name)

    embeddings = encoder(all_utterances)

    index.add(
        embeddings=embeddings,
        utterances=all_utterances,
        routes=route_mapping
    )

# -----------------------------
# Semantic Router
# -----------------------------
router = SemanticRouter(
    routes=routes,
    encoder=encoder,
    index=index,
    top_k=1,
)

# -----------------------------
# Test locally (optional)
# -----------------------------
if __name__ == "__main__":
    print(router("What is your policy on defective products?").name)
    print(router("Pink puma shoes in price range 5000 to 10000").name)
