import { useState, useRef } from 'react'
import './ImageUploader.css'

interface ProcessingResult {
  filename: string
  status: string
  description: string
}

const ImageUploader = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<ProcessingResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setError(null)
      setResult(null)
      
      // Create preview URL
      const url = URL.createObjectURL(file)
      setPreviewUrl(url)
    }
  }

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    const file = event.dataTransfer.files[0]
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file)
      setError(null)
      setResult(null)
      
      const url = URL.createObjectURL(file)
      setPreviewUrl(url)
    }
  }

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
  }

  const processImage = async () => {
    if (!selectedFile) return

    setIsLoading(true)
    setError(null)
    setResult(null)

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const response = await fetch('http://localhost:8000/process/image', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  const clearSelection = () => {
    setSelectedFile(null)
    setPreviewUrl(null)
    setResult(null)
    setError(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="image-uploader">
      <div className="upload-section">
        <div
          className={`drop-zone ${selectedFile ? 'has-file' : ''}`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
          
          {previewUrl ? (
            <div className="preview">
              <img src={previewUrl} alt="Preview" className="preview-image" />
              <p className="file-name">{selectedFile?.name}</p>
            </div>
          ) : (
            <div className="drop-message">
              <div className="upload-icon">📁</div>
              <p>Drop an image here or click to select</p>
              <p className="file-types">Supports: JPG, PNG, GIF, WebP, HEIC</p>
            </div>
          )}
        </div>

        <div className="action-buttons">
          {selectedFile && (
            <>
              <button
                onClick={processImage}
                disabled={isLoading}
                className="process-button"
              >
                {isLoading ? 'Processing...' : 'Analyze Image'}
              </button>
              <button onClick={clearSelection} className="clear-button">
                Clear
              </button>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="error-message">
          <h3>Error</h3>
          <p>{error}</p>
        </div>
      )}

      {result && (
        <div className="result-section">
          <h3>Analysis Result</h3>
          <div className="result-content">
            <div className="result-meta">
              <span>File: {result.filename}</span>
              <span>Status: {result.status}</span>
            </div>
            <p className="description">{result.description}</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default ImageUploader
