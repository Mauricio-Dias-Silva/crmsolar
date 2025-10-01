import qrcode
from io import BytesIO
from django.core.files import File

def generate_qr_code(url):
    """Gera um QR Code a partir de uma URL e retorna um arquivo"""
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    filename = 'qrcode.png'
    file = File(buffer, name=filename)
    return file, filename