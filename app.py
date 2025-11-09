import streamlit as st
import requests

# Backend URL
backend_url = "http://127.0.0.1:8000"

# Streamlit App UI
st.set_page_config(page_title="Employee Chatbot", page_icon="💬", layout="wide")

st.title("💼 Employee Chatbot")
st.markdown("AI assistant for **HR, IT, and organizational support.**")

st.sidebar.title("🧾 Menu")
option = st.sidebar.radio("Choose an action", ["📄 Upload Document", "💬 Chat", "🧠 Summarize Document"])

# ============ Upload ===============
if option == "📄 Upload Document":
    file = st.file_uploader("Upload a document (PDF or TXT)", type=["pdf", "txt"])
    if st.button("Upload"):
        if file:
            with st.spinner("Uploading..."):
                files = {"file": (file.name, file.getvalue(), file.type)}
                res = requests.post(f"{backend_url}/upload/", files=files)
                st.success(res.json()["message"])
        else:
            st.warning("Please upload a file first.")

# ============ Chat =================
elif option == "💬 Chat":
    st.subheader("Ask the Chatbot")
    query = st.text_area("Enter your question:")
    if st.button("Ask"):
        if query.strip():
            with st.spinner("Thinking..."):
                res = requests.post(f"{backend_url}/chat/", data={"query": query})
                st.info(res.json()["response"])
        else:
            st.warning("Enter a valid question.")

# ============ Summarize ============
elif option == "🧠 Summarize Document":
    st.subheader("Summarize Uploaded Document")
    if st.button("Summarize"):
        with st.spinner("Summarizing..."):
            res = requests.post(f"{backend_url}/summarize/")
            st.success(res.json()["summary"])