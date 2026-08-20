# Local RAG Assistant

PDF dokümanları üzerinde çalışan, tamamen yerel (local) modellerle çalışan basit bir RAG (Retrieval-Augmented Generation) uygulaması. Azure AI Foundry Local üzerinden çalıştırılan bir embedding modeli ve bir LLM kullanılarak, sorulan sorular yalnızca yüklenen dokümanlardaki bilgilere dayanarak cevaplanır.

## Mimari

```
Soru
  ↓
Embedding (qwen3-embedding-0.6b)
  ↓
Semantic Retrieval (cosine similarity, SQLite)
  ↓
Top-K Chunk Seçimi + Kaynakça Filtreleme
  ↓
Context Oluşturma
  ↓
Generation (phi-4-mini)
  ↓
Cevap
```

## Kullanılan Teknolojiler

- **Python 3.11**
- **Azure AI Foundry Local** — yerel LLM ve embedding modeli sunucusu (OpenAI uyumlu API)
- **qwen3-embedding-0.6b** — embedding modeli
- **phi-4-mini** — cevap üretimi (generation) modeli
- **SQLite** — chunk ve embedding depolama
- **FastAPI** — REST API katmanı
- **pypdf** — PDF metin çıkarımı

## Kurulum

1. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

2. [Azure AI Foundry Local](https://learn.microsoft.com/azure/ai-foundry/foundry-local/) kurun ve şu modelleri indirin:
   - `qwen3-embedding-0.6b`
   - `phi-4-mini`

3. Foundry Local'i başlatın ve verdiği portu not edin. `src/search.py` ve `src/insert_pdf.py` içindeki `base_url` değerini kendi portunuza göre güncelleyin:
   ```python
   client = OpenAI(
       base_url="http://127.0.0.1:PORT/v1",
       api_key="not-needed"
   )
   ```

4. Veritabanı şemasını oluşturun:
   ```bash
   python src/database.py
   ```

5. PDF dosyalarınızı `data/pdfs/` klasörüne koyun ve embedding'leri oluşturun:
   ```bash
   python src/insert_pdf.py
   ```

## Kullanım

### CLI üzerinden sorgulama

```bash
python src/search.py
```

### API üzerinden sorgulama

```bash
uvicorn src.api:app --reload
```

Sonra:
```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the relationship between sleep and memory?"}'
```

### Frontend

`frontend/index.html` dosyasını tarayıcıda açarak basit bir arayüz üzerinden de sorgulama yapabilirsiniz (API'nin çalışıyor olması gerekir).

## Proje Yapısı

```
LocalRAG/
├── data/
│   ├── pdfs/           # Kaynak PDF dosyaları
│   └── rag.db          # Chunk + embedding veritabanı
├── frontend/
│   └── index.html      # Basit web arayüzü
├── src/
│   ├── database.py     # Veritabanı şeması oluşturma
│   ├── insert_pdf.py   # PDF → chunk → embedding → veritabanı
│   ├── search.py       # Retrieval + generation (CLI)
│   ├── api.py           # FastAPI endpoint
│   └── test_retrieval.py  # Retrieval testleri
├── requirements.txt
└── README.md
```

## Notlar

- Kaynakça/referans metinlerinin retrieval sonuçlarına karışmasını önlemek için basit bir filtre (`looks_like_reference`) kullanılmaktadır.
- Context uzunluğu `max_chars` parametresi ile sınırlandırılmıştır (varsayılan 6000 karakter).
- Bu proje, RAG pipeline'ının temel bileşenlerini (chunking, embedding, retrieval, context management, generation) öğrenme amacıyla adım adım geliştirilmiştir.
