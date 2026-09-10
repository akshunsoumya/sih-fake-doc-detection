import "./Detect.css";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { analyzeDocument } from "../services/api";

import {
  ShieldCheck,
  Upload,
  FileImage,
  X,
  RefreshCw,
  ScanSearch,
  LockKeyhole,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
} from "lucide-react";

import UploadBox from "../components/UploadBox";
import DocumentPreview from "../components/DocumentPreview";
import AnalysisLoader from "../components/AnalysisLoader";

import "./Detect.css";

function Detect() {
  const navigate = useNavigate();

  const [documentType, setDocumentType] = useState("Aadhaar Card");
  const [selectedFile, setSelectedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState("");

  /*
   * ---------------------------------------------------------
   * FILE HANDLING
   * ---------------------------------------------------------
   */

    const handleFileSelect = (file) => {
      setError("");

      if (!file) {
        return;
      }

      // 10 MB frontend limit for now
      if (file.size > 10 * 1024 * 1024) {
        setError("File size must be less than 10 MB.");
        return;
      }

      setSelectedFile(file);
    };

    const handleRemoveFile = () => {
      setSelectedFile(null);
      setError("");
    };

    /*
    * ---------------------------------------------------------
    * MOCK ANALYSIS
    *
    * This will later be replaced with the actual API call.
    * ---------------------------------------------------------
    */

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError("Please upload a document before starting the analysis.");
      return;
    }

    setError("");
    setIsAnalyzing(true);

    try {
      const result = await analyzeDocument(
        selectedFile,
        documentType
      );

      navigate("/results", {
        state: {
          result,
          file: selectedFile,
          documentType,
          fileName: selectedFile.name,
          fileSize: selectedFile.size,
        },
      });
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Unable to analyze the document. Please try again."
      );
    } finally {
      setIsAnalyzing(false);
    }
  };


      /*
      * TEMPORARY MOCK BEHAVIOUR
      *
      * Later:
      *
      * selectedFile
      *      ↓
      * FormData
      *      ↓
      * Node.js API
      *      ↓
      * ML Model
      *      ↓
      * Results
      */


  //  * ---------------------------------------------------------
  //  * CLEAN UP
  //  * ---------------------------------------------------------
  //  */

  useEffect(() => {
    return () => {
      // Cleanup placeholder for future object URLs/resources
    };
  }, []);

  /*
   * ---------------------------------------------------------
   * ANALYSIS SCREEN
   * ---------------------------------------------------------
   */

  if (isAnalyzing) {
    return (
      <div className="detect-page">
        <div className="detect-container">
          <div className="analysis-wrapper">
            <AnalysisLoader />
          </div>
        </div>
      </div>
    );
  }

  /*
   * ---------------------------------------------------------
   * MAIN PAGE
   * ---------------------------------------------------------
   */

  return (
    <div className="detect-page">

      {/* =====================================================
          PAGE HEADER
      ===================================================== */}

      <section className="detect-header">

        <div className="detect-container">

          <div className="detect-header-content">

            <div className="detect-badge">
              <ScanSearch size={16} />
              <span>Document Verification</span>
            </div>

            <h1>
              Verify a document
              <span> with AI.</span>
            </h1>

            <p>
              Upload an official document and our AI system will
              analyze it for potential signs of forgery and
              manipulation.
            </p>

          </div>

        </div>

      </section>


      {/* =====================================================
          MAIN WORKSPACE
      ===================================================== */}

      <section className="detect-workspace">

        <div className="detect-container">

          <div className="workspace-grid">

            {/* =================================================
                LEFT PANEL
            ================================================= */}

            <div className="control-panel">

              <div className="panel-header">

                <div className="panel-header-icon">
                  <FileImage size={20} />
                </div>

                <div>
                  <h2>Document Details</h2>
                  <p>
                    Select the document you want to verify.
                  </p>
                </div>

              </div>


              {/* -----------------------------------------------
                  DOCUMENT TYPE
              ------------------------------------------------ */}

              <div className="form-group">

                <label htmlFor="document-type">
                  Document Type
                </label>

                <select
                  id="document-type"
                  value={documentType}
                  onChange={(event) =>
                    setDocumentType(event.target.value)
                  }
                >
                  <option value="Aadhaar Card">
                    Aadhaar Card
                  </option>

                  <option value="Passport">
                    Passport
                  </option>

                  <option value="Other">
                    Other Official Document
                  </option>
                </select>

              </div>


              {/* -----------------------------------------------
                  UPLOAD
              ------------------------------------------------ */}

              <div className="upload-section">

                <div className="upload-section-heading">

                  <div>
                    <h3>Upload Document</h3>

                    <p>
                      Use a clear image of the document.
                    </p>
                  </div>

                  <span className="required-label">
                    Required
                  </span>

                </div>


                {!selectedFile ? (
                  <UploadBox
                    onFileSelect={handleFileSelect}
                  />
                ) : (
                  <div className="selected-file">

                    <div className="selected-file-icon">
                      <FileImage size={22} />
                    </div>

                    <div className="selected-file-info">

                      <strong>
                        {selectedFile.name}
                      </strong>

                      <span>
                        {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                      </span>

                    </div>

                    <button
                      type="button"
                      className="remove-selected-file"
                      onClick={handleRemoveFile}
                      title="Remove file"
                    >
                      <X size={18} />
                    </button>

                  </div>
                )}

              </div>


              {/* -----------------------------------------------
                  ERROR
              ------------------------------------------------ */}

              {error && (
                <div className="detect-error">

                  <AlertCircle size={17} />

                  <span>{error}</span>

                </div>
              )}


              {/* -----------------------------------------------
                  ACTION BUTTON
              ------------------------------------------------ */}

              <button
                type="button"
                className="analyze-button"
                onClick={handleAnalyze}
                disabled={!selectedFile}
              >
                <ScanSearch size={19} />

                <span>
                  Analyze Document
                </span>

                <ArrowRight size={18} />

              </button>


              {/* -----------------------------------------------
                  SECURITY NOTE
              ------------------------------------------------ */}

              <div className="security-note">

                <LockKeyhole size={17} />

                <div>
                  <strong>
                    Secure document processing
                  </strong>

                  <span>
                    Your uploaded document is used only
                    for verification.
                  </span>
                </div>

              </div>

            </div>


            {/* =================================================
                RIGHT PANEL
            ================================================= */}

            <div className="preview-panel">

              <div className="preview-panel-header">

                <div>

                  <span className="preview-label">
                    PREVIEW
                  </span>

                  <h2>
                    Document Preview
                  </h2>

                </div>

                {selectedFile && (
                  <div className="ready-status">
                    <CheckCircle2 size={16} />
                    Ready
                  </div>
                )}

              </div>


              {/* -----------------------------------------------
                  EMPTY PREVIEW
              ------------------------------------------------ */}

              {!selectedFile && (
                <div className="empty-preview">

                  <div className="empty-preview-icon">
                    <FileImage size={42} />
                  </div>

                  <h3>
                    No document selected
                  </h3>

                  <p>
                    Your uploaded document will appear
                    here for preview.
                  </p>

                  <div className="preview-hint">
                    <Upload size={15} />
                    <span>
                      Upload an image to get started
                    </span>
                  </div>

                </div>
              )}


              {/* -----------------------------------------------
                  IMAGE PREVIEW
              ------------------------------------------------ */}

              {selectedFile && (
                <div className="document-preview-wrapper">

                  <DocumentPreview
                    file={selectedFile}
                    onRemove={handleRemoveFile}
                  />

                </div>
              )}

            </div>

          </div>


          {/* =================================================
              SUPPORTED FORMAT INFORMATION
          ================================================= */}

          <div className="format-information">

            <div className="format-item">

              <div className="format-icon">
                <FileImage size={18} />
              </div>

              <div>
                <strong>
                  Supported formats
                </strong>

                <span>
                  JPG, JPEG and PNG
                </span>
              </div>

            </div>


            <div className="format-divider"></div>


            <div className="format-item">

              <div className="format-icon">
                <ShieldCheck size={18} />
              </div>

              <div>
                <strong>
                  AI-powered verification
                </strong>

                <span>
                  Automated forgery analysis
                </span>
              </div>

            </div>


            <div className="format-divider"></div>


            <div className="format-item">

              <div className="format-icon">
                <LockKeyhole size={18} />
              </div>

              <div>
                <strong>
                  Maximum file size
                </strong>

                <span>
                  10 MB per document
                </span>
              </div>

            </div>

          </div>

        </div>

      </section>

    </div>
  );
}

export default Detect;