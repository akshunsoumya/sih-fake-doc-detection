
import { useState } from "react";
import { NavLink } from "react-router-dom";
import { Menu, X, ShieldCheck } from "lucide-react";

function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);

  const closeMenu = () => {
    setMenuOpen(false);
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">

        {/* Logo */}
        <NavLink to="/" className="navbar-logo" onClick={closeMenu}>
          <div className="logo-icon">
            <ShieldCheck size={24} />
          </div>

          <div className="logo-text">
            <span>Doc</span>Verify
          </div>
        </NavLink>

        {/* Desktop Navigation */}
        <div className="nav-links">
          <NavLink
            to="/"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            Home
          </NavLink>

          <NavLink
            to="/detect"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            Detect Document
          </NavLink>

          <NavLink
            to="/history"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            History
          </NavLink>

          <NavLink
            to="/about"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            About
          </NavLink>
        </div>

        {/* Mobile Menu Button */}
        <button
          className="mobile-menu-button"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle navigation menu"
        >
          {menuOpen ? <X size={26} /> : <Menu size={26} />}
        </button>
      </div>

      {/* Mobile Navigation */}
      {menuOpen && (
        <div className="mobile-nav">
          <NavLink to="/" onClick={closeMenu}>
            Home
          </NavLink>

          <NavLink to="/detect" onClick={closeMenu}>
            Detect Document
          </NavLink>

          <NavLink to="/history" onClick={closeMenu}>
            History
          </NavLink>

          <NavLink to="/about" onClick={closeMenu}>
            About
          </NavLink>
        </div>
      )}
    </nav>
  );
}

export default Navbar;