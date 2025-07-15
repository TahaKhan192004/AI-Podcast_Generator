from dotenv import load_dotenv
import os
import json
import argparse
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
import sys

load_dotenv()  # Loads the .env file

# Access the keys
eleven_api_key = os.getenv("ELEVENLABS_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

if not eleven_api_key:
    sys.exit("Error: ELEVENLABS_API_KEY is not set in environment variables.")

if not groq_api_key:
    sys.exit("Error: GROQ_API_KEY is not set in environment variables.")

parser = argparse.ArgumentParser()
parser.add_argument("--topic", default="Area 51", help="enter topic")
parser.add_argument("--output_audio_file", default="podcast.mp3", help="enter name of audio file")
parser.add_argument("--output_script_file", default="podcast_script.txt" ,help="enter name of txt file")
parser.add_argument("--llm_model", default="llama-3.1-8b-instant" ,help="enter your choosen llm model")
parser.add_argument("--llm_provider", default="groq" ,help="enter your choosen llm provider")
parser.add_argument("--host_voice", default="1SM7GgM6IMuvQlz2BwM3",help="enter host voice id")
parser.add_argument("--guest_voice", default="Dslrhjl3ZpzrctukrQSN",help="enter guest voice id")
arr = parser.parse_args()

try:
    prompt = PromptTemplate.from_template("""
Generate a podcast script (strictly mentioning just dialogues no title,summary or extra text)between a host and a guest about {topic} of strictly only three dialogues for guest and exactly three dialogues for host.
Return it as JSON with a list of "dialogue" entries, each having:
- "speaker": "Host" or "Guest"
- "text": what they say
""")
    
    # Groq Chat Model
    model = ChatGroq(
        temperature=0.7,
        model_name=arr.llm_model,
        api_key=groq_api_key
    )

    # Format and send prompt
    formatted_prompt = prompt.format(topic=arr.topic)
    response = model.invoke(formatted_prompt)

    print(response.content)

    with open(arr.output_script_file, "w", encoding="utf-8") as f:
        f.write(response.content)
    print(f"✅ Script saved to: {arr.output_script_file}")

except Exception as e:
    print(f"❌ Error generating or saving script: {e}")
    sys.exit(1)

import io
from elevenlabs import ElevenLabs
from pydub import AudioSegment

try:
    load_dotenv()
    eleven_api_key = os.getenv("ELEVENLABS_API_KEY")

    host_voice_id = arr.host_voice
    guest_voice_id = arr.guest_voice

    client = ElevenLabs(api_key=eleven_api_key)

    cleaned_content = response.content.strip("```json").strip("```").strip()
    dialogue_data = json.loads(cleaned_content)

    final_audio = AudioSegment.silent(duration=500)

    for turn in dialogue_data:
        voice_id = host_voice_id if turn["speaker"].lower() == "host" else guest_voice_id

        response = client.text_to_speech.convert(
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            text=turn["text"],
            output_format="mp3_44100"
        )

        audio_bytes = b"".join(response)
        segment = AudioSegment.from_mp3(io.BytesIO(audio_bytes))

        final_audio += segment + AudioSegment.silent(duration=300)

    final_audio.export(arr.output_audio_file, format="mp3")
    print(f"✅ Podcast saved as {arr.output_audio_file}")

except Exception as e:
    print(f"❌ Error generating or saving audio: {e}")
    sys.exit(1)
