import { useState, useRef } from 'react'
import './ImageUploader.css'
import { API_BASE_URL } from '../config/api'

interface ProcessingResult {
  filename: string
  status: string
  description: string
}

interface StreamingResult {
  type: string
  filename?: string
  status?: string
  description?: string
  message?: string
  error?: string
}

const ImageUploader = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<ProcessingResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [useStreaming, setUseStreaming] = useState(false)
  const [streamingResults, setStreamingResults] = useState<StreamingResult[]>([])
  const [streamingComplete, setStreamingComplete] = useState(false)
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
    setStreamingResults([])
    setStreamingComplete(false)

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      if (useStreaming) {
        await processImageStream(formData)
      } else {
        const response = await fetch(`${API_BASE_URL}/process/image`, {
          method: 'POST',
          body: formData,
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        setResult(data)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  const processImageStream = async (formData: FormData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/process/image/stream`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader!.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })

        // Process each complete line
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.trim()) {
            try {
              const data = JSON.parse(line)
              console.log('Stream event:', data)
              
              setStreamingResults(prev => [...prev, data])
              
              if (data.type === 'complete') {
                setStreamingComplete(true)
              } else if (data.type === 'error') {
                setError(data.error || 'Streaming error occurred')
              }
            } catch (parseError) {
              console.error('Error parsing stream data:', parseError)
              setError('Error processing stream data')
            }
          }
        }
      }

    } catch (err) {
      console.error('Failed to start streaming:', err)
      setError(err instanceof Error ? err.message : 'Failed to start streaming')
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

        <div className="streaming-toggle">
          <label>
            <input
              type="checkbox"
              checked={useStreaming}
              onChange={() => setUseStreaming(!useStreaming)}
              disabled={isLoading}
            />
            Streaming Mode {useStreaming ? '🎥' : '📄'}
          </label>
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

      {result && !useStreaming && (
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

      {useStreaming && streamingResults.length > 0 && (
        <div className="result-section">
          <h3>Streaming Analysis {streamingComplete ? '✅' : '🔄'}</h3>
          <div className="streaming-results">
            {streamingResults.map((item, index) => (
              <div key={index} className={`streaming-item ${item.type}`}>
                {item.type === 'start' && (
                  <div className="streaming-message">
                    <span className="streaming-icon">🚀</span>
                    <span>{item.message}</span>
                  </div>
                )}
                {item.type === 'processing' && (
                  <div className="streaming-message processing">
                    <span className="streaming-icon">⏳</span>
                    <span>{item.message}</span>
                  </div>
                )}
                {item.type === 'result' && (
                  <div className="streaming-result">
                    <div className="result-meta">
                      <span>File: {item.filename}</span>
                      <span>Status: {item.status}</span>
                    </div>
                    <p className="description">{item.description}</p>
                  </div>
                )}
                {item.type === 'complete' && (
                  <div className="streaming-message complete">
                    <span className="streaming-icon">✅</span>
                    <span>{item.message}</span>
                  </div>
                )}
                {item.type === 'error' && (
                  <div className="streaming-message error">
                    <span className="streaming-icon">❌</span>
                    <span>{item.error}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default ImageUploader
