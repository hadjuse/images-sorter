import { useState } from 'react'
import './FolderProcessor.css'
import ImagePreview from './ImagePreview'
import { API_BASE_URL } from '../config/api'

interface FolderRequest {
  folder_path: string
  extension: string
  max_images: number
}

interface FolderResult {
  folder_path: string
  extension: string
  total_found: number
  processed: number
  successful: number
  failed: number
  results: Array<{
    image_path: string
    status: string
    description?: string
    error?: string
  }>
}

interface ImagePreviewData {
  image_path: string
  filename: string
}

const FolderProcessor = () => {
  const [formData, setFormData] = useState<FolderRequest>({
    folder_path: '/mnt/c/Users/pc/Pictures/ted/',
    extension: 'png',
    max_images: 7
  })
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingPreview, setIsLoadingPreview] = useState(false)
  const [isAutoLoading, setIsAutoLoading] = useState(false)
  const [imagePreviews, setImagePreviews] = useState<ImagePreviewData[]>([])
  const [result, setResult] = useState<FolderResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [autoPreviewEnabled, setAutoPreviewEnabled] = useState(true)
  const [useStreaming, setUseStreaming] = useState(false)
  const [streamingResults, setStreamingResults] = useState<any[]>([])
  const [streamingMetadata, setStreamingMetadata] = useState<any>(null)
  const [streamingComplete, setStreamingComplete] = useState(false)

  const handleInputChange = (field: keyof FolderRequest, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
    
    // Clear previews when folder path or extension changes
    if (field === 'folder_path' || field === 'extension') {
      setImagePreviews([])
      
      // Auto-load preview for the new folder/extension if enabled
      if (autoPreviewEnabled && value && typeof value === 'string' && value.trim() !== '') {
        setIsAutoLoading(true)
        setError(null)
        
        setTimeout(() => {
          loadPreview().finally(() => {
            setIsAutoLoading(false)
          })
        }, 300) // Small delay to allow state to update
      }
    }
  }

  const loadPreview = async () => {
    if (!formData.folder_path.trim()) return

    setIsLoadingPreview(true)
    setError(null)

    try {
      const response = await fetch(`${API_BASE_URL}/preview/folder`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          folder_path: formData.folder_path,
          extension: formData.extension
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        const errorMessage = errorData.detail || `HTTP error! status: ${response.status}`
        throw new Error(errorMessage)
      }

      const data = await response.json()
      
      if (!data.image_paths || data.image_paths.length === 0) {
        setError(`No ${formData.extension} images found in the specified folder`)
        setImagePreviews([])
        return
      }
      
      const previews: ImagePreviewData[] = data.image_paths.map((path: string) => ({
        image_path: path,
        filename: path.split('/').pop() || path
      }))
      
      setImagePreviews(previews)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load preview'
      
      // More specific error messages
      if (errorMessage.includes('404')) {
        setError('Folder not found. Please check the path and try again.')
      } else if (errorMessage.includes('not a directory')) {
        setError('The specified path is not a folder. Please provide a valid folder path.')
      } else if (errorMessage.includes('permission')) {
        setError('Permission denied. The application cannot access this folder.')
      } else {
        setError(`Preview failed: ${errorMessage}`)
      }
    } finally {
      setIsLoadingPreview(false)
    }
  }

  const processFolder = async () => {
    setIsLoading(true)
    setError(null)
    setResult(null)
    setStreamingResults([])
    setStreamingMetadata(null)
    setStreamingComplete(false)

    try {
      if (useStreaming) {
        await processFolderStream()
      } else {
        const response = await fetch(`${API_BASE_URL}/process/folder`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData),
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

  const processFolderStream = async () => {
    try {
      const eventSource = new EventSource(
        `${API_BASE_URL}/process/folder/stream?folder_path=${encodeURIComponent(formData.folder_path)}&extension=${formData.extension}&max_images=${formData.max_images}`
      )

      eventSource.onopen = () => {
        console.log('Streaming connection opened')
      }

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          console.log('Stream event:', data)
          
          switch (data.type) {
            case 'metadata':
              setStreamingMetadata(data)
              break
              
            case 'start':
              // Add placeholder for starting image
              setStreamingResults(prev => [
                ...prev,
                {
                  image_path: data.image_path,
                  status: 'processing',
                  description: 'Processing...',
                  index: data.index,
                  total: data.total
                }
              ])
              break
              
            case 'result':
              setStreamingResults(prev => 
                prev.map(item => 
                  item.image_path === data.image_path 
                    ? { ...item, ...data, processing: false }
                    : item
                )
              )
              break
              
            case 'complete':
              setStreamingComplete(true)
              eventSource.close()
              break
              
            case 'error':
              setError(data.error || 'Streaming error occurred')
              eventSource.close()
              break
          }
        } catch (parseError) {
          console.error('Error parsing stream data:', parseError)
          setError('Error processing stream data')
          eventSource.close()
        }
      }

      eventSource.onerror = (error) => {
        console.error('Streaming error:', error)
        setError('Streaming connection error')
        eventSource.close()
      }

    } catch (err) {
      console.error('Failed to start streaming:', err)
      setError(err instanceof Error ? err.message : 'Failed to start streaming')
    }
  }

  const clearResults = () => {
    setResult(null)
    setError(null)
    setImagePreviews([])
  }

  const clearPreview = () => {
    setImagePreviews([])
  }

  return (
    <div className="folder-processor">
      <div className="form-section">
        <h3>Folder Configuration</h3>
        
        <div className="form-group">
          <div className="auto-preview-toggle">
            <label>
              <input
                type="checkbox"
                checked={autoPreviewEnabled}
                onChange={() => setAutoPreviewEnabled(!autoPreviewEnabled)}
              />
              Auto Preview {autoPreviewEnabled ? '🔄' : '🚫'}
            </label>
          </div>
          <div className="streaming-toggle">
            <label>
              <input
                type="checkbox"
                checked={useStreaming}
                onChange={() => setUseStreaming(!useStreaming)}
              />
              Streaming Mode {useStreaming ? '🎥' : '📄'}
            </label>
          </div>
          <label htmlFor="folder-path">Folder Path</label>
          <input
            id="folder-path"
            type="text"
            value={formData.folder_path}
            onChange={(e) => handleInputChange('folder_path', e.target.value)}
            placeholder="/path/to/images"
            className="path-input"
          />
          {isAutoLoading && (
            <div className="auto-loading-indicator">
              <span className="loading-text">Loading preview...</span>
              <div className="loading-spinner"></div>
            </div>
          )}
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="extension">File Extension</label>
            <select
              id="extension"
              value={formData.extension}
              onChange={(e) => handleInputChange('extension', e.target.value)}
              className="extension-select"
            >
              <option value="png">PNG</option>
              <option value="jpg">JPG</option>
              <option value="jpeg">JPEG</option>
              <option value="gif">GIF</option>
              <option value="webp">WebP</option>
              <option value="heic">HEIC</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="max-images">Max Images</label>
            <input
              id="max-images"
              type="number"
              min="1"
              max="50"
              value={formData.max_images}
              onChange={(e) => handleInputChange('max_images', parseInt(e.target.value) || 1)}
              className="number-input"
            />
          </div>
        </div>

        <div className="action-buttons">
          <button
            onClick={loadPreview}
            disabled={isLoadingPreview || !formData.folder_path}
            className="preview-button"
          >
            {isLoadingPreview ? 'Loading...' : 'Preview Images'}
          </button>
          <button
            onClick={processFolder}
            disabled={isLoading || !formData.folder_path}
            className="process-button"
          >
            {isLoading ? 'Processing...' : 'Process Folder'}
          </button>
          {result && (
            <button onClick={clearResults} className="clear-button">
              Clear Results
            </button>
          )}
        </div>
      </div>

      <ImagePreview 
        previews={imagePreviews}
        maxImages={formData.max_images}
        onClear={clearPreview}
      />

      {error && (
        <div className="error-message">
          <h3>Error</h3>
          <p>{error}</p>
        </div>
      )}

      {result && !useStreaming && (
        <div className="results-section">
          <div className="results-summary">
            <h3>Processing Summary</h3>
            <div className="summary-stats">
              <div className="stat">
                <span className="stat-label">Found:</span>
                <span className="stat-value">{result.total_found}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Processed:</span>
                <span className="stat-value">{result.processed}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Successful:</span>
                <span className="stat-value success">{result.successful}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Failed:</span>
                <span className="stat-value error">{result.failed}</span>
              </div>
            </div>
          </div>

          <div className="results-list">
            <h4>Individual Results</h4>
            {result.results.map((item, index) => (
              <div key={index} className={`result-item ${item.status}`}>
                <div className="result-content">
                  <div className="image-preview">
                    <img 
                      src={`${API_BASE_URL}/image/${encodeURIComponent(item.image_path)}`}
                      alt={item.image_path.split('/').pop()}
                      className="result-image"
                      onError={(e) => {
                        // If the image fails to load, hide it and show a placeholder
                        const target = e.target as HTMLImageElement;
                        target.style.display = 'none';
                        const placeholder = target.nextElementSibling as HTMLElement;
                        if (placeholder) placeholder.style.display = 'flex';
                      }}
                    />
                    <div className="image-placeholder" style={{display: 'none'}}>
                      <div className="placeholder-icon">🖼️</div>
                      <span>Image not available</span>
                    </div>
                  </div>
                  <div className="result-text">
                    <div className="result-header">
                      <span className="image-path">{item.image_path.split('/').pop()}</span>
                      <span className={`status-badge ${item.status}`}>{item.status}</span>
                    </div>
                    {item.status === 'success' && item.description && (
                      <p className="description">{item.description}</p>
                    )}
                    {item.status === 'error' && item.error && (
                      <p className="error-text">{item.error}</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {useStreaming && streamingMetadata && (
        <div className="results-section">
          <div className="results-summary">
            <h3>Streaming Processing {streamingComplete ? '✅' : '🔄'}</h3>
            <div className="summary-stats">
              <div className="stat">
                <span className="stat-label">Found:</span>
                <span className="stat-value">{streamingMetadata.total_found}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Processed:</span>
                <span className="stat-value">{streamingResults.length}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Successful:</span>
                <span className="stat-value success">{streamingResults.filter(r => r.status === 'success').length}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Failed:</span>
                <span className="stat-value error">{streamingResults.filter(r => r.status === 'error').length}</span>
              </div>
            </div>
          </div>

          <div className="results-list">
            <h4>Streaming Results {streamingResults.filter(r => r.status === 'processing').length > 0 && '🔄'}</h4>
            {streamingResults.map((item, index) => (
              <div key={index} className={`result-item ${item.status}`}>
                <div className="result-content">
                  <div className="image-preview">
                    <img 
                      src={`${API_BASE_URL}/image/${encodeURIComponent(item.image_path)}`}
                      alt={item.image_path.split('/').pop()}
                      className="result-image"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.style.display = 'none';
                        const placeholder = target.nextElementSibling as HTMLElement;
                        if (placeholder) placeholder.style.display = 'flex';
                      }}
                    />
                    <div className="image-placeholder" style={{display: 'none'}}>
                      <div className="placeholder-icon">🖼️</div>
                      <span>Image not available</span>
                    </div>
                  </div>
                  <div className="result-text">
                    <div className="result-header">
                      <span className="image-path">{item.image_path.split('/').pop()}</span>
                      <span className={`status-badge ${item.status}`}>{item.status}</span>
                      {item.index && item.total && (
                        <span className="progress-indicator">
                          {item.index}/{item.total}
                        </span>
                      )}
                    </div>
                    {item.status === 'processing' && (
                      <div className="streaming-description">
                        <div className="typing-indicator">
                          <span>Processing</span>
                          <span className="dot-typing"></span>
                        </div>
                      </div>
                    )}
                    {item.status === 'success' && item.description && (
                      <p className="description streaming-description">{item.description}</p>
                    )}
                    {item.status === 'error' && item.error && (
                      <p className="error-text">{item.error}</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default FolderProcessor
