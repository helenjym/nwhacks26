import './VideoPlayer.css'


export default function VideoPlayer() {
    return (
        <div id="video-player">
            <video width="320" height="240" playsInline>
                <source src="../public/15108937_3840_2160_50fps.mp4" type="video/mp4" />
            </video>
        </div>
    )
}