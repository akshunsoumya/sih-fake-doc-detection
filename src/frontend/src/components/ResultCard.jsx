import {
  ShieldCheck,
  ShieldAlert
} from "lucide-react";

function ResultCard({
  result = "forged",
  probability = 87
}) {
  const isForged = result.toLowerCase() === "forged";

  return (
    <div
      className={`result-card ${
        isForged ? "result-forged" : "result-authentic"
      }`}
    >
      <div className="result-icon">
        {isForged ? (
          <ShieldAlert size={42} />
        ) : (
          <ShieldCheck size={42} />
        )}
      </div>

      <div className="result-content">
        <span className="result-label">
          Analysis Result
        </span>

        <h2>
          {isForged
            ? "Forgery Detected"
            : "Document Appears Authentic"}
        </h2>

        <p>
          {isForged
            ? "The AI model has detected characteristics that may indicate document manipulation."
            : "The AI model did not detect significant signs of document manipulation."}
        </p>
      </div>

      <div className="result-score">
        <strong>{probability}%</strong>
        <span>
          {isForged
            ? "Forgery Probability"
            : "Authenticity Probability"}
        </span>
      </div>
    </div>
  );
}

export default ResultCard;