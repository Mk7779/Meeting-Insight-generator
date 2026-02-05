import streamlit as st
import requests
import os
import tempfile
import time

# ---------------- CONFIG ---------------- #
HF_API_KEY = os.getenv("HF_API_KEY")

WHISPER_API_URL = "https://api-inference.huggingface.co/models/openai/whisper-small"
LLM_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"

HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

# ---------------- FUNCTIONS ---------------- #

def generate_insights(conversation):
    prompt = f"""
You are an expert analyst.

Analyze the following English conversation and extract structured insights.
If something is not present, write "Not applicable".

Conversation:
{conversation}

Format exactly like this:

Summary:
- ...

Key Topics Discussed:
- ...

Decisions:
- ...

Action Items:
- ...

Additional Insights:
- ...
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 500,
            "temperature": 0.2
        }
    }

    for attempt in range(5):
        response = requests.post(
            LLM_API_URL,
            headers=HEADERS,
            json=payload
        )

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return data[0]["generated_text"]

        time.sleep(3)

    return """
Summary:
- Model is temporarily busy. Please click Generate again.

Key Topics Discussed:
- Not applicable

Decisions:
- Not applicable

Action Items:
- Not applicable

Additional Insights:
-Free-tier model loading delay.
"""


# ---------------- STREAMLIT UI ---------------- #

st.set_page_config(page_title="Conversation Insight Generator", layout="wide")

st.title("🗣️ AI Conversation Insight Generator")

st.write(
    "Analyze **any English conversation** from text, audio, video, or URL "
    "and instantly get structured insights."
)

input_type = st.selectbox(
    "Select Input Type",
    [
        "Text Transcript",
        "Audio File",
        "Video File",
        "Conversation URL"
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
    audio = st.file_uploader("Upload Audio (MP3 / WAV)", type=["mp3", "wav"])
    if audio:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(audio.read())
            path = tmp.name

        st.info("Converting audio to text...")
        conversation_text = speech_to_text(path)

        if conversation_text:
            st.success("Audio converted successfully")
            st.text_area("Generated Transcript", conversation_text, height=200)
        else:
            st.error("Audio transcription failed.")

# -------- VIDEO -------- #
elif input_type == "Video File":
    video = st.file_uploader("Upload Video (MP4 / MKV / WEBM)", type=["mp4", "mkv", "webm"])
    if video:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(video.read())
            path = tmp.name

        st.info("Extracting conversation from video...")
        conversation_text = speech_to_text(path)

        if conversation_text:
            st.success("Video processed successfully")
            st.text_area("Generated Transcript", conversation_text, height=200)
        else:
            st.error("Video transcription failed.")

# -------- URL -------- #
elif input_type == "Conversation URL":
    url = st.text_input("Paste conversation / transcript URL")
    if url:
        st.info("Fetching content...")
        conversation_text = fetch_text_from_url(url)

        if conversation_text:
            st.success("Content fetched successfully")
            st.text_area("Fetched Text", conversation_text, height=200)
        else:
            st.error("Could not fetch content from URL.")

# -------- GENERATE -------- #
if st.button("Generate Conversation Insights"):
    if not conversation_text.strip():
        st.error("Please provide valid conversation input.")
    else:
        with st.spinner("Analyzing conversation..."):
            insights = generate_insights(conversation_text)

        st.subheader("📌 Conversation Insights")
        st.markdown(insights)
