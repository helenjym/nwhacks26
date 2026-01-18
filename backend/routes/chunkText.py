import os
from dotenv import load_dotenv
from langchain_experimental.text_splitter import SemanticChunker
from langchain_google_genai import GoogleGenerativeAIEmbeddings
load_dotenv()

GEMINI_API_URL = os.environ.get("GEMINI_API_URL")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


def get_chunks(transcript_path="backend/data/transcripts/transcription_text.txt"):
    load_dotenv()
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)
    text_splitter = SemanticChunker(embeddings, breakpoint_threshold_type="percentile")
    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = f.read()
    docs = text_splitter.create_documents([transcript])
    return docs