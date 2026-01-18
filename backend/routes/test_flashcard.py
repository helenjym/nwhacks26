import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from routes.chunkText import get_chunks
from routes.flashcard import generate_flashcards, generate_flashcards_from_docs, flashcards_to_json
from dotenv import load_dotenv

load_dotenv()


def test_chunking():
    """Test that chunks are generated correctly."""
    print("\n" + "="*60)
    print("TEST 1: Testing Chunking")
    print("="*60)
    
    try:
        docs = get_chunks()
        print(f"✓ Successfully generated {len(docs)} chunks")
        
        if len(docs) > 0:
            print(f"\nFirst chunk preview (first 200 chars):")
            print(docs[0].page_content[:200] + "...")
            print(f"\nFirst chunk metadata: {docs[0].metadata}")
        
        return docs
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_single_flashcard():
    """Test generating flashcards from a single chunk."""
    print("\n" + "="*60)
    print("TEST 2: Testing Single Chunk Flashcard Generation")
    print("="*60)
    
    try:
        docs = get_chunks()
        if len(docs) == 0:
            print("✗ No chunks available to test")
            return None
        
        # Use first chunk
        first_chunk = docs[0].page_content
        print(f"Using chunk with {len(first_chunk)} characters")
        print(f"Chunk preview: {first_chunk[:150]}...")
        
        print("\nGenerating flashcards...")
        flashcards = generate_flashcards(first_chunk, count=2)
        
        print(f"\n✓ Successfully generated {len(flashcards)} flashcards")
        
        # Validate structure
        for i, card in enumerate(flashcards, 1):
            print(f"\nFlashcard {i}:")
            print(f"  Question: {card.get('question', 'MISSING')}")
            print(f"  Answer: {card.get('answer', 'MISSING')[:100]}...")
            
            # Validate required fields
            assert 'question' in card, f"Flashcard {i} missing 'question'"
            assert 'answer' in card, f"Flashcard {i} missing 'answer'"
            assert card['question'], f"Flashcard {i} has empty question"
            assert card['answer'], f"Flashcard {i} has empty answer"
        
        print("\n✓ All flashcards validated successfully")
        return flashcards
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_multiple_flashcards():
    """Test generating flashcards from multiple chunks."""
    print("\n" + "="*60)
    print("TEST 3: Testing Multiple Chunks Flashcard Generation")
    print("="*60)
    
    try:
        print("Generating flashcards from up to 3 chunks (2 cards per chunk)...")
        flashcards = generate_flashcards_from_docs(max_chunks=3, cards_per_chunk=2)
        
        print(f"\n✓ Successfully generated {len(flashcards)} total flashcards")
        
        # Show summary
        print(f"\nFlashcard Summary:")
        for i, card in enumerate(flashcards, 1):
            print(f"  {i}. {card['question'][:80]}...")
        
        # Validate all flashcards
        for i, card in enumerate(flashcards, 1):
            assert 'question' in card, f"Flashcard {i} missing 'question'"
            assert 'answer' in card, f"Flashcard {i} missing 'answer'"
        
        print(f"\n✓ All {len(flashcards)} flashcards validated")
        return flashcards
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_json_output():
    """Test JSON serialization."""
    print("\n" + "="*60)
    print("TEST 4: Testing JSON Output")
    print("="*60)
    
    try:
        docs = get_chunks()
        if len(docs) == 0:
            print("✗ No chunks available")
            return
        
        flashcards = generate_flashcards(docs[0].page_content, count=1)
        json_output = flashcards_to_json(flashcards)
        
        print("✓ JSON output generated")
        print(f"JSON length: {len(json_output)} characters")
        print("\nJSON preview:")
        print(json_output[:300] + "..." if len(json_output) > 300 else json_output)
        
        # Validate it's valid JSON
        import json
        parsed = json.loads(json_output)
        assert isinstance(parsed, list), "JSON should be a list"
        print("\n✓ JSON is valid and parseable")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        raise


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("FLASHCARD GENERATION TEST SUITE")
    print("="*60)
    
    # Check environment variables
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    GEMINI_API_URL = os.environ.get("GEMINI_API_URL")
    if not GEMINI_API_KEY or not GEMINI_API_URL:
        print("\n✗ ERROR: Missing required environment variables")
        print("Please ensure GEMINI_API_KEY and GEMINI_API_URL are set in your .env file")
        return
    
    print("\n✓ Environment variables found")
    
    try:
        # Run tests
        test_chunking()
        test_single_flashcard()
        test_multiple_flashcards()
        test_json_output()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED!")
        print("="*60)
        
    except Exception as e:
        print("\n" + "="*60)
        print(f"✗ TESTS FAILED: {e}")
        print("="*60)
        sys.exit(1)


if __name__ == "__main__":
    main()
