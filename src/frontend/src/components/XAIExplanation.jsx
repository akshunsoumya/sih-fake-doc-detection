import { Brain, AlertTriangle } from "lucide-react";

function XAIExplanation({
  explanation = "The model detected inconsistencies in specific regions of the document.",
  suspiciousRegions = []
}) {
  return (
    <div className="xai-container">

      <div className="xai-header">

        <div className="xai-icon">
          <Brain size={24} />
        </div>

        <div>
          <h2>Explainable AI Analysis</h2>
          <p>
            Why the model reached this conclusion
          </p>
        </div>

      </div>

      <div className="xai-explanation">
        <p>{explanation}</p>
      </div>

      <div className="suspicious-regions">

        <h3>
          Suspicious Regions
        </h3>

        {suspiciousRegions.length > 0 ? (
          <div className="region-list">
            {suspiciousRegions.map((region, index) => (
              <div
                className="region-item"
                key={index}
              >
                <AlertTriangle size={18} />
                <span>{region}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="no-regions">
            No suspicious regions identified.
          </p>
        )}

      </div>

      <div className="xai-heatmap-placeholder">
        <div>
          <Brain size={36} />

          <h3>AI Attention Map</h3>

          <p>
            XAI heatmap will appear here after model
            integration.
          </p>
        </div>
      </div>

    </div>
  );
}

export default XAIExplanation;