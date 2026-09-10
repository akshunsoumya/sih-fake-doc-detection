import { Routes, Route } from "react-router-dom";

import Home from "../pages/Home";
import Detect from "../pages/Detect";
import Results from "../pages/Results";
import History from "../pages/History";
import About from "../pages/About";

function AppRoutes() {
  return (
    <Routes>

      <Route path="/" element={<Home />} />

      <Route
        path="/detect"
        element={<Detect />}
      />

      <Route
        path="/results"
        element={<Results />}
      />

      <Route
        path="/history"
        element={<History />}
      />

      <Route
        path="/about"
        element={<About />}
      />

    </Routes>
  );
}

export default AppRoutes;