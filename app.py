from flask import Flask, jsonify, request
from flask_cors import CORS
from googletrans import Translator

app = Flask(__name__)
CORS(app)  # Cho phép cross-origin requests

translator = Translator()

users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
    {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
]

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(users)

@app.route('/api/translate', methods=['GET'])
def translate_text():
    text = request.args.get('text', '')
    src = request.args.get('src', 'en')
    dest = request.args.get('dest', 'vi')
    
    if not text:
        return jsonify({"error": "Missing 'text' parameter!"}), 400
    
    try:
        result = translator.translate(text, src=src, dest=dest)
        return jsonify({
            "original": text,
            "translated": result.text,
            "src_lang": result.src,
            "dest_lang": dest
        })
    except Exception as e:
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)