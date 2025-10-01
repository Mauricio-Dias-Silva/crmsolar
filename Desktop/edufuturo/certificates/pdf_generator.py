from weasyprint import HTML
from io import BytesIO

def generate_certificate_pdf(template_path, context):
    """Gera PDF a partir de um template HTML"""
    html = HTML(template_path)
    pdf = html.write_pdf()
    return BytesIO(pdf)