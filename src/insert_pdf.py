import json
import sqlite3
from pathlib import Path

from pypdf import PdfReader
from openai import OpenAI


client = OpenAI(
    base_url="http://127.0.0.1:55673/v1",
    api_key="not-needed"
)

connection = sqlite3.connect("data/rag.db")
cursor = connection.cursor()

# Eski kayıtları temizle
cursor.execute("DELETE FROM documents")


def split_into_chunks(text, chunk_size=150, overlap=30):
    words = text.split()

    chunks = []

    step = chunk_size - overlap

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])

        if chunk.strip():
            chunks.append(chunk)

    return chunks


pdf_folder = Path("data/pdfs")

pdf_files = list(pdf_folder.glob("*.pdf"))

print(f"{len(pdf_files)} PDF bulundu.")


for pdf_file in pdf_files:

    print("\n==============================")
    print(f"PDF: {pdf_file.name}")
    print("==============================")

    reader = PdfReader(pdf_file)

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text()

        if not text:
            continue

        chunks = split_into_chunks(text)

        for chunk in chunks:

            print(f"\nChunk: {chunk[:100]}...")

            response = client.embeddings.create(
                model="qwen3-embedding-0.6b",
                input=chunk
            )

            embedding = response.data[0].embedding

            cursor.execute(
                """
                INSERT INTO documents(text, embedding)
                VALUES (?, ?)
                """,
                (
                    chunk,
                    json.dumps(embedding)
                )
            )

connection.commit()

cursor.execute("SELECT COUNT(*) FROM documents")

count = cursor.fetchone()[0]

print("\n==============================")
print(f"Toplam {count} chunk veritabanına kaydedildi.")
print("==============================")


connection.close()