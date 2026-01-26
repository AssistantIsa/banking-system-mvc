from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "¡Banking API Funcionando!", "status": "online"})

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "service": "banking-api"})

if __name__ == "__main__":
    print("Starting banking API on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=True)
