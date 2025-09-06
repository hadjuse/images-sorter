import { useState } from 'react'
import ImageUploader from './components/ImageUploader'
import FolderProcessor from './components/FolderProcessor'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState<'upload' | 'folder'>('upload')

  return (
    <div className="app">
      <header className="app-header">
        <h1>Image Processing AI</h1>
        <p>Upload images or process folders with AI vision models</p>
      </header>

      <nav className="tab-nav">
        <button 
          className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          Upload Image
        </button>
        <button 
          className={`tab-button ${activeTab === 'folder' ? 'active' : ''}`}
          onClick={() => setActiveTab('folder')}
        >
          Process Folder
        </button>
      </nav>

      <main className="app-main">
        {activeTab === 'upload' ? <ImageUploader /> : <FolderProcessor />}
      </main>
    </div>
  )
}

export default App
