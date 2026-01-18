import './ControlPanel.css'

// const chapters = [
//     {time: "00:10", label: "Sample Marker 1"},
//     {time: "00:30", label: "Sample Marker 2"},
//     {time: "01:00", label: "Sample Marker 3"}
// ]

export default function ControlPanel({chapters}) {
    const chapterItems = chapters.map((chapter) => 
        <li key={chapter.label}>{chapter.time}: {chapter.label}</li>
    ); 
    return (
        <div>
            <ul>{chapterItems}</ul>
        </div>
    )
}