import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_experimental.text_splitter import SemanticChunker
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

# Get the backend directory (parent of routes directory)
BACKEND_DIR = Path(__file__).parent.parent
DEFAULT_TRANSCRIPT_PATH = BACKEND_DIR / "data" / "transcripts" / "transcription_text.txt"


def get_chunks(transcript_path=None):
    """
    Chunk a transcript file into semantic sections.
    
    Args:
        transcript_path: Path to transcript text file. If None, uses default.
        
    Returns:
        List of LangChain Document objects containing chunked text.
    """
    if transcript_path is None:
        transcript_path = DEFAULT_TRANSCRIPT_PATH
    else:
        # Convert string path to Path object if needed
        transcript_path = Path(transcript_path)
        if not transcript_path.is_absolute():
            transcript_path = BACKEND_DIR / transcript_path
    
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise RuntimeError("Missing GEMINI_API_KEY in .env")
    
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001", 
        google_api_key=GEMINI_API_KEY
    )
    text_splitter = SemanticChunker(embeddings, breakpoint_threshold_type="percentile")
    
    if not transcript_path.exists():
        raise FileNotFoundError(f"Transcript file not found: {transcript_path}")
    
    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = f.read()
    
    docs = text_splitter.create_documents([transcript])
    return docs