import sys
import os
# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from services.text_reader import TextReader
from services.image_recognition import detect_document
from services.contrast_tester import ContrastTester
import google.generativeai as genai

app = Flask(__name__)

# Initialize services
text_reader = TextReader()
contrast_tester = ContrastTester(800, 600)
API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=API_KEY)

@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    try:
        data = request.json
        text = data.get('text')
        speed = data.get('speed', 150)
        text_reader.read_text(text, speed)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/check-accuracy', methods=['POST'])
def check_accuracy():
    try:
        data = request.json
        user_input = data.get('user_input')
        expected_text = data.get('expected_text')
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = f"""You are a JSON-only response API. Analyze these texts and respond with ONLY valid JSON:
        Expected: "{expected_text}"
        Got: "{user_input}"
        Format: {{"is_correct": boolean, "feedback": "analysis"}}"""
        
        response = model.generate_content(prompt)
        return jsonify({"status": "success", "result": response.text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/process-image', methods=['POST'])
def process_image():
    try:
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file provided"}), 400
            
        file = request.files['file']
        extracted_text = detect_document(file.read())
        return jsonify({"status": "success", "text": extracted_text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/contrast-test/start', methods=['POST'])
def start_contrast_test():
    try:
        contrast_tester.start_test()
        return jsonify({
            "status": "success",
            "current_contrast": contrast_tester.get_current_contrast()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/contrast-test/feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.json
        rating = data.get('rating')
        contrast_tester.record_feedback(rating)
        
        if contrast_tester.feedback_provided():
            has_next = contrast_tester.next_contrast()
            if not has_next:
                results = contrast_tester.get_results_summary()
                return jsonify({
                    "status": "complete",
                    "results": results
                })
        
        return jsonify({
            "status": "success",
            "next_contrast": contrast_tester.get_current_contrast()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)