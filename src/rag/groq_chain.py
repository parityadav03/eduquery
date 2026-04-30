from groq import Groq
from src.rag.retriever import get_relevant_docs
from src.rag.prompt import ACADEMIC_PROMPT
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def format_context(docs) -> str:
    parts = []
    for doc in docs:
        parts.append(
            f"[Source: {doc.metadata['source_file']}, Page {doc.metadata['page_num']}]\n{doc.page_content}"
        )
    return "\n\n".join(parts)

def ask(question: str, k: int = 5) -> dict:
    docs = get_relevant_docs(question, k=k)
    context = format_context(docs)

    prompt_text = ACADEMIC_PROMPT.format(
        context=context,
        question=question
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt_text}],
        temperature=0.3,
        max_tokens=1024
    )

    answer = response.choices[0].message.content.strip()

    sources = list(set([
        f"{d.metadata['source_file']} (p.{d.metadata['page_num']})"
        for d in docs
    ]))

    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }