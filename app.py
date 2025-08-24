from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# Render 会在运行时创建文件，所以我们不需要检查文件是否存在
KEYS_FILE = "keys.txt"
BINDINGS_FILE = "bindings.json"

# 初始化 bindings.json
if not os.path.exists(BINDINGS_FILE):
    with open(BINDINGS_FILE, "w") as f:
        json.dump({}, f)

# --- 辅助函数 (和之前一样) ---
def load_bindings():
    with open(BINDINGS_FILE, "r") as f:
        try: return json.load(f)
        except json.JSONDecodeError: return {}
def save_bindings(data):
    with open(BINDINGS_FILE, "w") as f:
        json.dump(data, f, indent=4)
def get_valid_keys():
    with open(KEYS_FILE, "r") as f:
        return {line.strip() for line in f if line.strip()}

# --- API 路由 (和之前一样) ---
@app.route('/')
def index():
    return "Key System Server is Running on Render!"

@app.route('/verify', methods=['POST'])
def verify_key():
    try:
        data = request.json
        user_key, user_id = data.get('key'), data.get('userid')
        if not user_key or not user_id:
            return jsonify({"success": False, "message": "Missing key or userid."}), 400
        
        valid_keys = get_valid_keys()
        bindings = load_bindings()

        if user_key not in valid_keys:
            return jsonify({"success": False, "message": "卡密无效或不存在 (Invalid Key)"})
        
        if user_key in bindings:
            if str(bindings[user_key]) == str(user_id):
                return jsonify({"success": True, "message": "验证成功，欢迎回来！ (Welcome Back!)"})
            else:
                return jsonify({"success": False, "message": "卡密已被其他用户绑定 (Key already bound)"})
        else:
            bindings[user_key] = str(user_id)
            save_bindings(bindings)
            return jsonify({"success": True, "message": "验证成功，卡密已绑定！ (Success! Key bound)"})
    except Exception as e:
        return jsonify({"success": False, "message": "服务器内部错误 (Server Error)"}), 500
