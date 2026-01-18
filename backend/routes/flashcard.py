# backend/routes/flashcard.py

from dotenv import load_dotenv
from typing import List, Dict, Any
from .chunkText import get_chunks
import json
import os
import requests

load_dotenv()

GEMINI_API_URL = os.environ.get("GEMINI_API_URL")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


def _require_env() -> None:
    if not GEMINI_API_URL:
        raise RuntimeError("Missing GEMINI_API_URL in .env")
    if not GEMINI_API_KEY:
        raise RuntimeError("Missing GEMINI_API_KEY in .env")


def generate_flashcards(text: str, count: int = 2) -> List[Dict[str, str]]:
    _require_env()

    prompt = (
        f"Generate exactly {count} flashcards in JSON format from the transcript chunk below.\n"
        "Rules:\n"
        "- Use ONLY the chunk content, do not add outside knowledge\n"
        "- Each flashcard must have keys: question, answer\n"
        "- Return ONLY a JSON array (no markdown, no extra text)\n"
        "- Questions should be exam-style and answerable from the provided content\n"
        "- Answers should be concise and directly grounded in the transcript\n\n"
        f"TRANSCRIPT CHUNK:\n{text}\n"
    )

    headers = {"Content-Type": "application/json"}

    data: Dict[str, Any] = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    response = requests.post(
        f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
        headers=headers,
        json=data,
        timeout=60
    )

    response.raise_for_status()

    result = response.json()

    try:
        output_text = result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("=== Unexpected Gemini response shape ===")
        print(json.dumps(result, indent=2))
        print("=======================================")
        raise RuntimeError("Could not parse Gemini response") from e

    try:
        cards = json.loads(output_text)
        if not isinstance(cards, list):
            raise ValueError("Model did not return a JSON list.")
        # Basic validation: ensure question/answer exist
        cleaned: List[Dict[str, str]] = []
        for c in cards:
            if isinstance(c, dict) and "question" in c and "answer" in c:
                cleaned.append({"question": str(c["question"]), "answer": str(c["answer"])})
        return cleaned
    except Exception:
        print("=== RAW MODEL OUTPUT (not valid JSON) ===")
        print(output_text)
        print("========================================")
        raise


def generate_flashcards_from_docs(max_chunks: int = 12, cards_per_chunk: int = 2) -> List[Dict[str, str]]:
    docs = get_chunks()
    
    # Select representative chunks from across the lecture for better coverage
    if len(docs) <= max_chunks:
        selected_docs = docs
    else:
        # Select evenly distributed chunks across the lecture
        indices = [int(i * (len(docs) - 1) / (max_chunks - 1)) for i in range(max_chunks)]
        selected_docs = [docs[i] for i in indices]
    
    flashcards: List[Dict[str, str]] = []
    for i, doc in enumerate(selected_docs):
        chunk_text = doc.page_content
        cards = generate_flashcards(chunk_text, count=cards_per_chunk)
        flashcards.extend(cards)
        print(f"[OK] chunk {i+1}/{len(selected_docs)} -> {len(cards)} cards")

    return flashcards


def flashcards_to_json(flashcards: List[Dict[str, str]]) -> str:
    return json.dumps(flashcards, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    flashcards = generate_flashcards_from_docs()
    print(flashcards_to_json(flashcards))

# if __name__ == "__main__":

    # docs = get_chunks()
    # print("Num chunks:", len(docs))

    # first_chunk = docs[0].page_content
    # print("\n=== Testing FIRST chunk only ===\n")
    # one = generate_flashcards(first_chunk, count=2)
    # print(flashcards_to_json(one))