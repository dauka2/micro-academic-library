from flask import Flask, render_template, request, send_from_directory
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "database\\dbdb"
PDF_DIR = "database\\pdf"

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    conn = sqlite3.connect(DB_PATH)
    if not os.path.exists(DB_PATH):
        return "Error: Database file not found at " + DB_PATH
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM publications")
    total = cursor.fetchone()[0]
    pages = (total // per_page) + (1 if total % per_page else 0)
    
    cursor.execute("SELECT * FROM publications LIMIT ? OFFSET ?", (per_page, offset))
    pubs = cursor.fetchall()
    conn.close()
    
    if not pubs:
        return "No publications"
    
    return render_template('index.html', pubs=pubs, page=page, pages=pages)

@app.route('/pdf/<filename>')
def serve_pdf(filename):
    return send_from_directory(PDF_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)