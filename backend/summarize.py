import os
import google.generativeai as genai
from dotenv import load_dotenv

# Setup and Configuration
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use a model appropriate for text (Gemini 1.5 Flash is fast and efficient)
_model = None

def get_model():
    """Get or initialize the Gemini model (cached)."""
    global _model
    if _model is None:
        _model = genai.GenerativeModel('gemini-2.5-flash')
    return _model

def initialize_chat(transcript_text: str):
    """
    Initialize a chat session with transcript context.
    
    Args:
        transcript_text: Full transcript text to use as context
        
    Returns:
        ChatSession object
    """
    print(f"[DEBUG] initialize_chat called with transcript_text length: {len(transcript_text) if transcript_text else 0}")
    print(f"[DEBUG] transcript_text preview (first 200 chars): {transcript_text[:200] if transcript_text else 'EMPTY OR NONE'}")
    
    model = get_model()
    chat = model.start_chat(history=[])
    
    initial_prompt = f"""
    I am going to provide you with a text file of a lecture for context. 
    First, please summarize this lecture for me. Please keep it short and simple while still capturing a big picture.
    Then, use this text as the source of truth for our conversation.
    
    TEXT CONTENT:
    {transcript_text}
    """
    
    # Send the initial prompt to store the transcript in chat history
    print(f"[DEBUG] Sending initial prompt to chat...")
    chat.send_message(initial_prompt)
    print(f"[DEBUG] Chat history length after sending prompt: {len(chat.history)}")
    
    return chat

def generate_summary(chat_session) -> str:
    """
    Generate a summary using the initialized chat session.
    
    Args:
        chat_session: ChatSession object with transcript context
        
    Returns:
        Summary text
    """
    print(f"[DEBUG] generate_summary called")
    print(f"[DEBUG] Chat history length: {len(chat_session.history)}")
    
    # The summary was already generated in initialize_chat()
    # In Gemini chat history: history[0] = user message, history[1] = model response
    if len(chat_session.history) >= 2:
        print(f"[DEBUG] Returning summary from history[1] (model response)")
        summary = chat_session.history[1].parts[0].text
        print(f"[DEBUG] Summary length: {len(summary)}")
        print(f"[DEBUG] Summary preview (first 200 chars): {summary[:200]}")
        return summary
    else:
        print(f"[DEBUG] ERROR: Chat history doesn't have enough messages!")
        print(f"[DEBUG] History length: {len(chat_session.history)}")
        return "Error: No summary available"

def send_chat_message(chat_session, message: str) -> str:
    """
    Send a message to the chat session and get a response.
    
    Args:
        chat_session: ChatSession object with transcript context
        message: User's message
        
    Returns:
        AI response text
    """
    try:
        response = chat_session.send_message(message)
        return response.text
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"Error: {str(e)}"

def get_file_content(filename):
    """Reads the content of the local text file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Could not find file '{filename}'")
        return None

def main():
    import sys
    
    # Default transcript file path
    default_file_path = "data/transcripts/cs50transcription_text.txt"
    
    # Allow command line argument for custom file path
    file_path = sys.argv[1] if len(sys.argv) > 1 else default_file_path
    
    context_text = get_file_content(file_path)

    if not context_text:
        return

    chat = initialize_chat(context_text)
    
    response = generate_summary(chat)
    print(f"\n📝 **Summary:**\n{response}\n")
    print("-" * 50)

    while True:
        user_input = input("You: ")
            
        response = send_chat_message(chat, user_input)
        print(f"Bot: {response}")

if __name__ == "__main__":
    main()