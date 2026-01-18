import whisper
import json
import os
from typing import Dict, Any

# Global model cache
_model = None

def get_model():
    """Get or initialize the Whisper model (cached)."""
    global _model
    if _model is None:
        _model = whisper.load_model("base")
    return _model

def transcribe_video(video_path: str, output_dir: str = "data/transcripts") -> Dict[str, Any]:
    """
    Transcribe a video file using Whisper.
    
    Args:
        video_path: Path to the video file
        output_dir: Directory to save transcript files
        
    Returns:
        Dictionary containing:
        - segments: List of transcript segments with timestamps
        - full_text: Complete transcript text
    """
    model = get_model()
    
    print("Starting transcription...")
    
    result = model.transcribe(video_path, verbose=False)
    
    # Create simplified segments
    simplified_segments = []
    for segment in result["segments"]:
        simplified_segments.append({
            "id": segment["id"],
            "start": round(segment["start"], 2),
            "end": round(segment["end"], 2),
            "text": segment["text"].strip()
        })
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    return {
        "segments": simplified_segments,
        "full_text": result["text"]
    }

def save_transcript(transcript_data: Dict[str, Any], video_id: str, output_dir: str = "data/transcripts") -> None:
    """
    Save transcript data to files.
    
    Args:
        transcript_data: Dictionary containing segments and full_text
        video_id: Unique identifier for the video
        output_dir: Directory to save transcript files
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Save segments as JSON
    json_filename = os.path.join(output_dir, f"{video_id}_segments.json")
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(transcript_data["segments"], f, indent=4, ensure_ascii=False)
    
    # Save full text as TXT
    txt_filename = os.path.join(output_dir, f"{video_id}_text.txt")
    with open(txt_filename, "w", encoding="utf-8") as f:
        f.write(transcript_data["full_text"])

# Keep main function for standalone script usage
def main():
    import sys
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "Theunhingedworldoftech.mp4"
    
    audio_file = f"data/videos/{filename}"
    
    transcript_data = transcribe_video(audio_file)
    save_transcript(transcript_data, "transcription")
    
    print("Transcription complete!")

if __name__ == "__main__":
    main()