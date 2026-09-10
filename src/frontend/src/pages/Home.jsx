import "./Home.css";
import { Link } from "react-router-dom";

import {
  ShieldCheck,
  Brain,
  ScanSearch,
  Zap,
  Upload,
  Cpu,
  Lightbulb,
  ArrowRight,
  FileCheck2,
  FileWarning,
  Fingerprint,
  LockKeyhole,
} from "lucide-react";

function Home() {
  return (
    <div className="home-page">

      {/* =====================================================
          HERO SECTION
      ===================================================== */}

      <section className="hero-section">

        <div className="hero-container">

          {/* Left side */}
          <div className="hero-content">

            <div className="hero-badge">
              <ShieldCheck size={16} />
              <span>AI-Powered Document Verification</span>
            </div>

            <h1>
              Detect forged documents.
              <span> Understand why.</span>
            </h1>

            <p className="hero-description">
              DocVerify uses artificial intelligence to analyze
              official documents for signs of manipulation and
              provides an explainable analysis of its decision.
            </p>

            <div className="hero-buttons">

              <Link to="/detect" className="primary-button">
                Analyze Document
                <ArrowRight size={18} />
              </Link>

              <a href="#how-it-works" className="secondary-button">
                How It Works
              </a>

            </div>

            <div className="hero-trust">

              <div>
                <ShieldCheck size={17} />
                <span>AI-based detection</span>
              </div>

              <div>
                <Fingerprint size={17} />
                <span>Explainable results</span>
              </div>

              <div>
                <LockKeyhole size={17} />
                <span>Secure analysis</span>
              </div>

            </div>

          </div>


          {/* Right side - visual */}
          <div className="hero-visual">

            <div className="scanner-card">

              <div className="scanner-header">
                <div className="scanner-status">
                  <span className="status-dot"></span>
                  <span>AI Document Scanner</span>
                </div>

                <ScanSearch size={20} />
              </div>


              <div className="document-mockup">

                <div className="document-top">
                  <div className="mock-logo"></div>

                  <div className="mock-lines">
                    <span></span>
                    <span></span>
                  </div>
                </div>

                <div className="mock-photo">
                  <div className="photo-placeholder"></div>
                </div>

                <div className="mock-information">
                  <span></span>
                  <span></span>
                  <span></span>
                  <span></span>
                </div>

                <div className="mock-qr">
                  <div className="qr-grid">
                    {Array.from({ length: 25 }).map((_, index) => (
                      <span key={index}></span>
                    ))}
                  </div>
                </div>

              </div>


              <div className="scanner-analysis">

                <div className="analysis-item">
                  <div className="analysis-icon">
                    <Brain size={16} />
                  </div>

                  <div>
                    <strong>AI Analysis</strong>
                    <span>Document structure</span>
                  </div>

                  <div className="analysis-check">
                    ✓
                  </div>
                </div>


                <div className="analysis-item">
                  <div className="analysis-icon">
                    <Lightbulb size={16} />
                  </div>

                  <div>
                    <strong>Explainable AI</strong>
                    <span>Evidence-based result</span>
                  </div>

                  <div className="analysis-check">
                    ✓
                  </div>
                </div>

              </div>

            </div>

          </div>

        </div>

      </section>


      {/* =====================================================
          FEATURES
      ===================================================== */}

      <section className="features-section">

        <div className="section-container">

          <div className="section-heading">

            <span className="section-label">
              WHY DOCVERIFY
            </span>

            <h2>
              More than just a prediction
            </h2>

            <p>
              Our system doesn't simply tell you whether a
              document is suspicious. It helps you understand
              the reasoning behind the result.
            </p>

          </div>


          <div className="features-grid">

            <div className="feature-card">

              <div className="feature-icon blue">
                <Brain size={25} />
              </div>

              <h3>AI-Powered Detection</h3>

              <p>
                Analyze document images using machine learning
                techniques designed to identify potential signs
                of digital manipulation.
              </p>

            </div>


            <div className="feature-card">

              <div className="feature-icon purple">
                <Lightbulb size={25} />
              </div>

              <h3>Explainable AI</h3>

              <p>
                Understand why a document was flagged through
                visual explanations, suspicious regions and
                model-generated evidence.
              </p>

            </div>


            <div className="feature-card">

              <div className="feature-icon green">
                <Zap size={25} />
              </div>

              <h3>Fast Analysis</h3>

              <p>
                Upload a supported document and receive an
                automated analysis without manually inspecting
                every part of the document.
              </p>

            </div>

          </div>

        </div>

      </section>


      {/* =====================================================
          HOW IT WORKS
      ===================================================== */}

      <section
        className="how-section"
        id="how-it-works"
      >

        <div className="section-container">

          <div className="section-heading">

            <span className="section-label">
              HOW IT WORKS
            </span>

            <h2>
              Three steps to verify a document
            </h2>

            <p>
              The verification process is designed to be simple,
              transparent and easy to understand.
            </p>

          </div>


          <div className="steps-container">

            <div className="step-card">

              <div className="step-number">
                01
              </div>

              <div className="step-icon">
                <Upload size={26} />
              </div>

              <h3>Upload</h3>

              <p>
                Select the document type and upload a clear
                image of the official document.
              </p>

            </div>


            <div className="step-connector">
              <ArrowRight size={22} />
            </div>


            <div className="step-card">

              <div className="step-number">
                02
              </div>

              <div className="step-icon">
                <Cpu size={26} />
              </div>

              <h3>Analyze</h3>

              <p>
                Our machine learning model examines the image
                for characteristics associated with document
                manipulation.
              </p>

            </div>


            <div className="step-connector">
              <ArrowRight size={22} />
            </div>


            <div className="step-card">

              <div className="step-number">
                03
              </div>

              <div className="step-icon">
                <Lightbulb size={26} />
              </div>

              <h3>Explain</h3>

              <p>
                View the authenticity score, model confidence
                and visual explanations behind the prediction.
              </p>

            </div>

          </div>

        </div>

      </section>


      {/* =====================================================
          DOCUMENT TYPES
      ===================================================== */}

      <section className="documents-section">

        <div className="section-container">

          <div className="section-heading">

            <span className="section-label">
              DOCUMENT VERIFICATION
            </span>

            <h2>
              Designed for official documents
            </h2>

            <p>
              Start with supported identity documents and
              expand the system to additional document types.
            </p>

          </div>


          <div className="document-types">

            <div className="document-type-card">

              <div className="document-type-icon">
                <Fingerprint size={28} />
              </div>

              <div>
                <h3>Aadhaar Card</h3>
                <p>
                  Identity document verification
                </p>
              </div>

              <FileCheck2 size={20} />

            </div>


            <div className="document-type-card">

              <div className="document-type-icon">
                <ShieldCheck size={28} />
              </div>

              <div>
                <h3>Passport</h3>
                <p>
                  Passport image analysis
                </p>
              </div>

              <FileCheck2 size={20} />

            </div>


            <div className="document-type-card">

              <div className="document-type-icon">
                <FileWarning size={28} />
              </div>

              <div>
                <h3>Other Documents</h3>
                <p>
                  Extensible document support
                </p>
              </div>

              <ArrowRight size={20} />

            </div>

          </div>

        </div>

      </section>


      {/* =====================================================
          CTA
      ===================================================== */}

      <section className="cta-section">

        <div className="cta-container">

          <div className="cta-icon">
            <ScanSearch size={30} />
          </div>

          <h2>
            Ready to analyze a document?
          </h2>

          <p>
            Upload a document and let AI examine it for
            potential signs of forgery.
          </p>

          <Link
            to="/detect"
            className="cta-button"
          >
            Analyze Document
            <ArrowRight size={18} />
          </Link>

        </div>

      </section>

    </div>
  );
}

export default Home;