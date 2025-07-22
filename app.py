import os
from dotenv import load_dotenv# ✅ Load .env file
import streamlit as st
import google.generativeai as genai
from io import BytesIO

# ==============================
# 🔧 Configuration
# ==============================
load_dotenv()  # ✅ Loads .env variables

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("🚨 GEMINI_API_KEY not found. Please set it in a .env file or environment variables.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)
try:
    gemini_model = genai.GenerativeModel("gemini-2.0-flash")
except Exception as e:
    st.error(f"❌ Failed to load Gemini model: {e}")
    st.stop()


# ==============================
# 🧠 Summarization Function
# ==============================
def summarize_with_gemini(text, style="bullet"):
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


# ==============================
# 📦 File Creation Functions
# ==============================
def create_txt_file(summary_text):
    return BytesIO(summary_text.encode("utf-8"))


def create_pdf_file(summary_text):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    text_obj = c.beginText(40, 750)

    for line in summary_text.split("\n"):
        if text_obj.getY() <= 40:
            c.showPage()
            text_obj = c.beginText(40, 750)
        text_obj.textLine(line)

    c.drawText(text_obj)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


# ==============================
# 🌟 Streamlit App UI
# ==============================
st.set_page_config(page_title="Essentia", page_icon="📝", layout="centered")

st.title("📝 Essentia")
st.subheader("From clutter to clarity in seconds.")

user_input = st.text_area(
    "Enter text to summarize:",
    height=200,
    placeholder="Paste or type your long text here..."
)

summary_style = st.radio(
    "Choose summary style:",
    ["🔹 Bullet Points", "📖 Paragraph"],
    horizontal=True
)
style = "bullet" if summary_style == "🔹 Bullet Points" else "paragraph"

if "final_summary" not in st.session_state:
    st.session_state.final_summary = ""

if user_input != st.session_state.get("previous_input", ""):
    st.session_state.final_summary = ""
    st.session_state.previous_input = user_input

if st.button("✨ Summarize") or st.session_state.final_summary:
    if not user_input.strip():
        st.warning("⚠️ Please enter some text to summarize.")
    else:
        if not st.session_state.final_summary:
            with st.spinner("⏳ Summarizing with Gemini..."):
                summary = summarize_with_gemini(user_input, style)
                st.session_state.final_summary = summary
            st.success("✅ Summary ready!")

        st.markdown(st.session_state.final_summary)

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 Download as TXT",
                create_txt_file(st.session_state.final_summary),
                file_name="summary.txt",
                mime="text/plain",
            )
        with col2:
            st.download_button(
                "📥 Download as PDF",
                create_pdf_file(st.session_state.final_summary),
                file_name="summary.pdf",
                mime="application/pdf",
            )

        if st.button("🔄 Regenerate Summary"):
            st.session_state.final_summary = ""
