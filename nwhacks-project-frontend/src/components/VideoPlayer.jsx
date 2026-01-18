import './VideoPlayer.css'

import {Plyr} from 'plyr-react';
import "plyr-react/plyr.css"

// Player source configuration
const plyrProps = {
  source: {
    type: "video",
    sources: [
      {
        src: "/15108937_3840_2160_50fps.mp4",
        type: "video/mp4",
        size: 100,
      },
    ],
    poster:
    "/15108937_3840_2160_50fps.mp4"
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
        points: [{time: 5, label: "Intro"}]
    }
  },
}


export default function VideoPlayer({chapters, videoSrc}) {
    return (
        <div id='video-player'>
            <Plyr {...{
              source: {
                type: "video",
                sources: [
                  {
                    src: videoSrc,
                    type: "video/mp4",
                    size: 100,
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
                }
              },
            }} />
                    </div>
    )
}