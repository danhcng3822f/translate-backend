from flask import Flask, jsonify, request
from flask_cors import CORS
from googletrans import Translator
import json
import os

app = Flask(__name__)
CORS(app)

translator = Translator()

# Load từ điển từ file JSON
def load_vocabulary():
    if os.path.exists('vocabulary.json'):
        with open('vocabulary.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}  # Nếu file chưa có, trả dict rỗng

vocab_dict = load_vocabulary()  # Load lúc start

# Dữ liệu mẫu JSON cũ (giữ nguyên)
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
    text = request.args.get('text', '').strip().lower()  # Lowercase để tra dict
    src = request.args.get('src', 'en')
    dest = request.args.get('dest', 'vi')
    
    if not text:
        return jsonify({"error": "Missing 'text' parameter!"}), 400
    
    # Ưu tiên tra từ điển (cho cả từ đơn và cụm từ, lowercase)
    if text in vocab_dict:
        translated = vocab_dict[text]
        return jsonify({
            "original": text,
            "translated": translated,
            "src_lang": src,
            "dest_lang": dest,
            "source": "vocabulary"  # Đánh dấu nguồn từ dict
        })
    
    # Fallback Google Translate
    try:
        result = translator.translate(text, src=src, dest=dest)
        translated_lower = result.text.lower()
        
        # Kiểm tra lặp từ: Nếu dịch giống nguyên bản (lowercase), báo lỗi
        if translated_lower == text:
            return jsonify({
                "error": "Sai từ vựng hoặc nó là tên riêng"
            }), 400
        
        return jsonify({
            "original": text,
            "translated": result.text,
            "src_lang": result.src,
            "dest_lang": dest,
            "source": "google_translate"  # Đánh dấu nguồn
        })
    except Exception as e:
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500

# Endpoint mới: Add/Update từ vựng (POST)
@app.route('/api/vocab/add', methods=['POST'])
def add_vocabulary():
    data = request.json
    if not data or 'english' not in data or 'vietnamese' not in data:
        return jsonify({"error": "Missing 'english' or 'vietnamese' in JSON body!"}), 400
    
    english = data['english'].strip().lower()
    vietnamese = data['vietnamese'].strip()
    
    # Update dict
    vocab_dict[english] = vietnamese
    
    # Save lại file JSON
    with open('vocabulary.json', 'w', encoding='utf-8') as f:
        json.dump(vocab_dict, f, ensure_ascii=False, indent=2)
    
    return jsonify({
        "message": f"Added/Updated '{english}' -> '{vietnamese}'",
        "total_words": len(vocab_dict)
    }), 200

# Endpoint GET để xem từ điển (tùy chọn)
@app.route('/api/vocab', methods=['GET'])
def get_vocabulary():
    return jsonify(vocab_dict)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)