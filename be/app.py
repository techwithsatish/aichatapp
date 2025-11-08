from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
import os
import io
import time
import asyncio
import httpx

load_dotenv()

app = Flask(__name__)
CORS(app)

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel(model_name="gemini-1.5-flash")


# ----------- Helpers -----------
async def fetch_pdf(client, url):
    resp = await client.get(url)
    return io.BytesIO(resp.content)

async def upload_pdf(pdf_data):
    return genai.upload_file(pdf_data, mime_type="application/pdf")


# ----------- /compare-pdfs -----------
@app.route("/compare-pdfs", methods=["POST"])
def compare_pdfs():
    return asyncio.run(compare_pdfs_async())

async def compare_pdfs_async():
    files = []

    async with httpx.AsyncClient(timeout=60.0) as client:
        if request.is_json:
            data = request.get_json()
            pdf_urls = data.get("pdf_urls", [])

            if len(pdf_urls) < 2:
                return jsonify({"error": "Provide at least 2 PDF URLs"}), 400

            pdf_contents = await asyncio.gather(*[fetch_pdf(client, url) for url in pdf_urls])
            files = await asyncio.gather(*[upload_pdf(pdf) for pdf in pdf_contents])

        elif "files" in request.files:
            uploaded_files = request.files.getlist("files")

            if len(uploaded_files) < 2:
                return jsonify({"error": "Upload at least 2 PDF files"}), 400

            files = await asyncio.gather(
                *[upload_pdf(io.BytesIO(f.read())) for f in uploaded_files]
            )

        else:
            return jsonify({"error": "Provide PDF URLs in JSON or upload files"}), 400

    prompt = "Compare the key findings and benchmarks of these papers. Provide results in a table."
    compare_model = genai.GenerativeModel(model_name="gemini-2.5-flash")

    response = compare_model.generate_content(contents=files + [prompt])

    return jsonify({"result": response.text})


# ----------- /summarize-pdf -----------
@app.route("/summarize-pdf", methods=["POST"])
def summarize_pdf():
    return asyncio.run(summarize_pdf_async())

async def summarize_pdf_async():
    files = []

    async with httpx.AsyncClient(timeout=60.0) as client:
        if request.is_json:
            data = request.get_json()
            pdf_urls = data.get("pdf_urls", [])

            if not pdf_urls:
                return jsonify({"error": "Provide at least 1 PDF URL"}), 400

            pdf_contents = await asyncio.gather(*[fetch_pdf(client, url) for url in pdf_urls])
            files = await asyncio.gather(*[upload_pdf(pdf) for pdf in pdf_contents])

        elif "files" in request.files:
            uploaded_files = request.files.getlist("files")

            if not uploaded_files:
                return jsonify({"error": "Upload at least 1 PDF file"}), 400

            files = await asyncio.gather(
                *[upload_pdf(io.BytesIO(f.read())) for f in uploaded_files]
            )
        else:
            return jsonify({"error": "Provide PDF URLs in JSON or upload files"}), 400

    prompt = "Summarize the main findings and contributions of these papers in concise bullet points."
    summary_model = genai.GenerativeModel(model_name="gemini-2.5-flash")

    response = summary_model.generate_content(contents=files + [prompt])

    return jsonify({"summary": response.text})


# ----------- Chat + Stream -----------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    msg = data.get("chat", "")
    history = data.get("history", [])
    chat_session = model.start_chat(history=history)
    response = chat_session.send_message(msg)
    return {"text": response.text}

@app.route("/stream", methods=["POST"])
def stream():
    data = request.json
    message = data.get("chat", "Hello")

    def generate():
        for word in message.split():
            yield f"data: {word}\n\n"
            time.sleep(0.5)

    return Response(stream_with_context(generate()), mimetype="text/event-stream")


# ----------- Root -----------
@app.route("/", methods=["GET"])
def home():
    return "✅ Flask Gemini API is Live!"


# ----------- Run Locally Only -----------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 9000))
    app.run(host="0.0.0.0", port=port)
