import streamlit as st
import requests
import os
import tempfile
from pydub import AudioSegment

# ---------------- CONFIG ---------------- #
HF_API_KEY = os.getenv("HF_API_KEY")

WHISPER_API_URL = "https://api-inference.huggingface.co/models/openai/whisper-small"
LLM_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"

HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

# ---------------- FUNCTIONS ---------------- #

def speech_to_text(audio_file_path):
    with open(audio_file_path, "rb") as f:
        response = requests.post(
            WHISPER_API_URL,
            headers=HEADERS,
            data=f
        )
    return response.json().get("text", "")


def generate_insights(transcript):
    prompt = f"""
Analyze the following meeting transcript and generate structured insights.

Transcript:
{transcript}

Provide output in this format:

Summary:
- ...

Key Discussion Points:
- ...

Decisions Made:
- ...

Action Items:
- ...
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 512
        }
    }

    response = requests.post(
        LLM_API_URL,
        headers=HEADERS,
        json=payload
    )

    return response.json()[0]["generated_text"]


# ---------------- STREAMLIT UI ---------------- #

st.set_page_config(page_title="Meeting Insight Generator", layout="wide")

st.title("🎙️ AI Meeting Insight Generator")

st.markdown("""
Upload a meeting **audio file** or paste a **text transcript**,  
and the AI will generate structured meeting insights.
""")

input_type = st.radio("Select Input Type", ["Text Transcript", "Audio File"])

meeting_title = st.text_input("Meeting Title (Optional)")
meeting_type = st.selectbox(
    "Meeting Type (Optional)",
    ["Stand-up", "Planning", "Review", "Discussion", "Interview"]
)

transcript_text = ""

# -------- TEXT INPUT -------- #
if input_type == "Text Transcript":
    transcript_text = st.text_area("Paste Meeting Transcript", height=250)

# -------- AUDIO INPUT -------- #
else:
    uploaded_audio = st.file_uploader("Upload Audio File (MP3/WAV)", type=["mp3", "wav"])

    if uploaded_audio:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(uploaded_audio.read())
            audio_path = tmp.name

        st.info("Converting audio to text...")
        transcript_text = speech_to_text(audio_path)
        st.success("Audio converted successfully!")

        st.text_area("Generated Transcript", transcript_text, height=200)

# -------- PROCESS -------- #
if st.button("Generate Meeting Insights"):

    if transcript_text.strip() == "":
        st.error("Please provide transcript or audio.")
    else:
        with st.spinner("Analyzing meeting..."):
            insights = generate_insights(transcript_text)

        st.success("Insights Generated!")

        st.subheader("📌 Meeting Insights")
        st.markdown(insights)

        st.download_button(
            label="📥 Download Report",
            data=insights,
            file_name="meeting_insights.txt",
            mime="text/plain"
        )

