import './ControlPanel.css'
import Flashcards from './Flashcards.jsx'
import { useState } from 'react'

export default function ControlPanel({ chapters, flashcards }) {
    const chapterItems = chapters.map((chapter) =>
        <li key={chapter.label}>{chapter.time} - {chapter.label}</li>
    );

    const [showFlashcards, setShowFlashcards] = useState(false)


    return (
        <div id="control-panel">
            <div id="chapters">
                <div id="button-and-title">
                    <p id="chapters-title">Chapters 📕</p>
                    <button id="flashcards-button" onClick={() => {
                        setShowFlashcards(true)
                    }
                    }>
                        Flashcards 📄
                    </button>
                </div>
                {showFlashcards && (
                    <Flashcards
                        flashcards={flashcards}
                        onClose={() => setShowFlashcards(false)}
                    />
                )}
                <div id='chapter-list'>
                    <ul>{chapterItems}</ul>
                </div>
            </div>
            <div id="chatbot">
            </div>
        </div>
    )
}