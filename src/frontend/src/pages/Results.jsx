import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";

import {
  ArrowLeft,
  Download,
  Share2,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  ShieldCheck,
  ShieldAlert,
  FileText,
  Fingerprint,
  Activity,
  Image as ImageIcon,
  ScanLine,
  BarChart3,
  BrainCircuit,
  Info,
  Maximize2,
  Database,
  Clock3,
  FileImage,
} from "lucide-react";

import "./Results.css";


/* =========================================================
   TEMPORARY FRONTEND DATA
   =========================================================

   BACKEND INTEGRATION:
   Remove this object when the backend API is connected.

   Expected flow:

   Detect Page
        ↓
   POST /api/analyze
        ↓
   Node / ML Backend
        ↓
   JSON response
        ↓
   navigate("/results", { state: { result: response } })

========================================================= */

const mockResult = {

  request: {
    requestId: "VER-2026-000123",
    timestamp: "2026-09-07T12:30:45Z",
    fileName: "aadhaar.jpg",
    fileSize: "245 KB",
  },

  document: {
    documentType: "Aadhaar Card",
    classifierConfidence: 0.9896,
  },

  documentAnalysis: {

    fields: [

      {
        field: "aadhaar_number",
        value: "REDACTED",
        confidence: 0.88,

        validation: {
          valid: true,
        },
      },

      {
        field: "name",
        value: "REDACTED",
        confidence: 0.88,

        validation: {
          valid: true,
        },
      },

    ],
  },

  forensicAnalysis: {

    combinedAnomalyScore: 0.1537,

    signals: {

      ela: {
        score: 0.2562,
        maxBlockError: 6,
      },

      copyMove: {
        score: 0.0000,
        geometricMatches: 0,
        keypoints: 2129,
      },

      compression: {
        jpegToRawRatio: 0.0498,
      },

      imageQuality: {
        width: 640,
        height: 640,
        brightness: 178.89,
        contrast: 66.47,
        sharpness: 212.37,
        qualityStatus: "Good",
      },

      metadata: {
        hasMetadata: false,
      },

    },
  },

  forgeryAssessment: {

    predictedClass: "Recompress",

    confidence: 0.6267,

    classProbabilities: {

      Recompress: 0.6267,
      "Copy-Move": 0.1600,
      Splice: 0.1267,
      "Double Compress": 0.0633,
      Genuine: 0.0233,
      Retype: 0.0000,

    },

  },

};


/* =========================================================
   HELPERS
========================================================= */

const percent = (value) =>
  `${(value * 100).toFixed(2)}%`;


const formatDate = (timestamp) => {

  if (!timestamp) return "—";

  return new Date(timestamp).toLocaleString(
    "en-IN",
    {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }
  );
};


const formatFieldName = (field) => {

  const names = {

    aadhaar_number: "Aadhaar Number",

    name: "Name",

  };

  return names[field] || field;

};


/* =========================================================
   RESULTS COMPONENT
========================================================= */

export default function Results() {

  const location = useLocation();

  const [result, setResult] = useState(mockResult);

  const [previewUrl, setPreviewUrl] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");


  /* =======================================================
     BACKEND INTEGRATION #1
     =======================================================

     When Detect.jsx sends the user to Results:

     navigate("/results", {
       state: {
         result: apiResponse,
         file: selectedFile
       }
     });

  ======================================================= */

  useEffect(() => {

    if (location.state?.result) {

      setResult(location.state.result);

    }


    /* =====================================================
       FRONTEND IMAGE PREVIEW

       This currently displays the file selected by the user.

       BACKEND OPTION:

       Replace this with:

       result.document.imageUrl

       when the backend provides a stored image URL.
    ===================================================== */

    if (location.state?.file) {

      const url = URL.createObjectURL(
        location.state.file
      );

      setPreviewUrl(url);

      return () => {
        URL.revokeObjectURL(url);
      };

    }

  }, [location.state]);


  const {
    request,
    document,
    documentAnalysis,
    forensicAnalysis,
    forgeryAssessment,
  } = result;


  const isSuspicious =
    forgeryAssessment.predictedClass !== "Genuine";


  /* =========================================================
     BACKEND INTEGRATION #2
     DOWNLOAD REPORT
  ========================================================= */

  const handleDownload = () => {

    /*
      BACKEND:

      GET /api/report/:requestId

      Example:

      window.open(
        `/api/report/${request.requestId}`,
        "_blank"
      );
    */

    alert(
      "Report download will be connected to the backend."
    );

  };


  /* =========================================================
     BACKEND INTEGRATION #3
     SHARE RESULT
  ========================================================= */

  const handleShare = async () => {

    /*
      BACKEND:

      The backend can generate a public result URL.

      Example:

      const response = await fetch(
        `/api/results/${request.requestId}/share`
      );

      const data = await response.json();

      navigator.clipboard.writeText(data.url);
    */

    try {

      await navigator.clipboard.writeText(
        window.location.href
      );

      alert("Result link copied.");

    } catch {

      alert("Unable to copy result link.");

    }

  };


  return (

    <div className="results-page">


      {/* =====================================================
          HEADER
      ===================================================== */}

      <header className="results-header">

        <div className="results-header-inner">


          <Link
            to="/"
            className="brand"
          >

            <div className="brand-icon">
              <ShieldCheck size={23} />
            </div>

            <span>
              <b>Doc</b>Verify
            </span>

          </Link>


          <nav className="results-nav">

            <Link to="/">
              Home
            </Link>

            <Link to="/detect">
              Detect Document
            </Link>

            <Link to="/history">
              History
            </Link>

            <Link to="/about">
              About
            </Link>

          </nav>


          <div className="header-actions">

            <span className="analysis-status">

              <span />

              Analysis Complete

            </span>


            <Link
              to="/detect"
              className="analyze-again"
            >

              <RefreshCw size={14} />

              Analyze Another

            </Link>

          </div>

        </div>

      </header>



      {/* =====================================================
          PAGE INTRO
      ===================================================== */}

      <section className="results-intro">

        <div className="results-container">


          <Link
            to="/detect"
            className="back-link"
          >

            <ArrowLeft size={15} />

            Back to Detect

          </Link>


          <div className="intro-row">


            <div>

              <div className="intro-eyebrow">
                DOCUMENT VERIFICATION
              </div>

              <h1>
                Verification Result
              </h1>

              <p>
                Detailed analysis and verification report
                of the uploaded document.
              </p>

            </div>


            <div className="intro-meta">

              <div>

                <span>
                  Analysis ID
                </span>

                <strong>
                  {request.requestId}
                </strong>

              </div>


              <div>

                <span>
                  Date & Time
                </span>

                <strong>
                  {formatDate(request.timestamp)}
                </strong>

              </div>


              <button
                onClick={handleDownload}
                className="outline-button"
              >

                <Download size={15} />

                Download Report

              </button>


              <button
                onClick={handleShare}
                className="outline-button"
              >

                <Share2 size={15} />

                Share Result

              </button>

            </div>

          </div>

        </div>

      </section>



      {/* =====================================================
          MAIN DASHBOARD
      ===================================================== */}

      <main className="results-main">

        <div className="results-container">

          <div className="results-layout">


            {/* =================================================
                LEFT DOCUMENT PANEL
            ================================================= */}

            <aside className="document-panel">


              <div className="document-panel-title">

                <span>
                  Document Preview
                </span>

                <button
                  title="View full image"
                  onClick={() => {

                    if (previewUrl) {
                      window.open(
                        previewUrl,
                        "_blank"
                      );
                    }

                  }}
                >

                  <Maximize2 size={15} />

                </button>

              </div>


              <div className="document-preview">

                {previewUrl ? (

                  <img
                    src={previewUrl}
                    alt="Uploaded document"
                  />

                ) : (

                  <div className="document-placeholder">

                    <FileImage size={42} />

                    <span>
                      Document Preview
                    </span>

                    <small>
                      Uploaded document will appear here
                    </small>

                  </div>

                )}

              </div>


              <div className="document-name">

                <h2>
                  {document.documentType}
                </h2>

                {/* Confidence badge hidden until automatic document
                    classification has its trained model available. */}

              </div>


              <div className="document-divider" />


              <div className="document-details">

                <div className="details-heading">

                  <FileText size={16} />

                  Document Details

                </div>


                <Detail
                  label="Document Type"
                  value={document.documentType}
                />

                <Detail
                  label="Analysis ID"
                  value={request.requestId}
                />

                <Detail
                  label="Date & Time"
                  value={formatDate(
                    request.timestamp
                  )}
                />

                {/* <Detail
                  label="File Name"
                  value={request.fileName}
                />

                <Detail
                  label="File Size"
                  value={request.fileSize}
                /> */}

                <Detail
                  label="Resolution"
                  value={`${forensicAnalysis.signals.imageQuality.width} × ${forensicAnalysis.signals.imageQuality.height}`}
                />

                <div className="detail-row">

                  <span>
                    Status
                  </span>

                  <strong className="detail-complete">

                    <span />

                    Analysis Completed

                  </strong>

                </div>

              </div>


              <button
                className="full-image-button"
                onClick={() => {

                  if (previewUrl) {
                    window.open(
                      previewUrl,
                      "_blank"
                    );
                  }

                }}
              >

                <Maximize2 size={15} />

                View Full Image

              </button>


            </aside>



            {/* =================================================
                RIGHT ANALYSIS PANEL
            ================================================= */}

            <section className="analysis-panel" data-active-tab={activeTab}>


              {/* ===============================================
                  VERDICT
              =============================================== */}

              <div
                className={`verdict ${
                  isSuspicious
                    ? "verdict-danger"
                    : "verdict-safe"
                }`}
              >

                <div className="verdict-icon">

                  {isSuspicious ? (
                    <ShieldAlert size={27} />
                  ) : (
                    <ShieldCheck size={27} />
                  )}

                </div>


                <div className="verdict-text">

                  <span>
                    OVERALL ASSESSMENT
                  </span>

                  <h2>

                    {isSuspicious
                      ? "Potentially Forged / Anomalous"
                      : "Document Appears Authentic"}

                  </h2>

                  <p>

                    Highest model prediction:{" "}

                    <strong>
                      {forgeryAssessment.predictedClass}
                    </strong>

                  </p>

                </div>


                <div className="verdict-stat">

                  <span>
                    Confidence
                  </span>

                  <strong>
                    {percent(
                      forgeryAssessment.confidence
                    )}
                  </strong>

                </div>


                <div className="verdict-stat">

                  <span>
                    Anomaly Score
                  </span>

                  <strong className="dark-score">
                    {forensicAnalysis.combinedAnomalyScore.toFixed(4)}
                  </strong>

                </div>

              </div>



              {/* ===============================================
                  TABBED-STYLE ANALYSIS HEADER
              =============================================== */}

              <div className="analysis-tabs" role="tablist" aria-label="Analysis sections">

                <button
                  type="button"
                  className={activeTab === "overview" ? "active" : ""}
                  onClick={() => setActiveTab("overview")}
                >
                  <FileText size={16} />
                  Overview
                </button>

                {/* Extracted Information is intentionally hidden until
                    Aadhaar OCR and field validation are connected. */}

                <button
                  type="button"
                  className={activeTab === "forensic" ? "active" : ""}
                  onClick={() => setActiveTab("forensic")}
                >
                  <Fingerprint size={16} />
                  Forensic Analysis
                </button>

                <button
                  type="button"
                  className={activeTab === "classification" ? "active" : ""}
                  onClick={() => setActiveTab("classification")}
                >
                  <BarChart3 size={16} />
                  Classification
                </button>

                <button
                  type="button"
                  className={activeTab === "explanation" ? "active" : ""}
                  onClick={() => setActiveTab("explanation")}
                >
                  <BrainCircuit size={16} />
                  AI Explanation
                </button>

              </div>



              {/* ===============================================
                  SUMMARY METRICS
              =============================================== */}

              <div className="summary-cards">


                <SummaryCard
                  icon={<FileText size={20} />}
                  type="blue"
                  label="Document Type"
                  value={document.documentType}
                  sub={`${percent(document.classifierConfidence)} confidence`}
                />


                <SummaryCard
                  icon={<ShieldAlert size={20} />}
                  type="red"
                  label="Forgery Prediction"
                  value={percent(
                    forgeryAssessment.confidence
                  )}
                  sub={forgeryAssessment.predictedClass}
                />


                <SummaryCard
                  icon={<Activity size={20} />}
                  type="orange"
                  label="Anomaly Score"
                  value={forensicAnalysis.combinedAnomalyScore.toFixed(4)}
                  sub="Combined forensic score"
                />


                <SummaryCard
                  icon={<ImageIcon size={20} />}
                  type="green"
                  label="Image Quality"
                  value={
                    forensicAnalysis
                      .signals
                      .imageQuality
                      .qualityStatus
                  }
                  sub={`Sharpness: ${forensicAnalysis.signals.imageQuality.sharpness}`}
                />


              </div>



              {/* ===============================================
                  LOWER TWO-COLUMN GRID
              =============================================== */}

              <div className="analysis-grid">


                {/* =============================================
                    EXTRACTED INFORMATION
                ============================================= */}

                <DashboardCard
                  className="extracted-card"
                  title="Extracted Information"
                  icon={<FileText size={17} />}
                  badge={`${documentAnalysis.fields.length} Fields Detected`}
                  badgeType="blue"
                >

                  <div className="data-table">

                    <div className="table-head">

                      <span>
                        Field
                      </span>

                      <span>
                        Value
                      </span>

                      <span>
                        Validation
                      </span>

                      <span>
                        Confidence
                      </span>

                    </div>


                    {documentAnalysis.fields.map(
                      (field) => (

                        <div
                          className="table-row"
                          key={field.field}
                        >

                          <strong>
                            {formatFieldName(
                              field.field
                            )}
                          </strong>

                          <span>
                            {field.value}
                          </span>

                          <span>

                            {field.validation?.valid ? (

                              <em className="valid-badge">

                                <CheckCircle2 size={11} />

                                Valid

                              </em>

                            ) : (

                              <em className="invalid-badge">

                                <AlertTriangle size={11} />

                                Invalid

                              </em>

                            )}

                          </span>

                          <span>
                            {percent(
                              field.confidence
                            )}
                          </span>

                        </div>

                      )
                    )}

                  </div>


                  <div className="card-note">

                    <Info size={14} />

                    Extracted fields are validated against
                    available document format and validation
                    rules.

                  </div>

                </DashboardCard>



                {/* =============================================
                    FORENSIC ANALYSIS
                ============================================= */}

                <DashboardCard
                  className="forensic-card"
                  title="Forensic Analysis"
                  icon={<Fingerprint size={17} />}
                  badge="Completed"
                  badgeType="green"
                >

                  <div className="forensic-table">

                    <div className="forensic-head">

                      <span>
                        Metric
                      </span>

                      <span>
                        Value
                      </span>

                      <span>
                        Details
                      </span>

                    </div>


                    <ForensicRow
                      metric="ELA"
                      value={
                        forensicAnalysis
                          .signals
                          .ela
                          .score
                          .toFixed(4)
                      }
                      detail={`Max block error: ${forensicAnalysis.signals.ela.maxBlockError}`}
                    />


                    <ForensicRow
                      metric="Copy-Move"
                      value={
                        forensicAnalysis
                          .signals
                          .copyMove
                          .score
                          .toFixed(4)
                      }
                      detail={`Geometric matches: ${forensicAnalysis.signals.copyMove.geometricMatches}`}
                    />


                    <ForensicRow
                      metric="Compression"
                      value={
                        forensicAnalysis
                          .signals
                          .compression
                          .jpegToRawRatio
                          .toFixed(4)
                      }
                      detail="JPEG / raw ratio"
                    />


                    <ForensicRow
                      metric="Image Quality"
                      value={
                        forensicAnalysis
                          .signals
                          .imageQuality
                          .qualityStatus
                      }
                      detail={`Sharpness: ${forensicAnalysis.signals.imageQuality.sharpness}`}
                    />

                  </div>

                </DashboardCard>



                {/* =============================================
                    FORGERY CLASSIFICATION
                ============================================= */}

                <DashboardCard
                  className="classification-card"
                  title="Forgery Classification"
                  icon={<BarChart3 size={17} />}
                  badge="Model Prediction"
                  badgeType="red"
                >

                  <div className="classification-list">

                    {Object.entries(
                      forgeryAssessment.classProbabilities
                    ).map(
                      ([name, probability]) => {

                        const selected =
                          name ===
                          forgeryAssessment.predictedClass;


                        return (

                          <div
                            className={`classification-row ${
                              selected
                                ? "selected"
                                : ""
                            }`}
                            key={name}
                          >

                            <span className="classification-name">

                              {name}

                              {selected && (
                                <small>
                                  PREDICTED
                                </small>
                              )}

                            </span>


                            <div className="classification-bar">

                              <span
                                style={{
                                  width:
                                    `${probability * 100}%`,
                                }}
                              />

                            </div>


                            <strong>
                              {percent(
                                probability
                              )}
                            </strong>

                          </div>

                        );

                      }
                    )}

                  </div>

                </DashboardCard>



                {/* =============================================
                    QUICK TECHNICAL DETAILS
                ============================================= */}

                <DashboardCard
                  className="technical-card"
                  title="Quick Technical Details"
                  icon={<Activity size={17} />}
                >

                  <div className="technical-details">

                    <Technical
                      label="Resolution"
                      value={`${forensicAnalysis.signals.imageQuality.width} × ${forensicAnalysis.signals.imageQuality.height}`}
                    />

                    <Technical
                      label="Brightness"
                      value={
                        forensicAnalysis
                          .signals
                          .imageQuality
                          .brightness
                      }
                    />

                    <Technical
                      label="Contrast"
                      value={
                        forensicAnalysis
                          .signals
                          .imageQuality
                          .contrast
                      }
                    />

                    <Technical
                      label="Keypoints"
                      value={
                        forensicAnalysis
                          .signals
                          .copyMove
                          .keypoints
                      }
                    />

                    <Technical
                      label="Metadata"
                      value={
                        forensicAnalysis
                          .signals
                          .metadata
                          .hasMetadata
                          ? "Detected"
                          : "Not Detected"
                      }
                    />

                    <Technical
                      label="Compression"
                      value={
                        forensicAnalysis
                          .signals
                          .compression
                          .jpegToRawRatio
                      }
                    />

                  </div>


                  <div className="ai-disclaimer">

                    <Info size={15} />

                    <span>
                      This analysis uses AI models and
                      forensic techniques. Verify important
                      documents manually before taking action.
                    </span>

                  </div>

                </DashboardCard>

              </div>


              {/* ===============================================
                  XAI SECTION
              =============================================== */}

              <div className="xai-panel explanation-card">

                <div className="xai-header">

                  <div>

                    <span>
                      EXPLAINABLE AI
                    </span>

                    <h3>
                      Why did the model reach this result?
                    </h3>

                  </div>

                  <BrainCircuit size={21} />

                </div>


                <div className="xai-items">

                  <XaiItem
                    number="01"
                    title="Primary Prediction"
                    value={
                      `${forgeryAssessment.predictedClass} — ${percent(forgeryAssessment.confidence)}`
                    }
                    text="This class received the highest probability from the forgery classification model."
                  />


                  <XaiItem
                    number="02"
                    title="Error Level Analysis"
                    value={
                      `ELA Score ${forensicAnalysis.signals.ela.score.toFixed(4)}`
                    }
                    text="ELA provides a forensic signal that can help identify inconsistent compression behaviour."
                  />


                  <XaiItem
                    number="03"
                    title="Copy-Move Analysis"
                    value={
                      `${forensicAnalysis.signals.copyMove.geometricMatches} geometric matches`
                    }
                    text="No significant geometric copy-move matches were detected in the current analysis."
                  />


                  <XaiItem
                    number="04"
                    title="Combined Forensics"
                    value={
                      `Anomaly ${forensicAnalysis.combinedAnomalyScore.toFixed(4)}`
                    }
                    text="The combined forensic score summarizes the available image-level anomaly signals."
                  />

                </div>


                {/* =================================================
                    BACKEND XAI PLACEHOLDER

                    Future backend can provide:

                    result.xai.heatmapUrl
                    result.xai.annotatedImageUrl
                    result.xai.regions

                ================================================= */}

                <div className="xai-backend-placeholder">

                  <BrainCircuit size={19} />

                  <div>

                    <strong>
                      Advanced visual explanation
                    </strong>

                    <span>
                      Heatmaps, suspicious-region overlays,
                      bounding boxes and model explanations
                      can be rendered here once returned
                      by the ML backend.
                    </span>

                  </div>

                  <small>
                    BACKEND XAI
                  </small>

                </div>

              </div>



              {/* ===============================================
                  REVIEW RECOMMENDATION
              =============================================== */}

              {isSuspicious && (

                <div className="review-banner">

                  <div className="review-banner-icon">

                    <AlertTriangle size={22} />

                  </div>


                  <div>

                    <span>
                      RECOMMENDED ACTION
                    </span>

                    <h3>
                      Manual Review Recommended
                    </h3>

                    <p>
                      The document was not classified as
                      genuine. Verify the document manually
                      before accepting it as authentic.
                    </p>

                  </div>

                </div>

              )}



              {/* ===============================================
                  BOTTOM ACTIONS
              =============================================== */}

              <div className="bottom-actions">

                <div className="completion">

                  <CheckCircle2 size={15} />

                  Analysis completed successfully

                </div>


                <div className="bottom-buttons">

                  <Link
                    to="/detect"
                    className="secondary-action"
                  >

                    <RefreshCw size={14} />

                    Analyze Another

                  </Link>


                  <Link
                    to="/history"
                    className="primary-action"
                  >

                    <Database size={14} />

                    View History

                  </Link>

                </div>

              </div>


            </section>

          </div>

        </div>

      </main>

    </div>

  );
}


/* =========================================================
   REUSABLE COMPONENTS
========================================================= */

function Detail({ label, value }) {

  return (

    <div className="detail-row">

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

    </div>

  );

}


function SummaryCard({
  icon,
  type,
  label,
  value,
  sub,
}) {

  return (

    <div className="summary-card">

      <div className={`summary-icon ${type}`}>
        {icon}
      </div>

      <div>

        <span>
          {label}
        </span>

        <strong>
          {value}
        </strong>

        <small>
          {sub}
        </small>

      </div>

    </div>

  );

}


function DashboardCard({
  className = "",
  title,
  icon,
  badge,
  badgeType,
  children,
}) {

  return (

    <div className={`dashboard-card ${className}`}>

      <div className="dashboard-card-header">

        <div>

          {icon}

          <h3>
            {title}
          </h3>

        </div>


        {badge && (

          <span
            className={`card-badge ${
              badgeType || ""
            }`}
          >
            {badge}
          </span>

        )}

      </div>


      {children}

    </div>

  );

}


function ForensicRow({
  metric,
  value,
  detail,
}) {

  return (

    <div className="forensic-row">

      <strong>
        {metric}
      </strong>

      <span>
        {value}
      </span>

      <small>
        {detail}
      </small>

    </div>

  );

}


function Technical({
  label,
  value,
}) {

  return (

    <div className="technical-item">

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

    </div>

  );

}


function XaiItem({
  number,
  title,
  value,
  text,
}) {

  return (

    <div className="xai-item">

      <div className="xai-number">
        {number}
      </div>

      <div>

        <span>
          {title}
        </span>

        <strong>
          {value}
        </strong>

        <p>
          {text}
        </p>

      </div>

    </div>

  );

}
