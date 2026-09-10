import { useRef, useState } from "react";
import { Upload, FileImage } from "lucide-react";

function UploadBox({ onFileSelect }) {
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFile = (file) => {
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      alert("Please upload an image file.");
      return;
    }

    onFileSelect(file);
  };

  const handleInputChange = (event) => {
    const file = event.target.files[0];
    handleFile(file);
  };

  const handleDrop = (event) => {
    event.preventDefault();

    setIsDragging(false);

    const file = event.dataTransfer.files[0];
    handleFile(file);
  };

  return (
    <div
      className={`upload-box ${isDragging ? "dragging" : ""}`}
      onDragOver={(event) => {
        event.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current.click()}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        hidden
        onChange={handleInputChange}
      />

      <div className="upload-icon">
        {isDragging ? (
          <FileImage size={42} />
        ) : (
          <Upload size={42} />
        )}
      </div>

      <h3>
        {isDragging
          ? "Drop your document here"
          : "Upload your document"}
      </h3>

      <p>
        Drag & drop your document here or click to browse
      </p>

      <span className="upload-format">
        Supported formats: JPG, JPEG, PNG
      </span>
    </div>
  );
}

export default UploadBox;