
# Local RAG Assistant

PDF dokümanları üzerinde çalışan, **yerel (local) bir Retrieval-Augmented Generation (RAG)** uygulaması.

Uygulama, **Azure AI Foundry Local** kullanarak embedding modelini ve Large Language Model'i (LLM) yerel olarak çalıştırır. PDF dokümanları metin parçalarına (chunks) ayrılır, embedding'lere dönüştürülür ve SQLite veritabanında saklanır. Kullanıcının sorusu da embedding'e dönüştürülerek semantic similarity üzerinden en ilgili içerikler bulunur. Retrieved context, yerel LLM'e verilerek cevap oluşturulur.

Projenin temel amacı; **document processing, chunking, embeddings, semantic retrieval, context management ve local LLM generation** gibi RAG sistemlerinin temel bileşenlerini uygulamalı olarak öğrenmek ve uçtan uca çalışan bir local RAG pipeline geliştirmektir.

## Özellikler

- 📄 PDF dokümanlarından otomatik metin çıkarma
- ✂️ Metinleri daha küçük chunk'lara ayırma
- 🔢 Local embedding generation
- 🔎 Cosine similarity ile semantic retrieval
- 🗄️ SQLite ile local chunk ve embedding storage
- 🚫 Kaynakça/reference chunk'larının retrieval'dan filtrelenmesi
- 🤖 `phi-4-mini` ile local LLM generation
- 💻 CLI üzerinden sorgulama
- 🌐 FastAPI REST API
- 🖥️ Basit web frontend
- 🔒 Local model inference
- 🧪 Retrieval testleri

## Mimari

```text
Kullanıcı Sorusu
       ↓
Query Embedding
(qwen3-embedding-0.6b)
       ↓
Semantic Retrieval
(Cosine Similarity + SQLite)
       ↓
Top-K Chunk Seçimi
+ Kaynakça Filtreleme
       ↓
Context Oluşturma
       ↓
Local LLM Generation
(phi-4-mini)
       ↓
Cevap
```

## RAG Pipeline

Sistem aşağıdaki adımlardan oluşur:

1. **PDF Ingestion** — PDF dosyalarından metin `pypdf` kullanılarak çıkarılır.
2. **Chunking** — Çıkarılan metin daha küçük parçalara ayrılır.
3. **Embedding Generation** — Her chunk, `qwen3-embedding-0.6b` modeli ile embedding'e dönüştürülür.
4. **Local Storage** — Chunk'lar ve embedding'leri SQLite veritabanında saklanır.
5. **Query Embedding** — Kullanıcının sorusu aynı embedding modeli ile vektöre dönüştürülür.
6. **Semantic Retrieval** — Soru embedding'i ile kayıtlı chunk embedding'leri arasında cosine similarity hesaplanır.
7. **Filtering & Top-K Selection** — En ilgili chunk'lar seçilir ve reference-like chunk'lar filtrelenir.
8. **Context Construction** — Seçilen chunk'lar LLM'e gönderilecek context'i oluşturur.
9. **Generation** — `phi-4-mini`, retrieved context kullanılarak nihai cevabı üretir.

## Kullanılan Teknolojiler

| Teknoloji | Kullanım Amacı |
|---|---|
| **Python 3.11** | Uygulama geliştirme |
| **Azure AI Foundry Local** | Local model runtime ve OpenAI uyumlu API |
| **qwen3-embedding-0.6b** | Text embedding generation |
| **phi-4-mini** | Answer generation |
| **SQLite** | Chunk ve embedding storage |
| **FastAPI** | REST API katmanı |
| **pypdf** | PDF text extraction |

## Proje Yapısı

```text
LocalRAG/
├── data/
│   ├── pdfs/                  # Kaynak PDF dosyaları
│   └── rag.db                 # SQLite veritabanı
│
├── frontend/
│   └── index.html             # Basit web arayüzü
│
├── src/
│   ├── database.py            # Veritabanı şemasının oluşturulması
│   ├── insert_pdf.py          # PDF → chunk → embedding → database
│   ├── search.py              # Retrieval + generation (CLI)
│   ├── api.py                 # FastAPI uygulaması
│   └── test_retrieval.py      # Retrieval testleri
│
├── requirements.txt
└── README.md
```

## Kurulum

### 1. Python bağımlılıklarını yükleyin

```bash
pip install -r requirements.txt
```

### 2. Azure AI Foundry Local'i kurun

**Azure AI Foundry Local**'i kurun ve aşağıdaki modelleri indirin:

- `qwen3-embedding-0.6b`
- `phi-4-mini`

### 3. Foundry Local'i başlatın

Foundry Local'i başlatın ve local model server tarafından kullanılan portu öğrenin.

`src/search.py` ve `src/insert_pdf.py` içerisindeki `base_url` değerini kendi portunuza göre güncelleyin:

```python
client = OpenAI(
    base_url="http://127.0.0.1:PORT/v1",
    api_key="not-needed"
)
```

`PORT` yerine Foundry Local'in kullandığı portu yazın.

### 4. Veritabanını oluşturun

```bash
python src/database.py
```

### 5. PDF dosyalarını ekleyin

PDF dosyalarınızı aşağıdaki klasöre koyun:

```text
data/pdfs/
```

Ardından ingestion pipeline'ını çalıştırın:

```bash
python src/insert_pdf.py
```

Bu işlem:

```text
PDF
 ↓
Text Extraction
 ↓
Chunking
 ↓
Embedding Generation
 ↓
SQLite Storage
```

adımlarını gerçekleştirir.

## Kullanım

### CLI üzerinden sorgulama

```bash
python src/search.py
```

Program başladıktan sonra sorularınızı terminal üzerinden girebilirsiniz.

### REST API

FastAPI sunucusunu başlatın:

```bash
uvicorn src.api:app --reload
```

Ardından `/ask` endpoint'ine soru gönderebilirsiniz:

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the relationship between sleep and memory?"}'
```

### Frontend

Projede basit bir browser-based frontend de bulunmaktadır.

API çalışırken:

```text
frontend/index.html
```

dosyasını tarayıcıda açarak kullanıcı arayüzü üzerinden soru sorabilirsiniz.

Frontend, soruları local FastAPI endpoint'ine gönderir ve oluşturulan cevabı kullanıcıya gösterir.

## Knowledge Base

Mevcut knowledge base, **sleep, memory ve cognitive function** konularıyla ilgili üç İngilizce akademik makaleden oluşmaktadır.

| Dosya | Açıklama |
|---|---|
| `main.pdf` | Sleep ve memory consolidation üzerine ana kaynak makale |
| `rstb20190234.pdf` | Sleep-memory ilişkisi üzerine akademik yayın |
| `ssci-13-02-0152.pdf` | Sleep ve cognitive functions üzerine bilimsel makale |

Bu üç PDF, chunk'lara ayrılmış, her chunk için embedding oluşturulmuş ve sonuçlar `data/rag.db` içerisinde saklanmıştır.

Mevcut veri setinde yaklaşık **200 chunk** bulunmaktadır. Kesin chunk sayısı, `insert_pdf.py` çalıştırılırken kullanılan chunking parametrelerine bağlı olarak değişebilir.

## Teknik Problemler ve Çözümler

Geliştirme sürecinde retrieval kalitesini etkileyen çeşitli problemler tespit edilmiş ve çözülmüştür.

### 1. Kaynakça Metinlerinin Retrieval Sonuçlarına Karışması

PDF'lerden metin çıkarılırken makalelerin **References** bölümleri de normal içerikle aynı şekilde chunk'lara ayrılıyordu.

Bazı kaynakça chunk'ları, kullanıcı sorusuyla yüzeysel kelime benzerliği taşıdığı için yüksek cosine similarity skorlarına ulaşabiliyordu. Ancak bu chunk'lar gerçek içerik yerine bibliographic information içerdiğinden LLM için anlamlı bir context oluşturmuyordu.

Örneğin:

```text
Sakai T, Tamura T... Proc Natl Acad Sci...
```

gibi bir kaynakça satırı retrieval sonucunda üst sıralara çıkabiliyordu.

#### Çözüm

Bu problemi azaltmak için `looks_like_reference()` isimli filtering fonksiyonu geliştirildi.

Fonksiyon, chunk içerisinde aşağıdaki gibi reference göstergelerinin bulunma yoğunluğunu kontrol eder:

- `doi:`
- `et al.`
- `journal`
- `vol.`
- `pp.`

Reference-like olarak belirlenen chunk'lar retrieval aşamasında elenir ve LLM'e gönderilen context'e dahil edilmez.

Bu yaklaşım, bibliographic information içeren chunk'ların gerçek document content ile rekabet etmesini engellemek amacıyla uygulanmıştır.

### 2. Türkçe Sorular ve İngilizce Dokümanlar

Mevcut knowledge base tamamen İngilizce dokümanlardan oluşmaktadır.

Testler sırasında Türkçe soruların bazı durumlarda daha düşük semantic similarity skorları ürettiği ve bunun sonucunda yeterince ilgili chunk bulunamadığı gözlemlenmiştir.

Bu nedenle mevcut sürüm **İngilizce sorular + İngilizce dokümanlar** üzerine tasarlanmıştır.

Multilingual retrieval şu an projenin kapsamı dışındadır.

## Evaluation

Retrieval bileşeni aşağıdaki komut ile test edilebilir:

```bash
python src/test_retrieval.py
```

Mevcut test yaklaşımı temel olarak verilen sorular için semantic olarak ilgili chunk'ların retrieval edilip edilmediğini kontrol etmeye yöneliktir.

İlerleyen aşamada sistem aşağıdaki metriklerle daha kapsamlı şekilde değerlendirilebilir:

- **Top-1 Retrieval Accuracy**
- **Top-3 Retrieval Accuracy**
- Similarity score distribution
- Answer accuracy
- Out-of-domain / unanswerable question handling
- Response latency
- Farklı chunk size ve Top-K değerlerinin karşılaştırılması

## Limitations

Mevcut implementasyonun bazı sınırlamaları bulunmaktadır:

- Knowledge base şu anda küçük bir doküman koleksiyonundan oluşmaktadır.
- Embedding'ler SQLite içerisinde saklanmakta ve similarity search Python tarafında gerçekleştirilmektedir. Bu yaklaşım küçük veri setleri için yeterliyken çok büyük veri setlerinde verimli olmayacaktır.
- Mevcut doküman koleksiyonu İngilizce olduğu için multilingual retrieval uygulanmamıştır.
- LLM'in retrieved context'e bağlı kalması büyük ölçüde prompt instructions'a dayanmaktadır.
- Reference detection heuristic-based bir yaklaşımdır ve her türlü reference chunk'ını yakalamayı garanti etmez.
- Özel bir vector database veya dedicated vector index kullanılmamaktadır.

## Future Improvements

Projeye ileride aşağıdaki geliştirmeler eklenebilir:

- Daha güçlü multilingual retrieval desteği
- Daha gelişmiş chunking ve overlap stratejileri
- Chunk'lara document name ve page number gibi metadata eklenmesi
- Cevaplarda source citations gösterilmesi
- Similarity threshold eklenerek alakasız context'in reddedilmesi
- Farklı Top-K değerlerinin karşılaştırılması
- Farklı embedding modellerinin değerlendirilmesi
- Automated RAG evaluation metriklerinin eklenmesi
- Büyük veri setleri için vector search extension veya vector database kullanılması
- Frontend'in geliştirilmesi ve conversation history eklenmesi
- Farklı doküman formatları için destek eklenmesi

## Staj Bağlamı

Bu proje, **Microsoft AI Yazılım Programı** kapsamında gerçekleştirilen bir aylık öğrenme sürecinin parçası olarak geliştirilmiştir.

Projenin temel amacı, RAG mimarisini bir black-box çözüm olarak kullanmak yerine temel bileşenlerini uygulamalı olarak öğrenmek ve uçtan uca çalışan bir **local document Q&A system** geliştirmekti.

Proje kapsamında aşağıdaki konularda çalışılmıştır:

- Document processing ve chunking
- Text embeddings
- Semantic similarity search
- SQLite data storage
- Context construction
- Prompt design
- Local LLM inference
- Azure AI Foundry Local
- FastAPI
- Web-based interface

Bu proje aynı zamanda ilk **local LLM** deneyimim ve Azure AI Foundry Local ile ilk uygulamalı çalışmam oldu.

Proje sürecinde edinilen temel deneyimlerden biri, bir RAG sisteminin cevap kalitesinin yalnızca kullanılan LLM'e bağlı olmadığıdır. **Retrieval kalitesi, preprocessing, chunking ve modele sağlanan context**, nihai generation kalitesini doğrudan etkileyebilmektedir.

Özellikle reference filtering üzerinde yapılan çalışma, retrieval pipeline'ındaki küçük bir preprocessing probleminin bile LLM'e sağlanan context'i ve dolayısıyla oluşturulan cevabı etkileyebileceğini göstermiştir.

## References

- [Azure AI Foundry Local Documentation](https://learn.microsoft.com/azure/ai-foundry/foundry-local/)
- [Microsoft Learn — Build a RAG Application with Foundry Local](https://learn.microsoft.com/en-us/azure/foundry-local/tutorials/tutorial-build-rag-app)
- [Microsoft Learn — Prompt Engineering Techniques](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/prompt-engineering)
- [SQLite Documentation](https://sqlite.org/index.html)
- [pypdf Documentation](https://pypdf.readthedocs.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)


