# Offshore Wind Textbook - Content Editor System

This system allows non-technical users to edit the textbook content using simple Markdown syntax, without needing to know HTML.

## System Components

1. **editor.html** - Web-based editor interface with live preview
2. **build.py** - Converts Markdown to HTML while preserving interactive elements
3. **save_content.py** - Contains server API code (both R and Python versions)
4. **content/** - Directory containing Markdown source files
5. **content_backups/** - Automatic backups of all edits

## Features

- **Live Preview**: See changes as you type
- **Simple Markdown**: No HTML knowledge required
- **Preserves Interactivity**: Charts and calculators remain functional
- **Version Control**: Automatic backups of all changes
- **Offline Support**: Falls back to browser storage if server is unavailable

## Deployment on Posit Connect

### Option 1: R Plumber API (Recommended for Posit Connect)

1. **Extract the R API code**:
   ```bash
   python3 save_content.py
   ```
   This creates `save_content_api.R`

2. **Deploy to Posit Connect**:
   ```r
   library(rsconnect)
   deployAPI(
     api = "save_content_api.R",
     appTitle = "Offshore Wind Textbook Editor API",
     appFiles = c("save_content_api.R", "content/", "build.py")
   )
   ```

3. **Update editor.html** with your API URL:
   ```javascript
   const API_BASE = 'https://your-posit-connect.com/content/####';
   ```

### Option 2: Python Flask API

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Flask app**:
   ```bash
   python3 app.py
   ```

3. **Deploy to Posit Connect** as a Python API

## Usage Guide

### For Content Editors

1. **Access the Editor**:
   - Navigate to `editor.html`
   - Select a page from the dropdown

2. **Edit Content**:
   - Use simple Markdown syntax
   - Click formatting buttons for help
   - See live preview on the right

3. **Save Changes**:
   - Click "Save" button
   - Changes are automatically backed up
   - HTML pages are rebuilt automatically

### Markdown Quick Reference

```markdown
# Heading 1
## Heading 2
### Heading 3

**bold text**
*italic text*

- Bullet point
1. Numbered list

[Link text](https://example.com)

`inline code`

```
Code block
```
```

### Special Placeholders

To preserve interactive elements, use these placeholders:

- `[CHART:chartId]` - Preserves a chart
- `[CALCULATOR:calcId]` - Preserves a calculator
- `[INTERACTIVE:elementId]` - Generic interactive element

## File Structure

```
refs/
├── editor.html          # Web editor interface
├── build.py            # Markdown → HTML converter
├── save_content.py     # API generator script
├── content/            # Markdown source files
│   ├── theory.md
│   ├── measurement.md
│   └── ...
├── content_backups/    # Automatic backups
│   └── theory/
│       ├── theory_20240101_120000.md
│       └── ...
└── [existing HTML files preserved]
```

## Security Considerations

1. **Authentication**: Add Posit Connect authentication to the API
2. **Input Validation**: Page names are sanitized
3. **Backup System**: All changes are backed up with timestamps
4. **Access Control**: Configure who can edit via Posit Connect

## Customization

### Adding New Pages

1. Create a new Markdown file in `content/`:
   ```bash
   echo "# New Page" > content/new-page.md
   ```

2. Add to editor dropdown in `editor.html`:
   ```html
   <option value="new-page">New Page</option>
   ```

3. Update `build.py` with page configuration

### Modifying Templates

Edit the `base_template` in `build.py` to change the HTML structure.

## Troubleshooting

### Editor won't load content
- Check browser console for errors
- Verify API endpoint is accessible
- Check file permissions on server

### Changes not appearing
- Ensure `build.py` has execute permissions
- Check Python dependencies are installed
- Verify write permissions on directories

### Interactive elements missing
- Ensure original HTML files are present
- Check chart/calculator IDs match
- Verify JavaScript files are included

## Maintenance

### Regular Backups
```bash
# Backup entire content directory
tar -czf content_backup_$(date +%Y%m%d).tar.gz content/ content_backups/
```

### Clean Old Backups
```bash
# Remove backups older than 30 days
find content_backups -name "*.md" -mtime +30 -delete
```

### Monitor Usage
Check `content_changes.log` for edit history and patterns.

## Support

For issues or questions:
1. Check the browser console for errors
2. Review server logs
3. Verify all dependencies are installed
4. Ensure proper permissions on all directories