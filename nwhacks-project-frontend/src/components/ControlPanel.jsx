import './ControlPanel.css'

export default function ControlPanel(chapters) {
    return (
        <div id='control-panel'>
            {chapters.map((chapter) =>
                <p>{chapter}</p>
            )}
        </div>
    )
}