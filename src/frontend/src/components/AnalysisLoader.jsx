import { LoaderCircle, CheckCircle2 } from "lucide-react";

function AnalysisLoader() {
  return (
    <div className="analysis-loader">

      <div className="loader-spinner">
        <LoaderCircle size={42} />
      </div>

      <h2>Analyzing Document</h2>

      <p>
        Our AI model is examining the document for signs
        of manipulation.
      </p>

      <div className="analysis-steps">

        <div className="analysis-step completed">
          <CheckCircle2 size={19} />
          <span>Uploading document</span>
        </div>

        <div className="analysis-step completed">
          <CheckCircle2 size={19} />
          <span>Preprocessing image</span>
        </div>

        <div className="analysis-step processing">
          <LoaderCircle size={19} />
          <span>Detecting forgery</span>
        </div>

        <div className="analysis-step">
          <span className="step-circle"></span>
          <span>Generating explanation</span>
        </div>

      </div>

    </div>
  );
}

export default AnalysisLoader;