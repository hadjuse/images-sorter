import React from 'react'
import './ImagePreview.css'
import { API_BASE_URL } from '../config/api'

interface ImagePreview {
  image_path: string
  filename: string
}

interface ImagePreviewProps {
  previews: ImagePreview[]
  maxImages: number
  onClear: () => void
}

const ImagePreview: React.FC<ImagePreviewProps> = ({ previews, maxImages, onClear }) => {
  if (previews.length === 0) {
    return null
  }

  return (
    <div className="preview-section">
      <div className="preview-header">
        <div className="preview-info">
          <h3>Found {previews.length} images</h3>
          <p className="preview-note">
            Will process up to {maxImages} images from this selection
          </p>
        </div>
        <button onClick={onClear} className="clear-preview-button">
          Clear Preview
        </button>
      </div>
      
      <div className="preview-grid">
        {previews.slice(0, 20).map((preview, index) => (
          <div key={index} className="preview-item">
            <img 
              src={`${API_BASE_URL}/image/${encodeURIComponent(preview.image_path)}`}
              alt={preview.filename}
              className="preview-thumbnail"
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><rect width="100" height="100" fill="%23f3f4f6"/><text x="50" y="50" text-anchor="middle" dy="0.3em" fill="%239ca3af" font-size="12">No Image</text></svg>';
              }}
            />
            <span className="preview-filename">{preview.filename}</span>
            {index < maxImages && (
              <div className="will-process-badge">Will process</div>
            )}
          </div>
        ))}
        {previews.length > 20 && (
          <div className="preview-more">
            +{previews.length - 20} more images
          </div>
        )}
      </div>
    </div>
  )
}

export default ImagePreview
