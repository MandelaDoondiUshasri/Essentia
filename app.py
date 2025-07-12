import os
import requests
import streamlit as st
import google.generativeai as genai
from io import BytesIO

# ==============================
# 🔧 Configuration
# ==============================
OLLAMA_URL = "http://localhost:11434/api/generate"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-pro")


# ==============================
# 🧠 Summarization Functions
# ==============================
def summarize_with_gemini(text, style="bullet"):
    """Summarize text using Gemini API."""
    prompt = (
        "Summarize the following text into 3 simple and clear bullet points "
        if style == "bullet" else
        "Summarize the following text in a single concise paragraph "
    )
    prompt += "suitable for a general audience:\n\n" + text

    try:
        response = gemini_model.generate_content(prompt, stream=False)
        return response.text.strip()
    except Exception as e:
        return f"❌ Gemini Error: {str(e)}"


def summarize_with_ollama(text, style="bullet"):
    """Summarize text using Local Ollama API."""
    prompt = (
        "Summarize the following text into 3 simple and clear bullet points "
        if style == "bullet" else
        "Summarize the following text in a single concise paragraph "
    )
    prompt += "suitable for a general audience:\n\n" + text

    payload = {
        "model": "gemma:2b",  # Update if using different Ollama model
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        if response.status_code == 200:
            return response.json().get("response", "No summary generated.").strip()
        else:
            return f"❌ Ollama Error: {response.text}"
    except Exception as e:
        return f"❌ Ollama Connection Error: {str(e)}"


def combine_summaries(gemini_summary, ollama_summary, style="bullet"):
    """Combine Gemini and Ollama summaries intelligently."""
    if "Error" in gemini_summary:
        return ollama_summary
    if "Error" in ollama_summary:
        return gemini_summary

    refine_prompt = (
        "Combine and refine the following two summaries into a single, concise, high-quality summary "
        "without mentioning their sources:\n\n"
        f"Summary 1:\n{gemini_summary}\n\nSummary 2:\n{ollama_summary}"
    )
    refine_prompt += (
        "\n\nReturn the final summary as 3 bullet points." if style == "bullet"
        else "\n\nReturn the final summary as a single paragraph."
    )

    try:
        response = gemini_model.generate_content(refine_prompt, stream=False)
        return response.text.strip()
    except Exception:
        # Fallback: concatenate both
        return f"{gemini_summary}\n\n{ollama_summary}"


# ==============================
# 📦 File Creation Functions
# ==============================
def create_txt_file(summary_text):
    """Create a TXT file from summary text."""
    return BytesIO(summary_text.encode("utf-8"))


def create_pdf_file(summary_text):
    """Create a PDF file from summary text."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    text_obj = c.beginText(40, 750)
    for line in summary_text.split("\n"):
        text_obj.textLine(line)
    c.drawText(text_obj)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


# ==============================
# 🌟 Streamlit App UI
# ==============================
st.set_page_config(page_title="InstaGist", page_icon="📝", layout="centered")

st.title("📝 InstaGist")
st.subheader("From essay to essence in a click.")

# Text input
user_input = st.text_area(
    "Enter text to summarize:",
    height=200,
    placeholder="Paste or type your long text here..."
)

# Summary style selection
summary_style = st.radio(
    "Choose summary style:",
    ["🔹 Bullet Points", "📖 Paragraph"],
    horizontal=True
)
style = "bullet" if summary_style == "🔹 Bullet Points" else "paragraph"

# Session state to store the finest summary
if "finest_summary" not in st.session_state:
    st.session_state.finest_summary = ""

# Main summarization flow
if st.button("✨ Summarize") or st.session_state.finest_summary:
    if not user_input.strip():
        st.warning("⚠️ Please enter some text to summarize.")
    else:
        if not st.session_state.finest_summary:
            # Show loading message
            status_placeholder = st.info("⏳ Generating the finest summary...")
            summary_placeholder = st.empty()

            # Generate summaries
            gemini_summary = summarize_with_gemini(user_input, style)
            ollama_summary = summarize_with_ollama(user_input, style)

            # Combine and save to session
            st.session_state.finest_summary = combine_summaries(gemini_summary, ollama_summary, style)

            # Clear loading message
            status_placeholder.empty()
            st.success("✅ Summary ready!")

        # Display summary
        st.markdown(st.session_state.finest_summary)

        # Download options
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 Download as TXT",
                create_txt_file(st.session_state.finest_summary),
                file_name="summary.txt",
                mime="text/plain",
            )
        with col2:
            st.download_button(
                "📥 Download as PDF",
                create_pdf_file(st.session_state.finest_summary),
                file_name="summary.pdf",
                mime="application/pdf",
            )

        # Regenerate button
        if st.button("🔄 Regenerate Summary"):
            st.session_state.finest_summary = ""
