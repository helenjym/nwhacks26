import './VideoPlayer.css'

import {Plyr} from 'plyr-react';
import "plyr-react/plyr.css"



export default function VideoPlayer({chapters, videoSrc}) {
  // Player source configuration
const plyrProps = {
  source: {
    type: "video",
    sources: [
      {
        src: videoSrc,
        type: "video/mp4",
        size: 500,
      },
    ],
    poster:
    videoSrc
  },
  options: {
    controls: [
      "play-large",
      "play",
      "progress",
      "current-time",
      "mute",
      "volume",
      "captions",
      "settings",
      "pip",
      "airplay",
      "fullscreen",
    ],
    markers: {
        enabled: true,
        points: chapters
    },
    ratio: '16:16'
  },
}
    return (
        <div id='video-player'>
            {(videoSrc === null)? 
            <div id="video-placeholder">
              <p>Upload a video!</p> 
            </div>: 
            <Plyr {...plyrProps} />}
        </div>
    )
}