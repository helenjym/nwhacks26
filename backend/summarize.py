import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Setup and Configuration
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use a model appropriate for text (Gemini 1.5 Flash is fast and efficient)
model = genai.GenerativeModel('gemini-2.5-flash')

def get_file_content(filename):
    """Reads the content of the local text file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Could not find file '{filename}'")
        return None

def main():
    file_path = "data/transcripts/cs50transcription_text.txt"
    context_text = get_file_content(file_path)

    if not context_text:
        return

    chat = model.start_chat(history=[])

    initial_prompt = f"""
    I am going to provide you with a text file of a lecture for context. 
    First, please summarize this lecture for me. Please keep it short and simple while still capturing a big picture.
    Then, use this text as the source of truth for our conversation.
    
    TEXT CONTENT:
    {context_text}
    """
    
    response = chat.send_message(initial_prompt)
    print(f"\n📝 **Summary:**\n{response.text}\n")
    print("-" * 50)

    while True:
        user_input = input("You: ")
            
        try:
            response = chat.send_message(user_input)
            print(f"Bot: {response.text}")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()