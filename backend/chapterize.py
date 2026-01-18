import json
import os
import sys
import re
from typing import List, Dict, Tuple, Any
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def load_transcript_segments(file_path: str) -> List[Dict[str, Any]]:
    """
    Load transcript segments from a JSON file.
    
    Args:
        file_path: Path to the JSON file containing transcript segments
        
    Returns:
        List of transcript segment dictionaries
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def group_segments_for_processing(segments: List[Dict[str, Any]], window_size: int = 15, overlap: int = 5) -> List[List[Dict[str, Any]]]:
    """
    Group transcript segments into overlapping windows for processing.
    
    Args:
        segments: List of transcript segments
        window_size: Number of segments in each window
        overlap: Number of overlapping segments between windows
        
    Returns:
        List of segment groups (windows)
    """
    if len(segments) <= window_size:
        return [segments]
    
    groups = []
    start_idx = 0
    
    while start_idx < len(segments):
        end_idx = min(start_idx + window_size, len(segments))
        groups.append(segments[start_idx:end_idx])
        
        # Move start index forward with overlap
        if end_idx >= len(segments):
            break
        start_idx = end_idx - overlap
    
    return groups

def create_transcript_text(segments: List[Dict[str, Any]]) -> str:
    """
    Convert a list of segments into a single text string with timestamps.
    
    Args:
        segments: List of transcript segments
        
    Returns:
        Formatted transcript text with timestamps
    """
    transcript_parts = []
    for segment in segments:
        transcript_parts.append(f"[{segment['start']:.2f}-{segment['end']:.2f}] {segment['text']}")
    
    return "\n".join(transcript_parts)

def call_gemini_for_chapters(transcript_text: str, model_name: str = "gemini-2.5-flash") -> Dict[str, Any]:
    """
    Call Gemini API to identify chapters in the transcript.
    
    Args:
        transcript_text: Transcript text with timestamps
        model_name: Name of the Gemini model to use
        
    Returns:
        Dictionary containing chapter information
    """
    model = genai.GenerativeModel(model_name)
    
def call_gemini_for_chapters(transcript_text: str, max_chapters: int = 12, model_name: str = "gemini-2.5-flash") -> Dict[str, Any]:
    """
    Call Gemini API to identify chapters in the transcript.
    
    Args:
        transcript_text: Transcript text with timestamps
        max_chapters: Maximum number of chapters to generate
        model_name: Name of the Gemini model to use
        
    Returns:
        Dictionary containing chapter information
    """
    model = genai.GenerativeModel(model_name)
    
    prompt = f"""
    Analyze the following video transcript and identify logical chapter breaks.
    For each chapter, provide a short, descriptive name and the timestamp where it begins and ends.
    
    The transcript format is [start_time-end_time] text.
    
    Please respond ONLY with a valid JSON object in the following format:
    {{
        "chapters": [
            {{
                "chapter_name": "Short descriptive name",
                "start_time": timestamp_in_seconds,
                "end_time": timestamp_in_seconds
            }},
            ...
        ]
    }}
    
    Guidelines:
    1. Chapters should represent distinct topics or sections of the video
    2. Chapter names should be concise (2-5 words) but descriptive
    3. Start and end times should align with the timestamps in the transcript
    4. Create a reasonable number of chapters based on natural topic changes (typically 5-10 for this length of content)
    5. DO NOT exceed {max_chapters} chapters maximum - this is a hard limit, not a target
    6. Make sure chapters flow logically and cover the ENTIRE content from beginning to end
    7. The first chapter must start at the beginning of the transcript
    8. The last chapter must end at the end of the transcript
    9. Prioritize content coherence over hitting a specific number of chapters
    
    Transcript:
    {transcript_text}
    """
    
    try:
        print(f"Sending transcript to Gemini (length: {len(transcript_text)} chars)...")
        print(f"API Key configured: {bool(os.getenv('GEMINI_API_KEY'))}")
        
        response = model.generate_content(prompt)
        # Extract JSON from the response
        response_text = response.text
        print(f"Full Gemini response:\n{response_text}")
        
        # Check if response contains the expected structure
        if "chapters" not in response_text:
            print("Warning: Response doesn't contain 'chapters' keyword")
        
        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            print(f"Extracted JSON string: {json_str}")
            result = json.loads(json_str)
            print(f"Successfully parsed JSON: {result}")
            return result
        else:
            # If no JSON found, try to parse the entire response
            print("No JSON pattern found, trying to parse entire response...")
            result = json.loads(response_text)
            print(f"Parsed entire response: {result}")
            return result
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Response text was: {response_text}")
        return {"chapters": []}
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        print(f"Exception type: {type(e).__name__}")
        return {"chapters": []}

def merge_chapter_results(all_chapters: List[Dict[str, Any]], segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merge chapter results from multiple API calls and align with segment boundaries.
    
    Args:
        all_chapters: List of chapter dictionaries from multiple API calls
        segments: Original transcript segments
        
    Returns:
        Merged and refined list of chapters
    """
    if not all_chapters:
        return []
    
    # Flatten all chapters
    flat_chapters = []
    for chapter_group in all_chapters:
        if "chapters" in chapter_group:
            flat_chapters.extend(chapter_group["chapters"])
    
    if not flat_chapters:
        return []
    
    # Sort chapters by start time
    flat_chapters.sort(key=lambda x: x.get("start_time", 0))
    
    # Remove duplicates and merge overlapping chapters
    merged_chapters = []
    for chapter in flat_chapters:
        if not chapter.get("chapter_name") or chapter.get("start_time") is None:
            continue
            
        # Check if this chapter overlaps with the last one added
        if merged_chapters:
            last_chapter = merged_chapters[-1]
            # If chapters are very close or overlapping, merge them
            if abs(chapter["start_time"] - last_chapter["start_time"]) < 10:
                # Keep the more descriptive name (longer)
                if len(chapter["chapter_name"]) > len(last_chapter["chapter_name"]):
                    last_chapter["chapter_name"] = chapter["chapter_name"]
                # Update end time if this chapter extends further
                if chapter.get("end_time", 0) > last_chapter.get("end_time", 0):
                    last_chapter["end_time"] = chapter["end_time"]
                continue
        
        # Align times with segment boundaries
        aligned_start = align_time_to_segment(chapter["start_time"], segments)
        aligned_end = align_time_to_segment(chapter.get("end_time", chapter["start_time"] + 60), segments)
        
        merged_chapters.append({
            "chapter_name": chapter["chapter_name"],
            "start_time": aligned_start,
            "end_time": aligned_end
        })
    
    # Ensure chapters cover the entire video
    if merged_chapters:
        # First chapter should start at the beginning
        merged_chapters[0]["start_time"] = segments[0]["start"]
        
        # Last chapter should end at the end
        merged_chapters[-1]["end_time"] = segments[-1]["end"]
        
        # Fix any gaps or overlaps
        for i in range(len(merged_chapters) - 1):
            current_end = merged_chapters[i]["end_time"]
            next_start = merged_chapters[i + 1]["start_time"]
            
            # If there's a small gap, bridge it
            if next_start - current_end > 5:
                merged_chapters[i]["end_time"] = next_start
            # If chapters overlap, adjust the boundary
            elif next_start < current_end:
                merged_chapters[i + 1]["start_time"] = current_end
    
    return merged_chapters

def align_time_to_segment(time: float, segments: List[Dict[str, Any]]) -> float:
    """
    Align a timestamp to the nearest segment boundary.
    
    Args:
        time: Timestamp to align
        segments: List of transcript segments
        
    Returns:
        Aligned timestamp
    """
    # Find the segment closest to the given time
    closest_segment = min(segments, key=lambda s: abs(s["start"] - time))
    return closest_segment["start"]

def ensure_full_coverage(chapters: List[Dict[str, Any]], segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ensure chapters cover the entire video from start to end with no gaps.
    
    Args:
        chapters: List of chapter dictionaries
        segments: Original transcript segments
        
    Returns:
        Adjusted list of chapters covering the entire video
    """
    if not chapters:
        return []
    
    # Get video start and end times
    video_start = segments[0]["start"]
    video_end = segments[-1]["end"]
    
    # Ensure first chapter starts at the beginning
    chapters[0]["start_time"] = video_start
    
    # Ensure last chapter ends at the end
    chapters[-1]["end_time"] = video_end
    
    # Sort chapters by start time
    chapters.sort(key=lambda x: x["start_time"])
    
    # Fix any gaps or overlaps
    for i in range(len(chapters) - 1):
        current_end = chapters[i]["end_time"]
        next_start = chapters[i + 1]["start_time"]
        
        # If there's a gap, extend the current chapter
        if next_start > current_end:
            chapters[i]["end_time"] = next_start
        # If chapters overlap, adjust the boundary
        elif next_start < current_end:
            chapters[i + 1]["start_time"] = current_end
    
    return chapters

def save_chapters_to_file(chapters: List[Dict[str, Any]], output_path: str) -> None:
    """
    Save chapters to a JSON file.
    
    Args:
        chapters: List of chapter dictionaries
        output_path: Path to save the chapters JSON file
    """
    output_data = {"chapters": chapters}
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"Chapters saved to {output_path}")
    print(f"Generated {len(chapters)} chapters:")
    for i, chapter in enumerate(chapters, 1):
        print(f"  {i}. {chapter['chapter_name']} ({chapter['start_time']:.2f}s - {chapter['end_time']:.2f}s)")

def main():
    """
    Main function to process transcript segments and generate chapters.
    """
    # Default input and output paths
    default_input = "data/transcripts/transcription_segments.json"
    default_output = "data/chapters.json"
    
    # Allow command line arguments for custom paths
    input_path = sys.argv[1] if len(sys.argv) > 1 else default_input
    output_path = sys.argv[2] if len(sys.argv) > 2 else default_output
    
    try:
        # Load transcript segments
        print(f"Loading transcript segments from {input_path}...")
        segments = load_transcript_segments(input_path)
        print(f"Loaded {len(segments)} transcript segments")
        
        # Create transcript text from all segments
        print("Creating transcript text from all segments...")
        transcript_text = create_transcript_text(segments)
        print(f"Created transcript text of length: {len(transcript_text)}")
        
        # Set maximum chapters (default: 12)
        max_chapters = 12
        
        # Process the entire transcript with Gemini API
        print(f"Processing entire transcript with Gemini API (max {max_chapters} chapters)...")
        chapters = call_gemini_for_chapters(transcript_text, max_chapters)
        print(f"Received chapters: {chapters}")
        
        # Extract chapters from the response
        final_chapters = []
        if chapters.get("chapters"):
            print(f"Found {len(chapters['chapters'])} chapters")
            final_chapters = chapters["chapters"]
            # Ensure chapters cover the entire video
            final_chapters = ensure_full_coverage(final_chapters, segments)
            # Align timestamps with segment boundaries
            for chapter in final_chapters:
                chapter["start_time"] = align_time_to_segment(chapter["start_time"], segments)
                chapter["end_time"] = align_time_to_segment(chapter["end_time"], segments)
        else:
            print("No chapters found in the response")
        
        print(f"Final chapters after processing: {final_chapters}")
        
        # Save chapters to file
        save_chapters_to_file(final_chapters, output_path)
        
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()