import { useState } from "react";
import { BACKEND_URL } from "../config.js";

export default function ComparePDFs() {
  const [pdfUrls, setPdfUrls] = useState("");
  const [files, setFiles] = useState([]);
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    setFiles(e.target.files);
  };

  const handleSubmit = async () => {
    setLoading(true);
    setResult("");
    setError("");

    try {
      let res;

      if (files.length > 0) {
        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
          formData.append("files", files[i]);
        }
        res = await fetch(`${BACKEND_URL}/compare-pdfs`, {
          method: "POST",
          body: formData,
        });
      } else if (pdfUrls) {
        const urls = pdfUrls
          .split("\n")
          .map((u) => u.trim())
          .filter((u) => u.length > 0);

        res = await fetch(`${BACKEND_URL}/compare-pdfs`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ pdf_urls: urls }),
        });
      } else {
        alert("Provide PDF URLs or upload files");
        setLoading(false);
        return;
      }

      const data = await res.json();
      if (res.ok) {
        setResult(data.result || JSON.stringify(data, null, 2));
      } else {
        setError(data.error || "Something went wrong");
      }
    } catch (err) {
      console.error(err);
      setError("Error connecting to backend");
    }

    setLoading(false);
  };

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Compare PDFs</h2>

      <textarea
        className="border p-2 w-full mb-2"
        placeholder="Paste PDF URLs (one per line)"
        value={pdfUrls}
        onChange={(e) => setPdfUrls(e.target.value)}
        rows={4}
      />

      <input
        type="file"
        multiple
        onChange={handleFileChange}
        className="border p-2 mb-2"
      />

      <button
        className="bg-blue-600 text-white px-4 py-2 mb-2"
        onClick={handleSubmit}
        disabled={loading}
      >
        {loading ? "Comparing..." : "Compare PDFs"}
      </button>

      {error && (
        <div className="text-red-600 p-2 border mb-2 bg-red-100">{error}</div>
      )}

      {result && (
        <div className="mt-4 p-2 border bg-gray-100 whitespace-pre-wrap">
          <strong>Result:</strong>
          <pre>{result}</pre>
        </div>
      )}
    </div>
  );
}
