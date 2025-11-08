import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Chat from "./pages/Chat";


import ComparePDFs from "./pages/ComparePDFs";
import SummarizePDF from "./pages/SummarizePDF";
import './App.css'

function Home() {
  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold">🚀 AI Dashboard</h1>
      <p>Use the navigation bar to access API endpoints.</p>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/compare-pdfs" element={<ComparePDFs />} />
        <Route path="/summarize-pdf" element={<SummarizePDF />} />
      </Routes>
    </Router>
  );
}
