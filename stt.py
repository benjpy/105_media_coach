import os
import google.generativeai as genai

def configure_genai():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    genai.configure(api_key=api_key)

def transcribe_audio(audio_bytes):
    """
    Transcribes audio bytes using Gemini 1.5 Flash.
    """
    configure_genai()
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = "Transcribe the following audio exactly as spoken. Do not add any commentary or timestamps."
    
    response = model.generate_content([
        prompt,
        {
            "mime_type": "audio/wav",
            "data": audio_bytes
        }
    ])
    
    return response.text
