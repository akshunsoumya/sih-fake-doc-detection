import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import AppRoutes from "./routes/AppRoutes";

import "./App.css";
import "./components/components.css";

function App() {
  return (
    <div className="app">

      <Navbar />

      <main>
        <AppRoutes />
      </main>

      <Footer />

    </div>
  );
}

export default App;