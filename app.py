
# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime
from pathlib import Path
import subprocess

app = Flask(__name__)
CORS(app)  # Enable CORS for editor interface

CONTENT_DIR = Path("content")
BACKUP_DIR = Path("content_backups")

@app.route('/save', methods=['POST'])
def save_content():
    data = request.json
    page = data.get('page', '').strip()
    content = data.get('content', '').strip()
    author = data.get('author', 'anonymous')
    
    if not page or not content:
        return jsonify({
            'success': False,
            'message': 'Page and content are required'
        }), 400
    
    # Sanitize page name
    page = ''.join(c for c in page if c.isalnum() or c == '-')
    
    # Create backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = BACKUP_DIR / page
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    current_file = CONTENT_DIR / f"{page}.md"
    backup_file = None
    
    if current_file.exists():
        backup_file = backup_dir / f"{page}_{timestamp}.md"
        shutil.copy(current_file, backup_file)
    
    # Save new content
    try:
        current_file.write_text(content, encoding='utf-8')
        
        # Log the change
        log_entry = {
            'page': page,
            'timestamp': datetime.now().isoformat(),
            'author': author,
            'size': len(content)
        }
        
        with open('content_changes.log', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Trigger rebuild
        subprocess.Popen(['python3', 'build.py'])
        
        return jsonify({
            'success': True,
            'message': 'Content saved successfully',
            'backup': backup_file.name if backup_file else None
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error saving content: {str(e)}'
        }), 500

@app.route('/content/<page>', methods=['GET'])
def get_content(page):
    page = ''.join(c for c in page if c.isalnum() or c == '-')
    file_path = CONTENT_DIR / f"{page}.md"
    
    if not file_path.exists():
        return jsonify({
            'success': False,
            'message': 'Page not found'
        }), 404
    
    content = file_path.read_text(encoding='utf-8')
    
    return jsonify({
        'success': True,
        'content': content,
        'page': page
    })

@app.route('/pages', methods=['GET'])
def list_pages():
    pages = []
    
    for md_file in CONTENT_DIR.glob('*.md'):
        page_id = md_file.stem
        stat = md_file.stat()
        
        pages.append({
            'id': page_id,
            'name': page_id.replace('-', ' ').title(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'size': stat.st_size
        })
    
    return jsonify({
        'success': True,
        'pages': pages
    })

@app.route('/backups/<page>', methods=['GET'])
def get_backups(page):
    page = ''.join(c for c in page if c.isalnum() or c == '-')
    backup_dir = BACKUP_DIR / page
    
    if not backup_dir.exists():
        return jsonify({
            'success': True,
            'backups': []
        })
    
    backups = []
    for backup_file in backup_dir.glob('*.md'):
        stat = backup_file.stat()
        backups.append({
            'filename': backup_file.name,
            'timestamp': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'size': stat.st_size
        })
    
    return jsonify({
        'success': True,
        'backups': sorted(backups, key=lambda x: x['timestamp'], reverse=True)
    })

if __name__ == '__main__':
    CONTENT_DIR.mkdir(exist_ok=True)
    BACKUP_DIR.mkdir(exist_ok=True)
    app.run(debug=True, port=5000)
