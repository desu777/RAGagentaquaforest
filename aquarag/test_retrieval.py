#!/usr/bin/env python3

import os
import json
from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

# Konfiguracja
OPENAI_CLIENT = OpenAI()
PINECONE_CLIENT = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
INDEX_NAME = "aquaforestseawater"  # poprawiona nazwa
EMBEDDING_MODEL = "text-embedding-3-small"

def get_embedding(text):
    """Pobiera embedding dla tekstu"""
    response = OPENAI_CLIENT.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding

def flatten_metadata(product):
    """Konwertuje metadane do płaskiego formatu akceptowalnego przez Pinecone"""
    metadata = {}
    for k, v in product.items():
        if k == "text":
            continue
        elif isinstance(v, dict):
            metadata[k] = "; ".join(f"{subk}: {subv}" for subk, subv in v.items())
        elif isinstance(v, list):
            # Zamień na listę stringów lub łańcuch
            if all(isinstance(i, dict) for i in v):
                metadata[k] = "; ".join(str(i) for i in v)
            else:
                metadata[k] = v
        else:
            metadata[k] = v
    return metadata

def ingest_products():
    """Wgrywa produkty do Pinecone"""
    index = PINECONE_CLIENT.Index(INDEX_NAME)

    # Lista plików produktów
    product_files = [
        "produkty/seawater/afnitraphosminus.json",
        "produkty/seawater/bios.json", 
        "produkty/seawater/hybridprosalt.json",
        "produkty/seawater/nppro.json",
        "produkty/seawater/probiof.json",
        "produkty/seawater/probios.json"
    ]

    vectors_to_upsert = []

    for file_path in product_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                product = json.load(f)

            embedding = get_embedding(product["text"])
            metadata = flatten_metadata(product)

            vectors_to_upsert.append({
                "id": product["id"],
                "values": embedding,
                "metadata": metadata
            })

            print(f"✅ Przygotowano: {product['title']}")

        except Exception as e:
            print(f"❌ Błąd z {file_path}: {e}")

    if vectors_to_upsert:
        index.upsert(vectors=vectors_to_upsert, namespace="pl")
        print(f"🚀 Wgrano {len(vectors_to_upsert)} produktów do namespace 'pl'")

def test_retrieval(query, top_k=3):
    """Testuje wyszukiwanie"""
    index = PINECONE_CLIENT.Index(INDEX_NAME)
    query_embedding = get_embedding(query)

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        namespace="pl",
        include_metadata=True
    )

    print(f"\n🔍 Pytanie: '{query}'")
    print(f"📊 Znaleziono {len(results.matches)} wyników:\n")

    for i, match in enumerate(results.matches, 1):
        score = match.score
        title = match.metadata.get('title', 'Brak tytułu')
        slug = match.metadata.get('slug', '')
        print(f"{i}. {title} (score: {score:.3f})")
        print(f"   slug: {slug}")
        print(f"   url: {match.metadata.get('url', '')}")
        print()

if __name__ == "__main__":
    print("=== AQUAFOREST RAG - TEST RETRIEVAL ===\n")
    action = input("Co chcesz zrobić?\n1. Wgrać produkty (ingest)\n2. Testować wyszukiwanie\n3. Oba\nWybór (1/2/3): ")

    if action in ["1", "3"]:
        print("\n🔄 Wgrywanie produktów...")
        ingest_products()

    if action in ["2", "3"]:
        print("\n🔍 Testowanie wyszukiwania...")

        test_queries = [
            "Pro Bio S dawkowanie dzienne",
            "Skrócić cykl azotowy bakterie startowe",
            "Jak obniżyć NO3 bez filtra fluidyzacyjnego",
            "Płynne źródło węgla do probiotyków",
            "Redukcja NO3 i PO4 w rafie",
            "Hybrid Pro Salt parametry przy 35 ppt",
            "Probiotyk do małego zbiornika zamiast VSV",
            "Ile kropli NP Pro bez pompy dozującej",
            "Bakterie Nitrospirae do startu akwarium",
            "Jaka pożywka do Pro Bio S",
            "Obniżyć NO2 i amoniak jednocześnie",
            "Sól dla SPS – ile gram na 10 l",
            "Nitraphos Minus dawkowanie",
            "carbon source NP-lowering",
            "Test KH do SPS"
        ]


        for query in test_queries:
            test_retrieval(query)
            print("-" * 50)

        print("\n💬 Zadaj własne pytanie (Enter = koniec):")
        while True:
            user_query = input("Pytanie: ").strip()
            if not user_query:
                break
            test_retrieval(user_query)
            print("-" * 50)
