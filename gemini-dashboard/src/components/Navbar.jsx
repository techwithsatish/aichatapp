import { NavLink } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="bg-blue-600 text-white p-4 flex space-x-4">
      <NavLink to="/" className="hover:underline">Home</NavLink>
      <NavLink to="/chat" className="hover:underline">Chat</NavLink>

      <NavLink to="/compare-pdfs" className="hover:underline">Compare PDFs</NavLink>
      <NavLink to="/summarize-pdf" className="hover:underline">Summarize PDF</NavLink>
    </nav>
  );
}
