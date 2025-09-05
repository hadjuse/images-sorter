import { useState } from 'react'
import './FolderProcessor.css'
import ImagePreview from './ImagePreview'

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
    folder_path: '/mnt/c/Users/pc/Pictures/madagascar/',
    extension: 'jpg',
    max_images: 7
  })
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingPreview, setIsLoadingPreview] = useState(false)
  const [imagePreviews, setImagePreviews] = useState<ImagePreviewData[]>([])
  const [result, setResult] = useState<FolderResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleInputChange = (field: keyof FolderRequest, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
    
    // Clear previews when folder path or extension changes
    if (field === 'folder_path' || field === 'extension') {
      setImagePreviews([])
    }
  }

  const loadPreview = async () => {
    if (!formData.folder_path.trim()) return

    setIsLoadingPreview(true)
    setError(null)

    try {
      const response = await fetch('http://localhost:8000/preview/folder', {
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
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      const previews: ImagePreviewData[] = data.image_paths.map((path: string) => ({
        image_path: path,
        filename: path.split('/').pop() || path
      }))
      
      setImagePreviews(previews)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load preview')
    } finally {
      setIsLoadingPreview(false)
    }
  }

  const processFolder = async () => {
    setIsLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('http://localhost:8000/process/folder', {
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
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsLoading(false)
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
          <label htmlFor="folder-path">Folder Path</label>
          <input
            id="folder-path"
            type="text"
            value={formData.folder_path}
            onChange={(e) => handleInputChange('folder_path', e.target.value)}
            placeholder="/path/to/images"
            className="path-input"
          />
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
              <option value="jpg">JPG</option>
              <option value="jpeg">JPEG</option>
              <option value="png">PNG</option>
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

      {result && (
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
                      src={`http://localhost:8000/image/${encodeURIComponent(item.image_path)}`}
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
    </div>
  )
}

export default FolderProcessor
