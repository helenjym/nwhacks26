from flask import Flask, request, jsonify, render_template
import os
import uuid
import hashlib
import json
from werkzeug.utils import secure_filename

# Import our refactored modules
from video2transcript import transcribe_video, save_transcript
from chapterize import generate_chapters, save_chapters_to_file
from summarize import initialize_chat, generate_summary, send_chat_message

# Initialize Flask app
app = Flask(__name__, template_folder='templates')

# Configuration
UPLOAD_FOLDER = 'data/videos'
TRANSCRIPT_FOLDER = 'data/transcripts'
CHAPTERS_FOLDER = 'data/chapters'
CACHE_FOLDER = 'data/cache'
CACHE_INDEX_FILE = os.path.join(CACHE_FOLDER, 'cache_index.json')
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRANSCRIPT_FOLDER, exist_ok=True)
os.makedirs(CHAPTERS_FOLDER, exist_ok=True)
os.makedirs(CACHE_FOLDER, exist_ok=True)

# In-memory chat sessions storage
chat_sessions = {}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size


def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_cache_key(filename):
    """Generate MD5 hash from filename for cache directory name."""
    return hashlib.md5(filename.encode()).hexdigest()


def get_cache_index():
    """Load the cache index from file."""
    if os.path.exists(CACHE_INDEX_FILE):
        try:
            with open(CACHE_INDEX_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading cache index: {e}")
            return {}
    return {}


def update_cache_index(filename, cache_key):
    """Update the cache index with a new entry."""
    cache_index = get_cache_index()
    cache_index[filename] = cache_key
    try:
        with open(CACHE_INDEX_FILE, 'w') as f:
            json.dump(cache_index, f, indent=2)
    except Exception as e:
        print(f"Error updating cache index: {e}")


def cache_exists(filename):
    """Check if cached data exists for a given filename."""
    cache_key = get_cache_key(filename)
    cache_dir = os.path.join(CACHE_FOLDER, cache_key)
    
    # Check if cache directory exists and contains all required files
    required_files = [
        'transcript_segments.json',
        'transcript_text.txt',
        'chapters.json',
        'summary.txt'
    ]
    
    if not os.path.exists(cache_dir):
        return False
    
    for file in required_files:
        if not os.path.exists(os.path.join(cache_dir, file)):
            return False
    
    return True


def save_to_cache(filename, transcript_data, chapters, summary):
    """Save processed data to cache."""
    cache_key = get_cache_key(filename)
    cache_dir = os.path.join(CACHE_FOLDER, cache_key)
    os.makedirs(cache_dir, exist_ok=True)
    
    try:
        # Save transcript segments
        with open(os.path.join(cache_dir, 'transcript_segments.json'), 'w') as f:
            json.dump(transcript_data['segments'], f, indent=2)
        
        # Save transcript text
        with open(os.path.join(cache_dir, 'transcript_text.txt'), 'w', encoding='utf-8') as f:
            f.write(transcript_data['full_text'])
        
        # Save chapters
        with open(os.path.join(cache_dir, 'chapters.json'), 'w') as f:
            json.dump(chapters, f, indent=2)
        
        # Save summary
        with open(os.path.join(cache_dir, 'summary.txt'), 'w', encoding='utf-8') as f:
            f.write(summary)
        
        # Update cache index
        update_cache_index(filename, cache_key)
        
        print(f"Data cached successfully for {filename}")
        return True
    except Exception as e:
        print(f"Error saving to cache: {e}")
        return False


def load_from_cache(filename):
    """Load cached data for a given filename."""
    cache_key = get_cache_key(filename)
    cache_dir = os.path.join(CACHE_FOLDER, cache_key)
    
    try:
        # Load transcript segments
        with open(os.path.join(cache_dir, 'transcript_segments.json'), 'r') as f:
            segments = json.load(f)
        
        # Load transcript text
        with open(os.path.join(cache_dir, 'transcript_text.txt'), 'r', encoding='utf-8') as f:
            full_text = f.read()
        
        # Load chapters
        with open(os.path.join(cache_dir, 'chapters.json'), 'r') as f:
            chapters = json.load(f)
        
        # Load summary
        with open(os.path.join(cache_dir, 'summary.txt'), 'r', encoding='utf-8') as f:
            summary = f.read()
        
        transcript_data = {
            'segments': segments,
            'full_text': full_text
        }
        
        print(f"Data loaded from cache for {filename}")
        return transcript_data, chapters, summary
    except Exception as e:
        print(f"Error loading from cache: {e}")
        return None, None, None


@app.route('/', methods=['GET'])
def index():
    """Serve the frontend page."""
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_video():
    """
    Upload a video and process it through the full pipeline:
    - Check cache for existing data
    - If cached: load cached data and initialize new chat session
    - If not cached: transcribe with Whisper, generate chapters, generate summary
    - Initialize chat session
    
    Returns all results in a single response.
    """
    # Check if the post request has the file part
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    
    # If user does not select file, browser also submit an empty part without filename
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed types: mp4, mov, avi, mkv'}), 400
    
    try:
        # Generate unique video ID
        video_id = str(uuid.uuid4())
        original_filename = file.filename
        
        # Save the uploaded video
        filename = f"{video_id}.mp4"
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(video_path)
        
        print(f"Video saved to {video_path}")
        print(f"Original filename: {original_filename}")
        
        # Check if cached data exists for this filename
        if cache_exists(original_filename):
            print(f"Cache hit! Loading cached data for {original_filename}")
            
            # Load from cache
            transcript_data, chapters, summary = load_from_cache(original_filename)
            
            if transcript_data and chapters and summary:
                print("Successfully loaded from cache")
                
                # Initialize new chat session with cached transcript
                print("Initializing chat session with cached transcript...")
                chat_session = initialize_chat(transcript_data['full_text'])
                # Note: We don't call generate_summary() since we already have the cached summary
                
                # Store chat session in memory
                chat_sessions[video_id] = chat_session
                print("Chat session initialized!")
                
                # Return all results
                response_data = {
                    'video_id': video_id,
                    'filename': original_filename,
                    'transcript': {
                        'segments': transcript_data['segments'],
                        'full_text': transcript_data['full_text']
                    },
                    'chapters': chapters,
                    'summary': summary,
                    'chat_ready': True,
                    'cached': True
                }
                
                return jsonify(response_data), 200
            else:
                print("Failed to load from cache, processing normally")
        
        # Cache miss - process normally
        print(f"Cache miss! Processing video {original_filename}")
        
        # Step 1: Transcribe the video
        print("Starting transcription...")
        transcript_data = transcribe_video(video_path)
        print(f"Transcription result keys: {transcript_data.keys()}")
        print(f"Full text length: {len(transcript_data.get('full_text', ''))}")
        print(f"Full text preview (first 200 chars): {transcript_data.get('full_text', '')[:200]}")
        save_transcript(transcript_data, video_id, TRANSCRIPT_FOLDER)
        print("Transcription complete!")
        
        # Step 2: Generate chapters
        print("Generating chapters...")
        chapters = generate_chapters(transcript_data['segments'])
        chapters_path = os.path.join(CHAPTERS_FOLDER, f"{video_id}.json")
        save_chapters_to_file(chapters, chapters_path)
        print("Chapters generated!")
        
        # Step 3: Initialize chat session and generate summary
        print("Initializing chat session and generating summary...")
        chat_session = initialize_chat(transcript_data['full_text'])
        summary = generate_summary(chat_session)
        
        # Store chat session in memory
        chat_sessions[video_id] = chat_session
        print("Chat session initialized!")
        
        # Save to cache
        print(f"Saving processed data to cache for {original_filename}...")
        save_to_cache(original_filename, transcript_data, chapters, summary)
        
        # Return all results
        response_data = {
            'video_id': video_id,
            'filename': original_filename,
            'transcript': {
                'segments': transcript_data['segments'],
                'full_text': transcript_data['full_text']
            },
            'chapters': chapters,
            'summary': summary,
            'chat_ready': True,
            'cached': False
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"Error processing video: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Send a chat message to a specific video's chat session.
    
    Request body:
    {
        "video_id": "uuid",
        "message": "What was the main point?"
    }
    
    Returns the AI response.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        video_id = data.get('video_id')
        message = data.get('message')
        
        if not video_id:
            return jsonify({'error': 'video_id is required'}), 400
        
        if not message:
            return jsonify({'error': 'message is required'}), 400
        
        # Check if chat session exists
        if video_id not in chat_sessions:
            return jsonify({'error': 'Chat session not found. Please upload the video first.'}), 404
        
        # Get chat session and send message
        chat_session = chat_sessions[video_id]
        response = send_chat_message(chat_session, message)
        
        return jsonify({
            'video_id': video_id,
            'response': response
        }), 200
        
    except Exception as e:
        print(f"Error in chat: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'active_sessions': len(chat_sessions)
    }), 200


if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
