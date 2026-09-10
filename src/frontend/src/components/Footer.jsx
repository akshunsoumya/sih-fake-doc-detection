import { ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";

function Footer() {
  return (
    <footer className="footer">

      <div className="footer-container">

        <Link to="/" className="footer-brand">
          <div className="footer-logo">
            <ShieldCheck size={20} />
            <span>DocVerify</span>
          </div>
        </Link>

        <div className="footer-description">
          AI-powered official document verification with
          explainable analysis.
        </div>

        <div className="footer-links">
          <Link to="/detect">Detect</Link>
          <Link to="/history">History</Link>
          <Link to="/about">About</Link>
        </div>

      </div>

      <div className="footer-bottom">
        © {new Date().getFullYear()} DocVerify · SIH Project
      </div>

    </footer>
  );
}

export default Footer;