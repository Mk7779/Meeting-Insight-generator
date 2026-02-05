import streamlit as st
import requests
import os
import tempfile

# ---------------- CONFIG ---------------- #
HF_API_KEY = os.getenv("HF_API_KEY")

WHISPER_API_URL = "https://api-inference.huggingface.co/models/openai/whisper-small"
LLM_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"

HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

# ---------------- FUNCTIONS ---------------- #

def speech_to_text(file_path):
    with open(file_path, "rb") as f:
        response = requests.post(
            WHISPER_API_URL,
            headers=HEADERS,
            data=f
        )

    if response.status_code != 200:
        return ""

    return response.json().get("text", "")


def fetch_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text[:5000]  # limit length
        return ""
    except:
        return ""


def generate_insights(transcript):
    prompt = f"""
Analyze the following meeting content and generate structured insights.

Meeting Content:
{transcript}

Provide output in this format ONLY:

Summary:
- ...

Key Topics Discussed:
- ...

Decisions:
- ...

Action Items:
- ...

Additional Notes (if any):
- ...
"""

    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 600}
    }

    response = requests.post(
        LLM_API_URL,
        headers=HEADERS,
        json=payload
    )

    if response.status_code != 200:
        return "LLM failed to generate insights."

    return response.json()[0]["generated_text"]

# ---------------- STREAMLIT UI ---------------- #

st.set_page_config(page_title="Meeting Insight Generator", layout="wide")

st.title("📊 AI Meeting Insight Generator")

st.write(
    "Upload a meeting **audio**, **video**, paste a **transcript**, "
    "or provide a **meeting recording URL** to generate insights."
)

input_type = st.selectbox(
    "Select Input Type",
    [
        "Text Transcript",
        "Audio File",
        "Video File",
        "Meeting Recording URL"
    ]
)

transcript_text = ""

# -------- TEXT TRANSCRIPT -------- #
if input_type == "Text Transcript":
    transcript_text = st.text_area(
        "Paste Meeting Transcript",
        height=250
    )

# -------- AUDIO FILE -------- #
elif input_type == "Audio File":
    audio_file = st.file_uploader(
        "Upload Audio File (MP3 / WAV)",
        type=["mp3", "wav"]
    )

    if audio_file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(audio_file.read())
            file_path = tmp.name

        st.info("Converting audio to text...")
        transcript_text = speech_to_text(file_path)
        st.success("Audio converted successfully!")

        st.text_area("Generated Transcript", transcript_text, height=200)

# -------- VIDEO FILE -------- #
elif input_type == "Video File":
    video_file = st.file_uploader(
        "Upload Video File (MP4 / MKV / WEBM)",
        type=["mp4", "mkv", "webm"]
    )

    if video_file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(video_file.read())
            file_path = tmp.name

        st.info("Extracting speech from video...")
        transcript_text = speech_to_text(file_path)
        st.success("Video processed successfully!")

        st.text_area("Generated Transcript", transcript_text, height=200)

# -------- MEETING URL -------- #
elif input_type == "Meeting Recording URL":
    meeting_url = st.text_input("Paste Meeting Recording / Transcript URL")

    if meeting_url:
        st.info("Fetching meeting content...")
        transcript_text = fetch_text_from_url(meeting_url)

        if transcript_text:
            st.success("Content fetched successfully!")
            st.text_area("Fetched Content", transcript_text, height=200)
        else:
            st.warning("Could not fetch content from URL.")

# -------- PROCESS -------- #
if st.button("Generate Meeting Insights"):
    if transcript_text.strip() == "":
        st.error("Please provide valid meeting input.")
    else:
        with st.spinner("Analyzing meeting..."):
            insights = generate_insights(transcript_text)

        st.success("Insights Generated!")

        st.subheader("📌 Meeting Insights")
        st.markdown(insights)

        st.download_button(
            "📥 Download Summary Report",
            insights,
            file_name="meeting_insights.txt",
            mime="text/plain"
        )
