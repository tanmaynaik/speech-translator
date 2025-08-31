#Backend
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from murf import Murf
import assemblyai as aai
import os
import requests

client = Murf(
    api_key="ap2_54e91e5e-8ac8-4d96-ab04-cdae5ff7a0f3",
)
aai.settings.api_key = "dbdf9b629dcb4adba4a4cdd12a2ecf51"


def translate_text(text, target_lang):
    """
    Translate text using Murf API
    """
    try:
        response = client.text.translate(
            target_language=target_lang,
            texts=[text],
        )
        return response.translations[0].translated_text
    except Exception as e:
        print(f"Translation error: {e}")
        return None

app = Flask(__name__)
CORS(app)  # This allows your React app to communicate with Flask

# Original web interface route (keep existing)
@app.route('/')
def home_display():
    return render_template("index.html")

@app.route('/', methods=["POST"])
def submit():
    text = request.form.get('paragraph')
    locale = request.form.get('language')
    translated_text = translate_text(text, locale)
    return render_template("index.html", translated_text=translated_text)

# NEW API endpoint for your React frontend
@app.route('/api/translate', methods=["POST"])
def api_translate():
    """
    API endpoint for React frontend
    Expected JSON format: {
        "text": "Hello world",
        "targetLanguage": "es"
    }
    Returns: {
        "translatedText": "Hola mundo",
        "success": true
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided", "success": False}), 400
        
        text = data.get('text', '').strip()
        
        target_lang = data.get('targetLanguage', 'es')
        
        if not text:
            return jsonify({"error": "No text provided", "success": False}), 400
        
        # Map frontend language codes to Murf API language codes
        lang_mapping = {
            'en': 'en-US',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE',
            'it': 'it-IT',
            'pt': 'pt-BR',
            'ja': 'ja-JP',
            'ko': 'ko-KR',
            'zh': 'zh-CN',
            'ar': 'ar-SA',
            'hi': 'hi-IN',
            'ta': 'ta-IN',
            'bn': 'bn-IN',
            'nl': 'nl-NL',
            'pl': 'pl-PL',
            'ru': 'ru-RU'
        }
        
        # Convert to Murf API format
        murf_target_lang = lang_mapping.get(target_lang, 'en-US')
        
        translated_text = translate_text(text, murf_target_lang)
        
        if translated_text:
            return jsonify({
                "translatedText": translated_text,
                "success": True,
                # "sourceLanguage": source_lang,
                "targetLanguage": target_lang
            })
        else:
            return jsonify({
                "error": "Translation service failed",
                "success": False
            }), 500
            
    except Exception as e:
        print(f"API error: {e}")
        return jsonify({
            "error": str(e),
            "success": False
        }), 500

# Health check endpoint for testing connection
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "message": "Flask translation server is running",
        "version": "1.0"
    })

# Get available languages endpoint
@app.route('/api/languages', methods=['GET'])
def get_languages():
    languages = [
        {"code": "en", "name": "English", "flag": "🇺🇸"},
        {"code": "es", "name": "Spanish", "flag": "🇪🇸"},
        {"code": "fr", "name": "French", "flag": "🇫🇷"},
        {"code": "de", "name": "German", "flag": "🇩🇪"},
        {"code": "it", "name": "Italian", "flag": "🇮🇹"},
        {"code": "pt", "name": "Portuguese", "flag": "🇧🇷"},
        {"code": "ja", "name": "Japanese", "flag": "🇯🇵"},
        {"code": "ko", "name": "Korean", "flag": "🇰🇷"},
        {"code": "zh", "name": "Chinese", "flag": "🇨🇳"},
        {"code": "ar", "name": "Arabic", "flag": "🇸🇦"},
        {"code": "hi", "name": "Hindi", "flag": "🇮🇳"},
        {"code": "ta", "name": "Tamil", "flag": "🇮🇳"},
        {"code": "bn", "name": "Bengali", "flag": "🇧🇩"},
        {"code": "nl", "name": "Dutch", "flag": "🇳🇱"},
        {"code": "pl", "name": "Polish", "flag": "🇵🇱"},
        {"code": "ru", "name": "Russian", "flag": "🇷🇺"}
    ]
    return jsonify({"languages": languages})

def generate_speech(text, voice_id="en-US-Wavenet-D"):
    """
    Generate speech using Murf API
    """
    try:
        response = client.text_to_speech.synthesize(
            voice_id=voice_id,
            text=text,
            output_format="mp3",
        )
        return response.audio_url
    except Exception as e:
        print(f"Speech synthesis error: {e}")
        return None

def transcribe_audio(file_path):
    """
    Transcribe audio using AssemblyAI API
    """
    try:
        # Upload the audio file to AssemblyAI
        headers = {"authorization": "dbdf9b629dcb4adba4a4cdd12a2ecf51"}
        with open(file_path, "rb") as audio_file:
            upload_response = requests.post(
                "https://api.assemblyai.com/v2/upload",
                headers=headers,
                files={"file": audio_file},
            )
        upload_url = upload_response.json()["upload_url"]

        # Request transcription
        transcription_response = requests.post(
            "https://api.assemblyai.com/v2/transcript",
            headers=headers,
            json={"audio_url": upload_url},
        )
        transcript_id = transcription_response.json()["id"]

        # Poll for transcription completion
        while True:
            status_response = requests.get(
                f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                headers=headers,
            )
            status = status_response.json()["status"]
            if status == "completed":
                return status_response.json()["text"]
            elif status == "failed":
                raise Exception("Transcription failed")
            else:
                import time
                time.sleep(5)  # Wait before polling again
    except Exception as e:
        print(f"Transcription error: {e}")
        return None
    
@app.route('/api/audio', methods=["POST"])
def process_audio():
    """
    Endpoint to process audio and transcribe it using AssemblyAI
    """
    try:
        # Parse JSON data
        data = request.get_json()

        # audio_file = request.files['audio']
        # Extract audio file and target language
        audio_file = request.files.get('audio')
        if not audio_file:
            return jsonify({"error": "No audio file provided", "success": False}), 400
        
        file_path = "temp_audio.wav"
        audio_file.save(file_path)

        # Transcribe the audio using AssemblyAI
        # transcription = transcribe_audio(file_path)
        config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.universal)
        transcript = aai.Transcriber(config=config).transcribe(file_path)

        # if transcription:
        #     return jsonify({"transcription": transcription, "success": True}), 200
        # else:
        #     return jsonify({"error": "Transcription failed", "success": False}), 500

        if transcript.status == "error":
            raise RuntimeError(f"Transcription failed: {transcript.error}")

        transcription = transcript.text

        # Translate the transcription
        target_lang = request.json.get('language', 'en')

        # Map frontend language codes to Murf API language codes
        lang_mapping = {
            'en': 'en-US',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE',
            'it': 'it-IT',
            'pt': 'pt-BR',
            'ja': 'ja-JP',
            'ko': 'ko-KR',
            'zh': 'zh-CN',
            'ar': 'ar-SA',
            'hi': 'hi-IN',
            'ta': 'ta-IN',
            'bn': 'bn-IN',
            'nl': 'nl-NL',
            'pl': 'pl-PL',
            'ru': 'ru-RU'
        }

        # Convert to Murf API format
        murf_target_lang = lang_mapping.get(target_lang, None)

        if not murf_target_lang:
            return jsonify({"error": f"Unsupported language code: {target_lang}", "success": False}), 400


        translated_text = translate_text(transcription, target_lang)

        if not translated_text:
            return jsonify({"error": "Translation failed", "success": False}), 500

        # Generate speech for the translated text
        audio_url = generate_speech(translated_text)

        if not audio_url:
            return jsonify({"error": "Speech synthesis failed", "success": False}), 500

        # Clean up the temporary audio file
        if os.path.exists(file_path):
            os.remove(file_path)

        return jsonify({
            "transcription": transcription,
            "translatedText": translated_text,
            "audioUrl": audio_url,
            "success": True
        }), 200
    except Exception as e:
        print(f"Error processing audio: {e}")
        return jsonify({"error": str(e), "success": False}), 500


if __name__ == "__main__":
    print("Starting Flask Translation Server...")
    print("Backend will be available at: http://localhost:5000")
    print("API endpoint: http://localhost:5000/api/translate")
    app.run(debug=True, host='0.0.0.0', port=5000)
