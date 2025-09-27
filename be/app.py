from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
import os
import io
import httpx
import time

import asyncio

from flask import Flask, request, Response, jsonify, stream_with_context

load_dotenv()
app = Flask(__name__)
CORS(app)
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


model = genai.GenerativeModel(model_name="gemini-1.5-flash")

app = Flask(__name__)
CORS(app)
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# Async helper to fetch a PDF from URL
async def fetch_pdf(client, url):
    resp = await client.get(url)
    return io.BytesIO(resp.content)

# Async helper to upload to Gemini
async def upload_pdf(pdf_data):
    # Use genai client upload method
    uploaded = genai.upload_file(pdf_data, mime_type="application/pdf")
    return uploaded

@app.route("/compare-pdfs", methods=["POST"])
async def compare_pdfs():
    files = []

    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1️⃣ If JSON with URLs
        if request.is_json:
            data = request.get_json()
            pdf_urls = data.get("pdf_urls", [])

            if len(pdf_urls) < 2:
                return jsonify({"error": "Provide at least 2 PDF URLs"}), 400

            # Download and upload concurrently
            tasks = []
            for url in pdf_urls:
                tasks.append(fetch_pdf(client, url))
            pdf_contents = await asyncio.gather(*tasks)

            # Upload concurrently
            upload_tasks = [upload_pdf(pdf) for pdf in pdf_contents]
            files = await asyncio.gather(*upload_tasks)

        # 2️⃣ If local files uploaded
        elif "files" in request.files:
            uploaded_files = request.files.getlist("files")
            if len(uploaded_files) < 2:
                return jsonify({"error": "Upload at least 2 PDF files"}), 400

            upload_tasks = []
            for f in uploaded_files:
                pdf_data = io.BytesIO(f.read())
                upload_tasks.append(upload_pdf(pdf_data))
            files = await asyncio.gather(*upload_tasks)

        else:
            return jsonify({"error": "Provide PDF URLs in JSON or upload files"}), 400

    # 3️⃣ Prompt Gemini to compare PDFs
    prompt = (
        "Compare the key findings and benchmarks of these papers. "
        "Provide results in a table."
    )

    compare_model = genai.GenerativeModel(model_name="gemini-2.5-flash")
    response = compare_model.generate_content(
    contents=files + [prompt]
    )

    return jsonify({"result": response.text})




@app.route("/", methods=["GET"])
def home():
    return "🚀 Flask Gemini API is running! Available endpoints: /chat, /stream, /compare-pdfs, /summarize-pdf"


from flask import Flask, request, Response, stream_with_context
import time

@app.route("/stream", methods=["POST"])
def stream():
    data = request.json
    message = data.get("chat", "Hello")

    def generate():
        for word in message.split():
            yield f"data: {word} \n\n"
            time.sleep(0.5)  # simulate typing

    return Response(stream_with_context(generate()), mimetype="text/event-stream")


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    msg = data.get('chat', '')
    chat_history = data.get('history', [])
    chat_session = model.start_chat(history=chat_history)
    response = chat_session.send_message(msg)
    return {"text": response.text}

@app.route("/summarize-pdf", methods=["POST"])
async def summarize_pdf():
    """
    Summarize one or more PDFs.
    Accepts:
      1. JSON with "pdf_urls": ["url1", "url2"]
      2. Local PDF uploads via multipart/form-data with key "files"
    Returns:
      JSON with AI-generated summary.
    """
    files = []

    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1️⃣ If JSON with URLs
        if request.is_json:
            data = request.get_json()
            pdf_urls = data.get("pdf_urls", [])
            if not pdf_urls:
                return jsonify({"error": "Provide at least 1 PDF URL"}), 400

            pdf_contents = await asyncio.gather(*[fetch_pdf(client, url) for url in pdf_urls])
            files = await asyncio.gather(*[upload_pdf(pdf) for pdf in pdf_contents])

        # 2️⃣ If local files uploaded
        elif "files" in request.files:
            uploaded_files = request.files.getlist("files")
            if not uploaded_files:
                return jsonify({"error": "Upload at least 1 PDF file"}), 400

            files = await asyncio.gather(*[upload_pdf(io.BytesIO(f.read())) for f in uploaded_files])

        else:
            return jsonify({"error": "Provide PDF URLs in JSON or upload files"}), 400

    # 3️⃣ Prompt Gemini to summarize
    prompt = "Summarize the main findings and contributions of these papers in concise bullet points."

    summary_model = genai.GenerativeModel(model_name="gemini-2.5-flash")
    response = summary_model.generate_content(
        contents=files + [prompt]
    )

    return jsonify({"summary": response.text})


if __name__ == '__main__':
    port = int(os.getenv("PORT", 9000))
    print(f"🚀 Server running at http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
