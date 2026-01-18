# pip install python-dotenv if needed
from dotenv import load_dotenv
from typing import List, Dict
from backend.routes.chunkText import get_chunks
import json
import os
import requests
load_dotenv()

GEMINI_API_URL = os.environ.get("GEMINI_API_URL")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def generate_flashcards(text: str) -> List[Dict[str, str]]:
    prompt = (
        "Generate 2 flashcards in JSON format from the following transcript chunks."
        "Each flashcard should have a 'question' and an 'answer'. "
        "Return the result as a JSON array of objects.\n\n"
    )
    headers = {"Content-Type": "application/json"}
    data = {
    "contents": [{"parts": [{"text": prompt}]}]
    }   
    response = requests.post(
        f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
        headers=headers,
        json=data
    )

def generate_flashcards_from_docs():
    docs = get_chunks()
    flashcards = []
    for doc in docs:
        flashcards.extend(generate_flashcards(doc.page_content))
    return flashcards

def flashcards_to_json(flashcards: List[Dict[str, str]]) -> str:
    return json.dumps(flashcards, indent=2)

if __name__ == "__main__":
    flashcards = generate_flashcards_from_docs()
    print(flashcards_to_json(flashcards))