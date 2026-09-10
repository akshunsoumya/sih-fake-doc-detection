function ScoreCard({
  title,
  value,
  description,
  type = "default"
}) {
  return (
    <div className={`score-card score-${type}`}>

      <span className="score-title">
        {title}
      </span>

      <strong className="score-value">
        {value}
      </strong>

      {description && (
        <span className="score-description">
          {description}
        </span>
      )}

    </div>
  );
}

export default ScoreCard;