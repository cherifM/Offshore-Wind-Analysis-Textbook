#!/usr/bin/env python3
"""
Server endpoint for saving edited content
Can be deployed as a Plumber API in R or Flask app in Python
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
import hashlib
import subprocess

# For R Plumber API version
R_PLUMBER_API = """
# save_content_api.R
# Plumber API for content editing

library(plumber)
library(jsonlite)

# Configuration
CONTENT_DIR <- "content"
BACKUP_DIR <- "content_backups"

#* @apiTitle Offshore Wind Textbook Content Editor API
#* @apiDescription API for saving and managing textbook content

#* Save content for a specific page
#* @param page The page identifier (e.g., "theory", "measurement")
#* @param content The markdown content
#* @param author The author making the change (optional)
#* @post /save
function(req, page = "", content = "", author = "anonymous") {
    # Validate inputs
    if (page == "" || content == "") {
        res$status <- 400
        return(list(
            success = FALSE,
            message = "Page and content are required"
        ))
    }
    
    # Sanitize page name
    page <- gsub("[^a-zA-Z0-9-]", "", page)
    
    # Create backup
    timestamp <- format(Sys.time(), "%Y%m%d_%H%M%S")
    backup_dir <- file.path(BACKUP_DIR, page)
    dir.create(backup_dir, recursive = TRUE, showWarnings = FALSE)
    
    current_file <- file.path(CONTENT_DIR, paste0(page, ".md"))
    if (file.exists(current_file)) {
        backup_file <- file.path(backup_dir, paste0(page, "_", timestamp, ".md"))
        file.copy(current_file, backup_file)
    }
    
    # Save new content
    tryCatch({
        writeLines(content, current_file)
        
        # Log the change
        log_entry <- list(
            page = page,
            timestamp = Sys.time(),
            author = author,
            size = nchar(content)
        )
        
        log_file <- "content_changes.log"
        write(toJSON(log_entry, auto_unbox = TRUE), 
              file = log_file, append = TRUE)
        
        # Trigger rebuild
        system("python3 build.py", intern = FALSE, wait = FALSE)
        
        return(list(
            success = TRUE,
            message = "Content saved successfully",
            backup = basename(backup_file)
        ))
    }, error = function(e) {
        res$status <- 500
        return(list(
            success = FALSE,
            message = paste("Error saving content:", e$message)
        ))
    })
}

#* Get content for a specific page
#* @param page The page identifier
#* @get /content
function(page = "") {
    if (page == "") {
        res$status <- 400
        return(list(
            success = FALSE,
            message = "Page parameter is required"
        ))
    }
    
    page <- gsub("[^a-zA-Z0-9-]", "", page)
    file_path <- file.path(CONTENT_DIR, paste0(page, ".md"))
    
    if (!file.exists(file_path)) {
        res$status <- 404
        return(list(
            success = FALSE,
            message = "Page not found"
        ))
    }
    
    content <- paste(readLines(file_path), collapse = "\n")
    
    return(list(
        success = TRUE,
        content = content,
        page = page
    ))
}

#* List available pages
#* @get /pages
function() {
    files <- list.files(CONTENT_DIR, pattern = "\\.md$", full.names = FALSE)
    pages <- gsub("\\.md$", "", files)
    
    page_info <- lapply(pages, function(p) {
        file_path <- file.path(CONTENT_DIR, paste0(p, ".md"))
        list(
            id = p,
            name = gsub("-", " ", p),
            modified = file.info(file_path)$mtime,
            size = file.info(file_path)$size
        )
    })
    
    return(list(
        success = TRUE,
        pages = page_info
    ))
}

#* Get backup history for a page
#* @param page The page identifier
#* @get /backups
function(page = "") {
    if (page == "") {
        res$status <- 400
        return(list(
            success = FALSE,
            message = "Page parameter is required"
        ))
    }
    
    page <- gsub("[^a-zA-Z0-9-]", "", page)
    backup_dir <- file.path(BACKUP_DIR, page)
    
    if (!dir.exists(backup_dir)) {
        return(list(
            success = TRUE,
            backups = list()
        ))
    }
    
    backup_files <- list.files(backup_dir, full.names = TRUE)
    backups <- lapply(backup_files, function(f) {
        list(
            filename = basename(f),
            timestamp = file.info(f)$mtime,
            size = file.info(f)$size
        )
    })
    
    return(list(
        success = TRUE,
        backups = backups
    ))
}
"""

# Python Flask version
PYTHON_FLASK_API = """
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
            f.write(json.dumps(log_entry) + '\\n')
        
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
"""

# Save both versions
def save_api_files():
    # Save R Plumber API
    with open('save_content_api.R', 'w') as f:
        f.write(R_PLUMBER_API)
    
    # Save Python Flask API
    with open('app.py', 'w') as f:
        f.write(PYTHON_FLASK_API)
    
    # Create run script for R
    with open('run_r_api.R', 'w') as f:
        f.write("""
library(plumber)
pr <- plumb("save_content_api.R")
pr$run(port = 8000, host = "0.0.0.0")
""")
    
    # Create requirements.txt for Python
    with open('requirements.txt', 'w') as f:
        f.write("""flask==2.3.2
flask-cors==4.0.0
markdown==3.4.3
pyyaml==6.0
""")
    
    print("API files created:")
    print("  - save_content_api.R (R Plumber version)")
    print("  - app.py (Python Flask version)")
    print("  - run_r_api.R (R startup script)")
    print("  - requirements.txt (Python dependencies)")

if __name__ == '__main__':
    save_api_files()