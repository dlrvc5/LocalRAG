from search import load_documents, get_top_chunks


documents = load_documents()

test_questions = [
    "What is the relationship between sleep and memory?",
    "What are the effects of sleep deprivation on memory?",
    "How does sleep affect memory consolidation?"
]


for question in test_questions:

    print("\n" + "=" * 60)
    print("QUESTION:")
    print(question)

    chunks = get_top_chunks(
        question,
        documents,
        top_k=3,
        similarity_threshold=0.40
    )

    print("\nTOP CHUNKS:")

    for i, (text, similarity) in enumerate(chunks, 1):

        print(
            f"\n{i}. Similarity: {similarity:.4f}"
        )

        print(text[:300])