import {
  ShieldCheck,
  BrainCircuit,
  SearchCheck,
  FileSearch,
  Lightbulb,
  LockKeyhole,
  ArrowRight,
  CheckCircle2,
} from "lucide-react";

import { Link } from "react-router-dom";

import "./About.css";


function About() {

  return (
    <div className="about-page">


      {/* =====================================================
          HERO
      ===================================================== */}

      <section className="about-hero">

        <div className="about-container">

          <div className="about-hero-content">

            <div className="about-badge">

              <ShieldCheck size={16} />

              <span>
                About DocVerify
              </span>

            </div>


            <h1>
              Making document
              <span> verification smarter.</span>
            </h1>


            <p>
              DocVerify is an AI-powered system designed to
              detect potentially forged official documents and
              provide an understandable explanation behind every
              verification decision.
            </p>

          </div>

        </div>

      </section>



      {/* =====================================================
          WHAT IS DOCVERIFY
      ===================================================== */}

      <section className="about-section">

        <div className="about-container">

          <div className="about-intro-grid">

            <div className="about-section-heading">

              <span className="section-label">
                THE PROJECT
              </span>

              <h2>
                What is DocVerify?
              </h2>

            </div>


            <div className="about-intro-text">

              <p>
                Official documents such as Aadhaar cards and
                passports contain sensitive information and
                security features that can be manipulated through
                sophisticated image editing techniques.
              </p>

              <p>
                DocVerify aims to assist in identifying such
                manipulations using machine learning and image
                analysis techniques.
              </p>

              <p>
                Instead of simply returning a binary result,
                the system is designed to provide an
                <strong> explainable analysis</strong> so that
                users can understand why a document was classified
                as potentially forged or authentic.
              </p>

            </div>

          </div>

        </div>

      </section>



      {/* =====================================================
          HOW IT WORKS
      ===================================================== */}

      <section className="about-section about-process-section">

        <div className="about-container">

          <div className="center-heading">

            <span className="section-label">
              HOW IT WORKS
            </span>

            <h2>
              From document to decision
            </h2>

            <p>
              DocVerify follows a simple verification workflow
              designed to make complex AI analysis easy to understand.
            </p>

          </div>


          <div className="process-grid">


            {/* STEP 01 */}

            <div className="process-card">

              <div className="process-number">
                01
              </div>

              <div className="process-icon">
                <FileSearch size={23} />
              </div>

              <h3>
                Upload
              </h3>

              <p>
                Upload an image of the official document you
                want to verify.
              </p>

            </div>


            {/* STEP 02 */}

            <div className="process-card">

              <div className="process-number">
                02
              </div>

              <div className="process-icon">
                <BrainCircuit size={23} />
              </div>

              <h3>
                AI Analysis
              </h3>

              <p>
                The document is analyzed using machine learning
                and image-based forensic techniques.
              </p>

            </div>


            {/* STEP 03 */}

            <div className="process-card">

              <div className="process-number">
                03
              </div>

              <div className="process-icon">
                <SearchCheck size={23} />
              </div>

              <h3>
                Detect
              </h3>

              <p>
                The system evaluates potential visual and
                structural signs of document manipulation.
              </p>

            </div>


            {/* STEP 04 */}

            <div className="process-card">

              <div className="process-number">
                04
              </div>

              <div className="process-icon">
                <Lightbulb size={23} />
              </div>

              <h3>
                Explain
              </h3>

              <p>
                The result is presented together with an
                explainable analysis of the model's decision.
              </p>

            </div>

          </div>

        </div>

      </section>



      {/* =====================================================
          KEY FEATURES
      ===================================================== */}

      <section className="about-section">

        <div className="about-container">

          <div className="center-heading">

            <span className="section-label">
              KEY FEATURES
            </span>

            <h2>
              Built around trustworthy verification
            </h2>

          </div>


          <div className="feature-grid">


            {/* FEATURE 01 */}

            <div className="feature-card">

              <div className="feature-icon blue">
                <BrainCircuit size={22} />
              </div>

              <div>

                <h3>
                  AI-Powered Detection
                </h3>

                <p>
                  Machine learning models analyze document
                  images to identify patterns associated with
                  potential manipulation.
                </p>

              </div>

            </div>


            {/* FEATURE 02 */}

            <div className="feature-card">

              <div className="feature-icon green">
                <Lightbulb size={22} />
              </div>

              <div>

                <h3>
                  Explainable AI
                </h3>

                <p>
                  Results are accompanied by explanations and
                  visual indicators to make the model's decision
                  easier to understand.
                </p>

              </div>

            </div>


            {/* FEATURE 03 */}

            <div className="feature-card">

              <div className="feature-icon purple">
                <SearchCheck size={22} />
              </div>

              <div>

                <h3>
                  Forensic Analysis
                </h3>

                <p>
                  The system can be designed to examine visual
                  inconsistencies and suspicious regions within
                  the document.
                </p>

              </div>

            </div>


            {/* FEATURE 04 */}

            <div className="feature-card">

              <div className="feature-icon orange">
                <LockKeyhole size={22} />
              </div>

              <div>

                <h3>
                  Secure Processing
                </h3>

                <p>
                  Documents are processed specifically for
                  verification, with security and responsible
                  handling of sensitive information in mind.
                </p>

              </div>

            </div>

          </div>

        </div>

      </section>



      {/* =====================================================
          XAI SECTION
      ===================================================== */}

      <section className="about-xai-section">

        <div className="about-container">

          <div className="xai-card">

            <div className="xai-content">

              <span className="section-label">
                WHY EXPLAINABLE AI?
              </span>

              <h2>
                Don't just say "forged."
                <br />
                Explain why.
              </h2>

              <p>
                A verification system becomes more useful when
                users can understand the reasoning behind its
                prediction. DocVerify is designed to provide
                interpretable information alongside the final
                classification.
              </p>


              <div className="xai-points">

                <div>
                  <CheckCircle2 size={17} />

                  <span>
                    Highlight suspicious regions
                  </span>
                </div>


                <div>
                  <CheckCircle2 size={17} />

                  <span>
                    Provide confidence information
                  </span>
                </div>


                <div>
                  <CheckCircle2 size={17} />

                  <span>
                    Explain factors influencing the prediction
                  </span>
                </div>

              </div>

            </div>


            <div className="xai-visual">

              <div className="xai-visual-header">

                <span>
                  AI ANALYSIS
                </span>

                <span className="xai-status">
                  Analysis Complete
                </span>

              </div>


              <div className="xai-document">

                <div className="document-scan-line"></div>

                <div className="fake-document-content">

                  <div className="fake-document-photo"></div>

                  <div className="fake-document-lines">

                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>

                  </div>

                </div>


                <div className="suspicious-region region-one">
                  <span>
                    Suspicious Region
                  </span>
                </div>

                <div className="suspicious-region region-two">
                  <span>
                    Anomaly
                  </span>
                </div>

              </div>


              <div className="xai-score">

                <div>

                  <span>
                    Forgery Risk
                  </span>

                  <strong>
                    82%
                  </strong>

                </div>

                <div className="xai-score-bar">

                  <span></span>

                </div>

              </div>

            </div>

          </div>

        </div>

      </section>



      {/* =====================================================
          CTA
      ===================================================== */}

      <section className="about-cta">

        <div className="about-container">

          <div className="cta-content">

            <ShieldCheck size={30} />

            <h2>
              Ready to verify a document?
            </h2>

            <p>
              Upload a document and explore how DocVerify
              analyzes potential signs of forgery.
            </p>


            <Link
              to="/detect"
              className="about-cta-button"
            >

              Start Verification

              <ArrowRight size={17} />

            </Link>

          </div>

        </div>

      </section>


    </div>
  );
}

export default About;