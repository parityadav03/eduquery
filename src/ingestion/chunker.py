from langchain_text_splitters import RecursiveCharacterTextSplitter
def chunk_pages(pages: list[dict]) -> list[dict]:
    """
    Splits pages into smaller overlapping chunks for better retrieval.
    Returns list of {text, metadata} dicts.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=64,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    all_chunks = []

    for page in pages:
        splits = splitter.split_text(page["text"])
        for i, chunk_text in enumerate(splits):
            all_chunks.append({
                "text": chunk_text.strip(),
                "metadata": {
                    **page["metadata"],
                    "chunk_index": i
                }
            })

    print(f"Created {len(all_chunks)} chunks from {len(pages)} pages")
    return all_chunks