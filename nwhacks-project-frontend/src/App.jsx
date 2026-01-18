import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import VideoPlayer from './components/VideoPlayer.jsx'
import ControlPanel from './components/ControlPanel.jsx'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div id="app">
      <ControlPanel />
      <VideoPlayer />
    </div>
  )
}

export default App
