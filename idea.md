Buduje właśnie agenta RAG dla firmy aquaforest, natomiast nie wiem czy takie metadane są odpowiednie co przygotowałem. 
Cel i charakterystyka aplikacji AquaRAG
Twoja aplikacja to inteligentny asystent RAG (Retrieval-Augmented Generation) dla firmy Aquaforest, która specjalizuje się w produktach do akwarystyki. Główne cele:
🎯 Główny cel biznesowy:
Automatyzacja wsparcia klienta w zakresie produktów Aquaforest
Redukcja obciążenia działu support przez odpowiadanie na typowe pytania
Zwiększenie konwersji poprzez dokładne informacje o produktach i dawkowaniu
Obsługa wielojęzyczna (PL/EN + inne) z automatyczną detekcją języka 
┌──────── WordPress Widget (React) ──────┐
│  Greeting + Chat Interface + Feedback  │
└─────────────────────────────────────────┘
                │ REST API / SSE
                ▼
┌──────────── FastAPI + LangChain ─────────────┐
│ /chat    → RAG (embed → Pinecone → GPT)     │
│ /feedback → Email/CRM integration            │
│ /healthz → Monitoring                        │
└──────────────────────────────────────────────┘
        │                    │
        ▼                    ▼
  Pinecone Vector DB    OpenAI GPT-4o-mini
  (pl/en namespaces)    + text-embedding-3-small
Struktura danych:
Rodzaje treści:
Produkty (product) - informacje o preparatach, dawkowanie, ceny
FAQ (faq) - najczęściej zadawane pytania
Baza wiedzy (blog_post/guide) - artykuły edukacyjne
Kategorie produktów:
Seawater - akwaria morskie (NP Pro, Bios, sól Hybrid Pro Salt)
Freshwater - akwaria słodkowodne
Lab - testy i pomiary
OceanGuard - systemy monitoringu
🚀 Obecny stan rozwoju:
Zaimplementowane:
✅ Struktura danych produktów (JSON + metadata)
✅ Script testowy test_retrieval.py
✅ Przykładowe produkty kategorii Seawater
✅ Embedding i wyszukiwanie w Pinecone
✅ Plan architektury i roadmapa
Do zaimplementowania:
⏳ FastAPI backend z endpointami
⏳ React widget dla WordPress
⏳ System feedback i integracja z CRM
⏳ Wersja angielska i namespace EN
⏳ Deployment i monitoring
💡 Kluczowe zalety rozwiązania:
Kontekstowe odpowiedzi - bot wie o dawkowaniu, kompatybilności produktów
Metadata-driven - filtrowanie po kategoriach, tagach, językach
Fallback międzyjęzykowy - brak odpowiedzi w PL → sprawdza EN
Inteligentny feedback - niezadowolony użytkownik → automatyczny ticket do support
WordPress integration - widget wbudowany w istniejącą stronę
🎨 User Experience:
Użytkownik wchodzi na /pl/ → greeting po polsku
Pyta: "Jak obniżyć azotany w akwarium rafowym?"
System: wyszukuje w bazie → zwraca info o NP Pro + Pro Bio S + link do produktu
Niezadowolony? → klik 👎 → formularz kontaktowy → automatyczny mail do support
Podsumowując: To zaawansowany, branżowy chatbot który ma zastąpić część pracy działu obsługi klienta, oferując precyzyjne odpowiedzi o produktach akwarystycznych z możliwością escalacji do człowieka gdy AI nie wystarczy.

właśnie obmyśliłem plan dodania reasoningu przysłowiowego gdzie user zadaje pytanie -> pinecone zwraca coś -> model ocenia czy pinecone dało na tyle dobrą informacje by odpowiedzieć userowi? -> tak/nie -> jeśli nie wywołujemy tool calling z promptem od modelu do przeszukania znowu bazy wektorowej i znowu aż uzyskamy odpowiedni rezlutat, chyba że po 3 reasoningach w przysłowi nie znajdziemy nic to wtedy proponuje skonsultować się z supportem. Natomiast MVP -> język polski pracuje nad metadanymi. Czy wszystko oprócz text do embedingu, description oraz lang etc potrzebne nam są pola tags, price etc? skoro moglibyśmy to wszystko zawrzeć w description?