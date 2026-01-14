#!/usr/bin/env python3
"""
Generate PDF reports from markdown files using markdown2 and weasyprint
"""

import os
from pathlib import Path
import src.env as env
from src.common.arg_parser import parse_args

try:
    import markdown2
    from weasyprint import HTML, CSS
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError:
    print("❌ Required packages not installed.")
    print("   Install them with: pip install markdown2 weasyprint jinja2")
    exit(1)

template = Environment(
    loader=FileSystemLoader(str(Path(__file__).parent)),
    autoescape=select_autoescape(['html', 'xml'])
).get_template('report_template.html.j2')
    
def generate_pdf_from_markdown(markdown_file, account_id, output_dir="outputs"):
    """
    Generate PDF from markdown file using markdown2 and weasyprint
    
    Args:
        markdown_file: Path to markdown file
        output_dir: Directory to save PDF files
    """
    markdown_path = Path(markdown_file)
    
    if not markdown_path.exists():
        print(f"❌ Markdown file not found: {markdown_file}")
        return None
    
    # Create output directory
    pdf_dir = Path(output_dir) / os.environ.get('AWS_ACCOUNT_ID') / os.environ.get('REPORTING_DATE')
    pdf_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate PDF filename
    pdf_filename = os.environ.get('AWS_ACCOUNT_ID') + '_' + os.environ.get('REPORTING_DATE') + ".pdf"
    pdf_path = pdf_dir / pdf_filename
    
    print(f"📄 Converting {markdown_path.name} to PDF...")
    
    # Read markdown content
    with open(markdown_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Split content into cover page and main content using a unique marker
    cover_page_content = ""
    main_content = markdown_content
    if "<!--COVERPAGEBREAK-->" in markdown_content:
        parts = markdown_content.split("<!--COVERPAGEBREAK-->", 1)
        cover_page_content = parts[0]
        main_content = parts[1] if len(parts) > 1 else ""
    elif "\\pagebreak" in markdown_content:
        parts = markdown_content.split("\\pagebreak", 1)
        cover_page_content = parts[0]
        main_content = parts[1] if len(parts) > 1 else ""
    elif "# AWS Security Hub - Comprehensive" in markdown_content:
        parts = markdown_content.split("# AWS Security Hub - Comprehensive", 1)
        cover_page_content = parts[0]
        main_content = "# AWS Security Hub - Comprehensive" + (parts[1] if len(parts) > 1 else "")
    
    # Convert cover page to HTML (no TOC)
    cover_html = ""
    if cover_page_content.strip():
        cover_html = str(markdown2.markdown(
            cover_page_content,
            extras=['tables', 'fenced-code-blocks']
        ))
    
    # Convert main content to HTML with table of contents support
    html_content = markdown2.markdown(
        main_content,
        extras=['tables', 'fenced-code-blocks', 'header-ids', 'metadata', 'toc']
    )
    
    # Extract TOC and add page breaks before major sections
    toc_html = html_content.toc_html if hasattr(html_content, 'toc_html') else ""
    
    html_body = str(html_content)
    
    
    ## read report_style.css
    css_path = Path("src/to_pdf") / "report_style.css"
    css = ""
    print(css_path)
    if css_path.exists():
        with open(css_path, 'r') as css_file:
            css = css_file.read()
    html_template = template.render(
        title="AWS Security Hub Compliance Report",
        cover_html=cover_html,
        toc_html=toc_html,
        html_body=html_body,
        css=css
    )
    ## write html to temp file
    with open(pdf_dir / (markdown_path.stem + ".html"), 'w', encoding='utf-8') as f:
        f.write(html_template)

    # Generate PDF
    try:
        HTML(string=html_template).write_pdf(pdf_path)
        return str(pdf_path)
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        return None



if __name__ == "__main__":
    args = parse_args()
    
    # Load environment
    print(f"📄 Loading environment from: {args.env_file}\n")
    env.load_environment_variables(args.env_file)  
    profile = os.getenv('AWS_PROFILE')
    region_name = os.getenv('AWS_REGION')
    account_id = os.getenv('AWS_ACCOUNT_ID')
    
    markdown_dir = Path("markdown") / account_id
    if not markdown_dir.exists():
        print("❌ Markdown directory not found.")
        exit(1)
    # Find all comprehensive reports
    report_files = list(markdown_dir.glob("report.md"))
    
    if not report_files:
        print("❌ No comprehensive reports found.")
        exit(1)
    print(f"🚀 Generating PDFs for {len(report_files)} reports...\n")
    generated = []
    for report_file in sorted(report_files):
        pdf_path = generate_pdf_from_markdown(report_file)
        if pdf_path:
            generated.append(pdf_path)
        print()
    
    if generated:
        print(f"\n{'='*80}")
        print(f"✅ Generated {len(generated)} PDF reports")
        print(f"{'='*80}")
        for pdf in generated:
            print(f"📄 {pdf}")
    else:
        print("\n⚠️  No PDFs were generated. Make sure pandoc is installed.")

