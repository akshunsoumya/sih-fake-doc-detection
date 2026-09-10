import { X, FileImage } from "lucide-react";

function DocumentPreview({ file, onRemove }) {
  if (!file) return null;

  const imageUrl = URL.createObjectURL(file);

  return (
    <div className="document-preview">

      <div className="preview-header">
        <div className="preview-title">
          <FileImage size={20} />
          <span>Document Preview</span>
        </div>

        <button
          className="remove-file"
          onClick={onRemove}
          type="button"
          aria-label="Remove file"
        >
          <X size={20} />
        </button>
      </div>

      <div className="preview-image-container">
        <img
          src={imageUrl}
          alt="Uploaded document"
          className="preview-image"
        />
      </div>

      <div className="file-information">
        <strong>{file.name}</strong>

        <span>
          {(file.size / (1024 * 1024)).toFixed(2)} MB
        </span>
      </div>

    </div>
  );
}

export default DocumentPreview;