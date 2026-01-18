import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import VideoPlayer from './components/VideoPlayer.jsx'
import ControlPanel from './components/ControlPanel.jsx'

function App() {

  const [videoSrc, setVideoSrc] = useState(null);
  const [chapters, setChapters] = useState([]);

  async function handleVideoUpload(e) {
    const file = e.target.files[0];
    const url = URL.createObjectURL(file);
    console.log(url);
    setVideoSrc(url);
    
    try {
      const formData = new FormData();
      formData.append('video', file);
      const response = await fetch('http://localhost:5000/api/upload', {
        method: 'POST',
        body: formData
      })
    } catch(err) {

    }
    const data = await response.json();
    setChapters(data.chapters);
  }

  return (
    <div id="app">
      <div id='left-panel'>
        <label id="video-upload">
        <img 
          src="upload_16147059.png" 
          alt="Upload" 
          style={{marginTop: "-4px", width: "16px", height: "16px", verticalAlign: "middle", marginRight: "8px" }}
        />
          Upload Video
          <input id="video-file-upload" onChange={handleVideoUpload} accept="video/mp4" type='file'></input>
        </label>
        <ControlPanel chapters={chapters}/>
      </div>
      <div id='right-panel'>
        <VideoPlayer chapters={chapters} videoSrc={videoSrc}/>
      </div>
    </div>
  )
}

export default App
