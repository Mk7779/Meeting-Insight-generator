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
            return response.text[:5000]
        return ""
    except:
        return ""


def generate_insights(conversation_text):
    prompt = f"""
Analyze the following English conversation and extract structured insights.
The conversation may be a meeting, interview, discussion, debate, or casual talk.

Conversation:
{conversation_text}

Generate output in EXACTLY this format:

Summary:
- ...

Key Topics Discussed:
- ...

Decisions:
- ...

Action Items:
- ...

Additional Insights (if any):
- ...
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 600,
            "temperature": 0.3
        }
    }

    response = requests.post(
        LLM_API_URL,
        headers=HEADERS,
        json=payload
    )

    if response.status_code != 200:
        return "Insight generation failed."

    return response.json()[0]["generated_text"]

# ---------------- STREAMLIT UI ---------------- #

st.set_page_config(page_title="Conversation Insight Generator", layout="wide")

st.title("🗣️ AI Conversation Insight Generator")

st.write(
    "Analyze **any English conversation** from text, audio, video, or URL "
    "and generate structured insights automatically."
)

input_type = st.selectbox(
    "Select Input Type",
    [
        "Text Transcript",
        "Audio File",
        "Video File",
        "Conversation / Recording URL"
    ]
)

conversation_text = ""

# -------- TEXT -------- #
if input_type == "Text Transcript":
    conversation_text = st.text_area(
        "Paste English Conversation",
        height=250
    )

# -------- AUDIO -------- #
elif input_type == "Audio File":
    audio_file = st.file_uploader(
        "Upload Audio (MP3 / WAV)",
        type=["mp3", "wav"]
    )

    if audio_file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(audio_file.read())
            file_path = tmp.name

        st.info("Converting audio to text...")
        conversation_text = speech_to_text(file_path)
        st.success("Audio processed successfully!")

        st.text_area("Generated Transcript", conversation_text, height=200)

# -------- VIDEO -------- #
elif input_type == "Video File":
    video_file = st.file_uploader(
        "Upload Video (MP4 / MKV / WEBM)",
        type=["mp4", "mkv", "webm"]
    )

    if video_file:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(video_file.read())
            file_path = tmp.name

        st.info("Extracting conversation from video...")
        conversation_text = speech_to_text(file_path)
        st.success("Video processed successfully!")

        st.text_area("Generated Transcript", conversation_text, height=200)

# -------- URL -------- #
elif input_type == "Conversation / Recording URL":
    url = st.text_input("Paste Conversation or Transcript URL")

    if url:
        st.info("Fetching content from URL...")
        conversation_text = fetch_text_from_url(url)

        if conversation_text:
            st.success("Content fetched successfully!")
            st.text_area("Fetched Content", conversation_text, height=200)
        else:
            st.warning("Unable to fetch content from URL.")

# -------- GENERATE -------- #
if st.button("Generate Conversation Insights"):
    if conversation_text.strip() == "":
        st.error("Please provide valid conversation input.")
    else:
        with st.spinner("Analyzing conversation..."):
            insights = generate_insights(conversation_text)

        st.success("Insights Generated!")

        st.subheader("📌 Conversation Insights")
        st.markdown(insights)

        st.download_button(
            "📥 Download Insights",
            insights,
            file_name="conversation_insights.txt",
            mime="text/plain"
        )
