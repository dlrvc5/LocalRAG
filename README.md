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

## Kullanılan Dokümanlar

Sistem, uyku ve hafıza ilişkisi üzerine üç adet İngilizce akademik makale ile beslenmiştir:

| Dosya | Açıklama |
|---|---|
| `main.pdf` | Uyku ve hafıza konsolidasyonu üzerine ana kaynak makale |
| `rstb20190234.pdf` | Royal Society Philosophical Transactions'tan uyku-hafıza ilişkisine dair akademik yayın |
| `ssci-13-02-0152.pdf` | Uyku ve bilişsel fonksiyonlar üzerine bilimsel makale |

Bu üç PDF, chunk'lara ayrılıp embedding'e dönüştürülerek `data/rag.db` veritabanına kaydedilmiştir. Toplamda yaklaşık **~200 chunk** oluşmuştur (kesin sayı, `insert_pdf.py` her çalıştırıldığında chunking parametrelerine bağlı olarak değişebilir).

## Karşılaşılan Sorunlar ve Çözümler

Geliştirme sürecinde karşılaşılan başlıca teknik problemler ve bunlara getirilen çözümler:

**1. Kaynakça metinlerinin retrieval'a karışması**

PDF'lerden metin çıkarımı yapılırken, makalelerin kaynakça (references) bölümleri de diğer metinlerle aynı şekilde chunk'lara ayrılıyordu. Bu kaynakça chunk'ları (örn. `"Sakai T, Tamura T... Proc Natl Acad Sci..."` gibi) bazen soruyla yüzeysel bir kelime benzerliği taşıdığı için cosine similarity skorunda yüksek puan alıyor, ancak kullanıcıya anlamlı bir bilgi sunmuyordu.

*Çözüm:* `looks_like_reference()` adında bir fonksiyon yazıldı. Bu fonksiyon bir metin parçasının içinde `doi:`, `et al.`, `journal`, `vol.`, `pp.` gibi kaynakça belirteçlerinin yoğunluğuna bakarak o parçanın kaynakça olup olmadığını tahmin ediyor. Kaynakça olarak işaretlenen chunk'lar, retrieval aşamasında (`get_top_chunks()` içinde) tamamen elenip modele hiç gönderilmiyor.

**2. Türkçe soru — İngilizce doküman uyumsuzluğu**

Kullanılan embedding modeli (`qwen3-embedding-0.6b`) ve tüm kaynak PDF'ler İngilizce olduğu için, soru Türkçe sorulduğunda semantic similarity düşük çıkıyor, bazen hiç chunk seçilemiyor ya da alakasız chunk'lar dönüyordu. Bu nedenle sistemin şu anki hâliyle sorular İngilizce sorulmalıdır; çok dilli kullanım kapsam dışında bırakılmıştır.



## Staj Bağlamı

Bu projeyi, Microsoft AI Yazılım Programı kapsamında bir aylık bir öğrenme sürecinde geliştirdim. Amacım, RAG (Retrieval-Augmented Generation) mimarisinin temel bileşenlerini — chunking, embedding, semantic retrieval, context management ve generation — sıfırdan uygulayarak derinlemesine öğrenmekti.

Bu proje benim ilk yerel (local) LLM deneyimimdi; Azure AI Foundry Local'i de bu süreçte ilk kez kullandım. Süreç boyunca yalnızca bir pipeline kurmakla kalmadım, aynı zamanda retrieval kalitesinin generation kalitesi üzerindeki etkisini, kaynakça/referans metinlerinin retrieval sonuçlarını nasıl bozabileceğini ve context yönetiminin neden kritik olduğunu pratikte gözlemleme fırsatı buldum.
