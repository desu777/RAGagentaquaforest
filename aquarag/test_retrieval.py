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
INDEX_NAME = "aquaforest-9yo8nh1"  # z twojego URL
EMBEDDING_MODEL = "text-embedding-3-small"

def get_embedding(text):
    """Pobiera embedding dla tekstu"""
    response = OPENAI_CLIENT.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding

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
            
            # Embedding z pola "text"
            embedding = get_embedding(product["text"])
            
            # Przygotuj metadata (bez pola "text" - to będzie w embedding)
            metadata = {k: v for k, v in product.items() if k != "text"}
            
            # Dodaj do listy
            vectors_to_upsert.append({
                "id": product["id"],
                "values": embedding, 
                "metadata": metadata
            })
            
            print(f"✅ Przygotowano: {product['title']}")
            
        except Exception as e:
            print(f"❌ Błąd z {file_path}: {e}")
    
    # Wgraj do Pinecone
    if vectors_to_upsert:
        index.upsert(vectors=vectors_to_upsert, namespace="pl")
        print(f"🚀 Wgrano {len(vectors_to_upsert)} produktów do namespace 'pl'")

def test_retrieval(query, top_k=3):
    """Testuje wyszukiwanie"""
    index = PINECONE_CLIENT.Index(INDEX_NAME)
    
    # Embedding pytania
    query_embedding = get_embedding(query)
    
    # Wyszukaj w Pinecone
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
    # Wybierz operację
    print("=== AQUAFOREST RAG - TEST RETRIEVAL ===\n")
    
    action = input("Co chcesz zrobić?\n1. Wgrać produkty (ingest)\n2. Testować wyszukiwanie\n3. Oba\nWybór (1/2/3): ")
    
    if action in ["1", "3"]:
        print("\n🔄 Wgrywanie produktów...")
        ingest_products()
    
    if action in ["2", "3"]:
        print("\n🔍 Testowanie wyszukiwania...")
        
        # Przykładowe pytania testowe
        test_queries = [
            "jak obniżyć azotany NO3",
            "bakterie do akwarium", 
            "sól do akwarium morskiego",
            "probiotyki",
            "dawkowanie kropli"
        ]
        
        for query in test_queries:
            test_retrieval(query)
            print("-" * 50)
        
        # Pozwól użytkownikowi zadać własne pytania
        print("\n💬 Zadaj własne pytanie (Enter = koniec):")
        while True:
            user_query = input("Pytanie: ").strip()
            if not user_query:
                break
            test_retrieval(user_query)
            print("-" * 50)