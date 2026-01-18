# backend/routes/flashcard.py

from dotenv import load_dotenv
from typing import List, Dict, Any
import json
import os
import requests
import time

# Handle import for both module and standalone script usage
try:
    from .chunkText import get_chunks
except ImportError:
    # Fallback for when running as standalone script
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from routes.chunkText import get_chunks

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

    # Retry logic for rate limiting (429 errors)
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                headers=headers,
                json=data,
                timeout=60
            )
            
            # If we get a 429, wait and retry
            if response.status_code == 429:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"⚠️  Rate limit hit (429). Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                    time.sleep(wait_time)
                    continue
                else:
                    response.raise_for_status()
            else:
                response.raise_for_status()
                break
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429 and attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                print(f"⚠️  Rate limit hit (429). Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                continue
            raise

    result = response.json()

    try:
        output_text = result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("=== Unexpected Gemini response shape ===")
        print(json.dumps(result, indent=2))
        print("=======================================")
        raise RuntimeError("Could not parse Gemini response") from e

    # Strip markdown code blocks if present (e.g., ```json ... ```)
    output_text = output_text.strip()
    if output_text.startswith("```"):
        # Remove opening ```json or ```
        lines = output_text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        # Remove closing ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        output_text = "\n".join(lines)

    try:
        cards = json.loads(output_text)
        if not isinstance(cards, list):
            raise ValueError("Model did not return a JSON list.")
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


def generate_flashcards_from_docs(max_chunks: int = 5, cards_per_chunk: int = 2, delay_between_chunks: float = 1.0) -> List[Dict[str, str]]:
    """
    Generate flashcards from document chunks.
    
    Args:
        max_chunks: Maximum number of chunks to process (default: 5 to avoid rate limits)
        cards_per_chunk: Number of flashcards per chunk
        delay_between_chunks: Delay in seconds between processing chunks (default: 1.0)
    """
    docs = get_chunks()
    
    if len(docs) <= max_chunks:
        selected_docs = docs
    else:
        indices = [int(i * (len(docs) - 1) / (max_chunks - 1)) for i in range(max_chunks)]
        selected_docs = [docs[i] for i in indices]
    
    flashcards: List[Dict[str, str]] = []
    for i, doc in enumerate(selected_docs):
        chunk_text = doc.page_content
        cards = generate_flashcards(chunk_text, count=cards_per_chunk)
        flashcards.extend(cards)
        print(f"[OK] chunk {i+1}/{len(selected_docs)} -> {len(cards)} cards")
        
        # Add delay between chunks to avoid rate limiting (except for last chunk)
        if i < len(selected_docs) - 1:
            time.sleep(delay_between_chunks)

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