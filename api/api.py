# api.py
from flask import Flask, request, jsonify
from services.text_reader import TextReader
from services.image_recognition import ImageRecognitionService
from services.contrast_tester import ContrastTester
from services.voice_assistant import VoiceAssistant
from services.voice_input import get_voice_input, get_level_from_voice, get_command_from_voice
import threading
import os

app = Flask(__name__)  
reader = TextReader()
ocr = ImageRecognitionService()
tester = ContrastTester(window_width=800, window_height=600)
voice_assistant = VoiceAssistant()
voice_assistant.start_listening()

#text_reader
@app.route('/read', methods=['POST'])
def read_text():
    data = request.json
    text = data.get("text", "")
    rate = data.get("rate", 150)

    thread = threading.Thread(target=reader.read_text, args=(text, rate))
    thread.start()

    return jsonify({"status": "reading"})

@app.route('/pause', methods=['POST'])
def pause():
    reader.pause()
    return jsonify({"status": "paused"})

@app.route('/resume', methods=['POST'])
def resume():
    thread = threading.Thread(target=reader.resume)
    thread.start()
    return jsonify({"status": "resumed"})

#ocr
@app.route('/ocr', methods=['POST'])
def ocr_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not ocr.is_supported_format(file.filename):
        return jsonify({"error": "Unsupported file format"}), 400

    file_path = os.path.join("temp_uploads", file.filename)
    os.makedirs("temp_uploads", exist_ok=True)
    file.save(file_path)

    text, confidence, error = ocr.detect_document_with_confidence(file_path)

    os.remove(file_path)

    if error:
        return jsonify({"error": error}), 500

    return jsonify({"text": text, "confidence": round(confidence * 100, 2)})

#contrast testing
@app.route('/contrast/start', methods = ['POST'])
def start_contrast_test():
    try:
        tester.start_test()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    bg, text, name = tester.get_current_contrast()
    return jsonify({
        "text": tester.current_text,
        "bg": bg,
        "text_color": text,
        "name": name
    })

@app.route('/contrast/feedback', methods=['POST'])
def provide_feedback():
    data = request.json
    rating = data.get('rating')
    if rating not in [1, 2, 3]:
        return jsonify({"error": "Rating must be 1 (low) to 3 (high)"}), 400

    tester.record_feedback(rating)
    if tester.next_contrast():
        bg, text, name = tester.get_current_contrast()
        return jsonify({
            "text": tester.current_text,
            "bg": bg,
            "text_color": text,
            "name": name
        })
    else:
        summary = tester.get_results_summary()
        return jsonify(summary)

#voice assistant
@app.route("/voice/command", methods=["GET"])
def get_voice_command():
    command = voice_assistant.get_command()
    return jsonify({"command": command}) 

@app.route("/voice/help", methods=["POST"])
def voice_help():
    voice_assistant.provide_help()
    return jsonify({"status": "help spoken"})

#voice input
@app.route('/api/voice', methods=['GET'])
def voice_command():
    voice_text = get_voice_input()
    if not voice_text:
        return jsonify({"error": "Could not recognize any voice input"}), 400

    level = get_level_from_voice(voice_text)
    command = get_command_from_voice(voice_text)

    return jsonify({
        "recognized_text": voice_text,
        "level": level,
        "command": command
    })

if __name__ == '__main__':
    app.run(debug=True)
