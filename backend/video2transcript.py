import whisper
import json


model = whisper.load_model("base")
filename = "Theunhingedworldoftech.mp4"
audio_file = f"data/videos/{filename}"

print("Starting transcription...")

result = model.transcribe(audio_file, verbose=False)

simplified_segments = []
for segment in result["segments"]:
    simplified_segments.append({
        "id": segment["id"],
        "start": round(segment["start"], 2),
        "end": round(segment["end"], 2),
        "text": segment["text"].strip()
    })

json_filename = "data/transcripts/transcription_segments.json"
with open(json_filename, "w", encoding="utf-8") as f:
    json.dump(simplified_segments, f, indent=4, ensure_ascii=False)

txt_filename = "data/transcripts/transcription_text.txt"
with open(txt_filename, "w", encoding="utf-8") as f:
    f.write(result["text"])