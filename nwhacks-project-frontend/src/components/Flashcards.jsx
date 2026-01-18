import { useState } from 'react'
import './Flashcards.css'

export default function Flashcards({ flashcards, onClose }) {
  const [currIndex, setcurrIndex] = useState(0)
  const [showAnswer, setShowAnswer] = useState(false)

  if (!flashcards || flashcards.length == 0) return null

  const currCard = flashcards[currIndex]

  function handlePrev() {
    setShowAnswer(false)
    setcurrIndex((prev) => (prev == 0) ? (flashcards.length - 1) : (prev - 1))
  }

  function handleNext() {
    setShowAnswer(false)
    setcurrIndex((prev) => (prev + 1) % flashcards.length)
  }

  return (
    <div className="flashcard-overlay">
      <div className="flashcard-popup">
        <button className="close-btn" onClick={onClose}>✕</button>

        <h2>Test your knowledge!</h2>

        <div 
            className="flashcard-card" 
            onClick={() => setShowAnswer(!showAnswer)}
        >
          {showAnswer ? (
            <>
            <p className="flashcard-type"><strong>Answer:</strong></p>
            <p className="flashcard-answer">{currCard.answer}</p>
            </>
          ) : (
            <>
            <p className="flashcard-type"><strong>Question:</strong></p>
            <p className="flashcard-question">{currCard.question}</p>
            </>
          )}
        </div>

        <div className="flashcard-controls">
            <button onClick={handlePrev}>Prev</button>
            <button onClick={handleNext}>Next</button>
        </div>

        <div className="flashcard-progress">
          {currIndex + 1} / {flashcards.length}
        </div>
      </div>
    </div>
  )
}
