from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import nltk
from transformers import pipeline
import PyPDF2
import io

# Download NLTK data quietly
nltk.download('punkt', quiet=True)

# ================== Load NLP models ==================
# Summarizer (small, fast)
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
# Q&A model (lightweight)
qa_model = pipeline("question-answering", model="deepset/tinyroberta-squad2")

# Global variable to store uploaded document text
DOCUMENT_TEXT = ""

# ================== Initialize FastAPI ==================
app = FastAPI(title="Employee Chatbot")

# Allow requests from Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================== Routes ==================
@app.get("/")
def root():
    return {"message": "Employee Chatbot is running 🚀"}


@app.post("/upload/")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF or TXT document and store text globally for chat and summarization.
    """
    global DOCUMENT_TEXT
    try:
        content = await file.read()
        text = ""

        if file.filename.lower().endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
        else:
            text = content.decode("utf-8", errors="ignore")

        DOCUMENT_TEXT = text.strip()
        if not DOCUMENT_TEXT:
            return {"message": "No text could be extracted from the document ❌"}

        return {"message": "✅ Document uploaded successfully!"}

    except Exception as e:
        return {"message": f"❌ Error processing file: {str(e)}"}


@app.post("/chat/")
async def chat(query: str = Form(...)):
    """
    Answer employee queries based on uploaded document.
    """
    global DOCUMENT_TEXT
    if not DOCUMENT_TEXT:
        return {"response": "📄 Please upload a document first."}

    try:
        answer = qa_model(question=query, context=DOCUMENT_TEXT)
        if not answer["answer"]:
            return {"response": "I couldn't find an exact answer in the document."}
        return {"response": answer["answer"]}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}


@app.post("/summarize/")
async def summarize_doc():
    """
    Summarize the uploaded document text.
    """
    global DOCUMENT_TEXT
    if not DOCUMENT_TEXT:
        return {"summary": "📄 Please upload a document first."}

    try:
        # Process only first 3000 characters for speed
        short_text = DOCUMENT_TEXT[:3000]
        summary = summarizer(short_text, max_length=150, min_length=40, do_sample=False)
        return {"summary": summary[0]["summary_text"]}
    except Exception as e:
        return {"summary": f"Error: {str(e)}"}


# ================== Run Server ==================
if __name__ == "__main__":
    uvicorn.run("simple_chatbot:app", host="127.0.0.1", port=8000, reload=True)