import os
import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_experimental.text_splitter import SemanticChunker
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

load_dotenv()

# Get the backend directory (parent of routes directory)
BACKEND_DIR = Path(__file__).parent.parent
DEFAULT_TRANSCRIPT_PATH = BACKEND_DIR / "data" / "transcripts" / "transcription_text.txt"
DEFAULT_SEGMENTS_PATH = BACKEND_DIR / "data" / "transcripts" / "transcription_segments.json"
LOG_PATH = "/Users/stephaniechen/nwhacks26/.cursor/debug.log"

# #region agent log
def _log(hypothesis_id, location, message, data):
    try:
        import time
        log_entry = {
            "sessionId": "debug-session",
            "runId": "run1",
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": int(time.time() * 1000)
        }
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except:
        pass
# #endregion


def get_chunks_from_segments(segments_path=None, chunk_size=15):
    """
    Load pre-chunked transcript segments from JSON and group them into larger chunks.
    
    Args:
        segments_path: Path to segments JSON file. If None, uses default.
        chunk_size: Number of segments to group together per chunk.
        
    Returns:
        List of LangChain Document objects.
    """
    # #region agent log
    _log("C", "chunkText.py:get_chunks_from_segments", "Fallback: loading pre-chunked segments", {"segments_path": str(segments_path) if segments_path else "default"})
    # #endregion
    
    if segments_path is None:
        segments_path = DEFAULT_SEGMENTS_PATH
    else:
        segments_path = Path(segments_path)
        if not segments_path.is_absolute():
            segments_path = BACKEND_DIR / segments_path
    
    if not segments_path.exists():
        raise FileNotFoundError(f"Segments file not found: {segments_path}")
    
    with open(segments_path, "r", encoding="utf-8") as f:
        segments = json.load(f)
    
    # #region agent log
    _log("C", "chunkText.py:get_chunks_from_segments", "Loaded segments from JSON", {"segment_count": len(segments)})
    # #endregion
    
    # Group segments into chunks
    docs = []
    for i in range(0, len(segments), chunk_size):
        chunk_segments = segments[i:i+chunk_size]
        chunk_text = " ".join(seg["text"] for seg in chunk_segments)
        start_time = chunk_segments[0]["start"]
        end_time = chunk_segments[-1]["end"]
        
        docs.append(Document(
            page_content=chunk_text,
            metadata={"start": start_time, "end": end_time, "segment_ids": [s["id"] for s in chunk_segments]}
        ))
    
    # #region agent log
    _log("C", "chunkText.py:get_chunks_from_segments", "Created chunks from segments", {"chunk_count": len(docs), "chunk_size": chunk_size})
    # #endregion
    
    return docs


def get_chunks(transcript_path=None):
    """
    Chunk a transcript file into semantic sections.
    Falls back to pre-chunked segments if semantic chunking fails due to quota limits.
    
    Args:
        transcript_path: Path to transcript text file. If None, uses default.
        
    Returns:
        List of LangChain Document objects containing chunked text.
    """
    # #region agent log
    _log("A", "chunkText.py:get_chunks", "Starting chunking", {"transcript_path": str(transcript_path) if transcript_path else "default"})
    # #endregion
    
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
    
    # #region agent log
    _log("A", "chunkText.py:get_chunks", "API key found, attempting semantic chunking", {})
    # #endregion
    
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001", 
        google_api_key=GEMINI_API_KEY
    )
    text_splitter = SemanticChunker(embeddings, breakpoint_threshold_type="percentile")
    
    if not transcript_path.exists():
        raise FileNotFoundError(f"Transcript file not found: {transcript_path}")
    
    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = f.read()
    
    # #region agent log
    _log("A", "chunkText.py:get_chunks", "Transcript loaded", {"transcript_length": len(transcript)})
    # #endregion
    
    try:
        # #region agent log
        _log("B", "chunkText.py:get_chunks", "Attempting semantic chunking", {})
        # #endregion
        
        docs = text_splitter.create_documents([transcript])
        
        # #region agent log
        _log("A", "chunkText.py:get_chunks", "Semantic chunking succeeded", {"chunk_count": len(docs)})
        # #endregion
        
        return docs
        
    except Exception as e:
        error_str = str(e)
        
        # #region agent log
        _log("B", "chunkText.py:get_chunks", "Semantic chunking failed", {"error_type": type(e).__name__, "error_message": error_str[:200]})
        # #endregion
        
        # Check if it's a quota/resource exhausted error
        is_quota_error = "RESOURCE_EXHAUSTED" in error_str or "429" in error_str or "quota" in error_str.lower()
        
        # #region agent log
        _log("C", "chunkText.py:get_chunks", "Error analysis", {"is_quota_error": is_quota_error})
        # #endregion
        
        if is_quota_error:
            # #region agent log
            _log("C", "chunkText.py:get_chunks", "Quota error detected, using fallback", {})
            # #endregion
            print("⚠️  Semantic chunking failed due to API quota limits. Falling back to pre-chunked segments.")
            return get_chunks_from_segments()
        else:
            # #region agent log
            _log("D", "chunkText.py:get_chunks", "Non-quota error, re-raising", {})
            # #endregion
            # Re-raise if it's not a quota error
            raise