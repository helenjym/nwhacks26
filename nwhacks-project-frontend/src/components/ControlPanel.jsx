import './ControlPanel.css'

export default function ControlPanel({chapters}) {
    const chapterItems = chapters.map((chapter) => 
        <li key={chapter.label}>{chapter.time} - {chapter.label}</li>
    ); 
    return (
        <div id="control-panel">
            <div id="chapters">
                <p id="chapters-title">Chapters 📕</p>
                <div id='chapter-list'>
                    <ul>{chapterItems}</ul>
                </div>
            </div>
            <div id="chatbot">
            </div>
        </div>
    )
}