#!/usr/bin/env python3
"""
Build script to convert Markdown content to HTML pages
Preserves interactive elements like charts and calculators
"""

import os
import re
import json
import yaml
import markdown
from datetime import datetime
from pathlib import Path

# Configuration
CONTENT_DIR = Path("content")
TEMPLATE_DIR = Path("templates")
OUTPUT_DIR = Path(".")  # Current directory where HTML files are

class OffshoreWindBuilder:
    def __init__(self):
        self.md = markdown.Markdown(extensions=[
            'extra',        # Tables, footnotes, etc.
            'codehilite',   # Code syntax highlighting
            'toc',          # Table of contents
            'meta',         # Metadata support
        ])
        
        # Load templates
        self.templates = self.load_templates()
        
        # Interactive elements to preserve
        self.interactive_elements = self.load_interactive_elements()
    
    def load_templates(self):
        """Load HTML templates for each page type"""
        templates = {}
        
        # Base template
        base_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Offshore Wind Analysis Textbook</title>
    <link rel="stylesheet" href="styles.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    {extra_head}
</head>
<body>
    <nav class="nav-main">
        <a href="index.html"{index_active}>Home</a>
        <a href="theory.html"{theory_active}>Theory</a>
        <a href="measurement.html"{measurement_active}>Measurements</a>
        <a href="modeling.html"{modeling_active}>Modeling</a>
        <a href="data-processing.html"{data_active}>Data Processing</a>
        <a href="case-studies.html"{case_active}>Case Studies</a>
        <a href="advanced-topics.html"{advanced_active}>Advanced Topics</a>
        <a href="calculators.html"{calc_active}>Calculators</a>
        <a href="exercises.html"{exercises_active}>Exercises</a>
        <a href="formulas.html"{formulas_active}>Formulas</a>
        <a href="glossary.html"{glossary_active}>Glossary</a>
        <a href="references.html"{references_active}>References</a>
        <a href="datasets.html"{datasets_active}>Datasets</a>
    </nav>

    <div class="header">
        <h1>{header_icon} {header_title}</h1>
        <p>{header_subtitle}</p>
    </div>

    {extra_nav}

    <div class="container">
        {content}
    </div>

    <footer class="footer">
        <p>© 2024 Offshore Wind Analysis Textbook | {page_name}</p>
        {footer_nav}
    </footer>

    {scripts}
</body>
</html>"""
        
        templates['base'] = base_template
        return templates
    
    def load_interactive_elements(self):
        """Load configuration for interactive elements that need to be preserved"""
        return {
            'charts': {
                'pattern': r'<canvas\s+id="([^"]+)"[^>]*></canvas>',
                'preserve': True
            },
            'calculators': {
                'pattern': r'<div\s+class="calculator-section"[^>]*>.*?</div>',
                'preserve': True,
                'multiline': True
            },
            'scripts': {
                'pattern': r'<script[^>]*>.*?</script>',
                'preserve': True,
                'multiline': True
            }
        }
    
    def extract_metadata(self, md_content):
        """Extract YAML frontmatter from markdown content"""
        if md_content.startswith('---'):
            try:
                _, frontmatter, content = md_content.split('---', 2)
                metadata = yaml.safe_load(frontmatter)
                return metadata, content.strip()
            except:
                pass
        return {}, md_content
    
    def preserve_interactive_elements(self, html_content, original_html_path):
        """Preserve interactive elements from original HTML"""
        if not original_html_path.exists():
            return html_content
        
        try:
            with open(original_html_path, 'r', encoding='utf-8') as f:
                original_html = f.read()
            
            # Extract all canvas elements
            canvas_pattern = r'<canvas\s+id="([^"]+)"[^>]*></canvas>'
            canvases = re.findall(canvas_pattern, original_html)
            
            # Extract calculator sections
            calc_pattern = r'<div\s+class="calculator-section"[^>]*>.*?</div>(?:\s*</div>)*'
            calculators = re.findall(calc_pattern, original_html, re.DOTALL)
            
            # Extract script sections (for Chart.js initialization)
            script_pattern = r'<script>\s*// Chart\.js visualizations.*?</script>'
            scripts = re.findall(script_pattern, original_html, re.DOTALL)
            
            # Add placeholders in markdown-generated HTML
            # These will be replaced with actual interactive elements
            for canvas_id in canvases:
                placeholder = f'[CHART:{canvas_id}]'
                if placeholder in html_content:
                    html_content = html_content.replace(
                        placeholder, 
                        f'<canvas id="{canvas_id}"></canvas>'
                    )
            
            # Add scripts at the end if they exist
            if scripts:
                script_section = '\n'.join(scripts)
                html_content = html_content.replace('</body>', f'{script_section}\n</body>')
            
        except Exception as e:
            print(f"Warning: Could not preserve interactive elements: {e}")
        
        return html_content
    
    def build_page(self, page_name, md_path):
        """Build a single HTML page from markdown"""
        # Read markdown content
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Extract metadata
        metadata, content = self.extract_metadata(md_content)
        
        # Convert markdown to HTML
        html_content = self.md.convert(content)
        
        # Get page configuration
        page_config = self.get_page_config(page_name, metadata)
        
        # Build final HTML
        template = self.templates['base']
        
        # Set active nav item
        nav_items = ['index', 'theory', 'measurement', 'modeling', 'data', 
                     'case', 'advanced', 'calc', 'exercises', 'formulas', 
                     'glossary', 'references', 'datasets']
        
        nav_active = {f"{item}_active": "" for item in nav_items}
        if page_name in nav_active:
            nav_active[f"{page_name}_active"] = ' class="active"'
        
        # Fill template
        html = template.format(
            title=page_config['title'],
            extra_head=page_config.get('extra_head', ''),
            header_icon=page_config.get('icon', '📚'),
            header_title=page_config['header_title'],
            header_subtitle=page_config.get('subtitle', ''),
            extra_nav=page_config.get('extra_nav', ''),
            content=html_content,
            page_name=page_config['title'],
            footer_nav=self.get_footer_nav(page_name),
            scripts=page_config.get('scripts', ''),
            **nav_active
        )
        
        # Preserve interactive elements from original
        output_path = OUTPUT_DIR / f"{page_name}.html"
        html = self.preserve_interactive_elements(html, output_path)
        
        return html
    
    def get_page_config(self, page_name, metadata):
        """Get configuration for specific page"""
        configs = {
            'theory': {
                'title': 'Theory',
                'header_title': 'Theoretical Foundations',
                'icon': '🌬️',
                'subtitle': 'Understanding Wind Physics and Atmospheric Dynamics'
            },
            'measurement': {
                'title': 'Measurements',
                'header_title': 'Measurement Techniques & Instrumentation',
                'icon': '📡',
                'subtitle': 'Comprehensive Guide to Offshore Wind Measurements'
            },
            'modeling': {
                'title': 'Modeling',
                'header_title': 'Numerical Modeling & Simulations',
                'icon': '🌊',
                'subtitle': 'From Mesoscale to Microscale Wind Modeling'
            },
            # Add more page configs...
        }
        
        config = configs.get(page_name, {
            'title': page_name.title(),
            'header_title': page_name.replace('-', ' ').title(),
            'icon': '📄'
        })
        
        # Override with metadata if provided
        config.update(metadata)
        
        return config
    
    def get_footer_nav(self, current_page):
        """Generate footer navigation"""
        pages = [
            ('index', 'Home'),
            ('theory', 'Theory'),
            ('measurement', 'Measurements'),
            ('modeling', 'Modeling'),
            ('data-processing', 'Data Processing'),
            ('case-studies', 'Case Studies'),
            ('advanced-topics', 'Advanced Topics')
        ]
        
        current_idx = next((i for i, (name, _) in enumerate(pages) if name == current_page), -1)
        
        nav_parts = []
        if current_idx > 0:
            prev_page, prev_title = pages[current_idx - 1]
            nav_parts.append(f'<a href="{prev_page}.html">← Previous: {prev_title}</a>')
        
        if current_idx < len(pages) - 1 and current_idx >= 0:
            next_page, next_title = pages[current_idx + 1]
            nav_parts.append(f'<a href="{next_page}.html">Next: {next_title} →</a>')
        
        return '<p>' + ' | '.join(nav_parts) + '</p>' if nav_parts else ''
    
    def build_all(self):
        """Build all pages from markdown sources"""
        # Ensure content directory exists
        CONTENT_DIR.mkdir(exist_ok=True)
        
        # Build each markdown file
        built_pages = []
        for md_file in CONTENT_DIR.glob('*.md'):
            page_name = md_file.stem
            print(f"Building {page_name}...")
            
            try:
                html = self.build_page(page_name, md_file)
                output_path = OUTPUT_DIR / f"{page_name}.html"
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                
                built_pages.append(page_name)
                print(f"  ✓ Built {output_path}")
            except Exception as e:
                print(f"  ✗ Error building {page_name}: {e}")
        
        print(f"\nBuild complete! Built {len(built_pages)} pages.")
        print(f"Last build: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Save build info
        build_info = {
            'timestamp': datetime.now().isoformat(),
            'pages': built_pages,
            'status': 'success'
        }
        
        with open('.build_info.json', 'w') as f:
            json.dump(build_info, f, indent=2)


def main():
    """Main build function"""
    builder = OffshoreWindBuilder()
    builder.build_all()


if __name__ == '__main__':
    main()