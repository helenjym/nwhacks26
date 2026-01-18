import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import VideoPlayer from './components/VideoPlayer.jsx'
import ControlPanel from './components/ControlPanel.jsx'

function App() {

  const [videoSrc, setVideoSrc] = useState(null);
  const [chapters, setChapters] = useState([]);
  // const chapters = [{time: 10, label: "Sample Marker 1"}, {time: 30, label: "Sample Marker 2"}];

  function handleVideoUpload(e) {
    const file = e.target.files[0];
    const url = URL.createObjectURL(file);
    console.log(url);
    setVideoSrc(url);
    // send file to backend for processing and get markers
    // update markers, temp markers for now
    setChapters([{time: 1, label: "Intro"}, {time: 3, label: "Middle"}, {time: 7, label: "End"}]);
  }

  return (
    <div id="app">
      <div id='left-panel'>
        <input onChange={handleVideoUpload} accept="video/mp4" type='file'></input>
        <ControlPanel chapters={chapters}/>
      </div>
      <div id='right-panel'>
        <VideoPlayer chapters={chapters} videoSrc={videoSrc}/>
      </div>
    </div>
  )
}

export default App
