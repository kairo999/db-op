from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# ============================================
# SUPABASE CONFIG (Environment Variables se)
# ============================================
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://kzedjjswtuveudssyzaa.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt6ZWRqanN3dHV2ZXVkc3N5emFhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkwMjM2NTQsImV4cCI6MjA5NDU5OTY1NH0.7iqsEcY6n-hy81CvYqDFnvuIRoLwEZ7oiC6rgfHbzQ0')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ============================================
# UNIVERSAL DATABASE ROUTES
# ============================================

@app.route('/<project>', methods=['GET'])
def get_data(project):
    """GET: Data retrieve karo"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/storage?name=eq.{project}&select=data&limit=1"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        result = resp.json()
        
        if result and len(result) > 0:
            return jsonify(result[0].get('data', {}))
        
        return jsonify({"status": "empty", "message": f"No data for '{project}'"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/<project>', methods=['POST'])
def save_data(project):
    """POST: Jo bhi JSON bhejo - WAHI save hoga"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        record = {
            "name": project,
            "data": data,
            "updated_at": datetime.now().isoformat()
        }
        
        # Check existing
        check_url = f"{SUPABASE_URL}/rest/v1/storage?name=eq.{project}&select=id"
        check = requests.get(check_url, headers=HEADERS, timeout=10)
        existing = check.json()
        
        if existing and len(existing) > 0:
            # UPDATE
            url = f"{SUPABASE_URL}/rest/v1/storage?name=eq.{project}"
            requests.patch(url, headers=HEADERS, json=record, timeout=10)
        else:
            # INSERT
            url = f"{SUPABASE_URL}/rest/v1/storage"
            requests.post(url, headers=HEADERS, json=record, timeout=10)
        
        return jsonify({
            "status": "✅ SAVED PERMANENTLY",
            "project": project,
            "message": "Data saved in Supabase Cloud!"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/<project>', methods=['DELETE'])
def delete_data(project):
    """DELETE: Project delete karo"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/storage?name=eq.{project}"
        requests.delete(url, headers=HEADERS, timeout=10)
        return jsonify({"status": "✅ DELETED", "project": project})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return jsonify({
        "service": "🗄️ BRONX UNIVERSAL SUPABASE API",
        "storage": "Supabase Cloud - PERMANENT",
        "usage": {
            "save": "POST /{project_name}",
            "get": "GET /{project_name}",
            "delete": "DELETE /{project_name}"
        },
        "example": "POST /my-keys → JSON data",
        "credit": "@BRONX_ULTRA"
    })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
