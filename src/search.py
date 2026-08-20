import sqlite3
import json
import numpy as np


from openai import OpenAI


client = OpenAI(
    base_url="http://127.0.0.1:55673/v1",
    api_key="not-needed"
)


DB_PATH = "data/rag.db"
DEBUG = False


def create_embedding(text):

    response = client.embeddings.create(
        model="qwen3-embedding-0.6b",
        input=text
    )

    return np.array(
            response.data[0].embedding,
            dtype=np.float32
        )

def cosine_similarity(vector1, vector2):

    denominator = (
        np.linalg.norm(vector1) *
        np.linalg.norm(vector2)
    )

    if denominator == 0:
        return 0.0

    return float(
        np.dot(vector1, vector2) / denominator
    )


def load_documents():

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT text, embedding FROM documents"
    )

    rows = cursor.fetchall()

    connection.close()

    documents = []

    for text, embedding_json in rows:

        embedding = np.array(
            json.loads(embedding_json),
            dtype=np.float32
        )

        documents.append(
            (text, embedding)
        )

    return documents


def looks_like_reference(text):

    lower_text =text.lower()

    reference_signals = [
        "doi:",
        "et al.",
        "journal",
        "vol.",
        "pp.",
        "proc.",
        "nature",
        "science",
        "plos",
    ]

    signal_count = sum(
        signal in lower_text
        for signal in reference_signals
    )

    if "doi:" in lower_text and signal_count >= 2:
        return True

    if lower_text.count(" et al.") >= 2:
        return True

    
    return signal_count >= 4


def get_top_chunks(
    question,
    documents,
    top_k=4,
    similarity_threshold=0.40
):

    question_embedding = create_embedding(question)

    similarities = []

    for text, embedding in documents:

        if looks_like_reference(text):
            continue

        similarity = cosine_similarity(
            question_embedding,
            embedding
        )

        if similarity < similarity_threshold:
            continue


        similarities.append(
            (
                text,
                similarity,
            )
        )

    similarities.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return similarities[:top_k]

def create_context(chunks,max_chars=6000):

    if not chunks:
        return ""

    context_parts = []
    current_length = 0

    for i, (text, similarity) in enumerate(chunks, 1):

        chunk_text = (
            f"[Chunk {i} | Similarity: {similarity:.4f}]\n"
            f"{text}"
        )

        if current_length + len(chunk_text) > max_chars:
            break

        context_parts.append(chunk_text)
        current_length += len(chunk_text)

    return "\n\n".join(context_parts)


def generate_answer(question, context):

    prompt = f"""
Sen bir soru-cevap asistanısın.

Görevin, yalnızca aşağıdaki context içinde bulunan bilgilere
dayanarak kullanıcının sorusunu cevaplamaktır.

Kurallar:
- Sadece context'teki bilgileri kullan.
- Kendi genel bilgini veya dışarıdan herhangi bir bilgiyi ekleme.
- Context'te olmayan bir bilgiyi tahmin etme veya uydurma.
- Context soruyu cevaplamak için yeterli değilse:
  "Bu konuda yeterli bilgim bulunmadı." de.
- Cevabı doğrudan soruyla ilgili ver.
- Gereksiz ayrıntıya girme.
- Açık ve anlaşılır bir dil kullan.

Context:
{context}

Soru:
{question}

Cevap:
"""

    response = client.chat.completions.create(
        model="phi-4-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


def main():

    print("=" * 50)
    print("LOCAL RAG SEARCH")
    print("=" * 50)

    documents = load_documents()

    print(f"\nVeritabanındaki chunk sayısı: {len(documents)}")


    while True:

        question = input("\nSorunuzu yazın: ")

        if question.lower() in [
            "çıkış",
            "cikis",
            "exit",
            "quit"
        ]:
            print("Program kapatılıyor...")
            break

        if not question.strip():
            print("Lütfen bir soru girin.")
            continue

        
        chunks = get_top_chunks(
            question,
            documents,
            top_k=4,
            similarity_threshold=0.40
        )

        if DEBUG:

            print("\n" + "=" * 50)
            print("RETRIEVED CHUNKS")
            print("=" * 50)

            if not chunks:

                print("Uygun chunk bulunamadı.")

                continue

            for i, (text, similarity) in enumerate(chunks, 1):

                preview = text.replace("\n", " ")

                if len(preview) > 250:
                    preview = preview[:250] + "..."

                print(
                    f"\n--- Chunk {i} "
                    f"| Similarity: {similarity:.4f} ---"
                )

                print(preview)

       
        context = create_context(chunks)

        

        answer = generate_answer(
            question,
            context
        )

        print("\n" + "=" * 50)
        print("CEVAP")
        print("=" * 50)

        print(answer)

        print("\n" + "=" * 50)
        print("KAYNAKLAR")
        print("=" * 50)

        for i, (text, similarity) in enumerate(chunks, 1):
            print(
                f"[Chunk {i}] Similarity: {similarity:.4f}"
            )


if __name__ == "__main__":
    main()