import base64
import io
import re
from decimal import Decimal
from urllib.parse import quote


def upi_deep_link(upi_id, amount=None, payee_name=None, note=None):
    """Build a upi:// intent URI that opens the customer's UPI app pre-filled.

    Spec: upi://pay?pa=<vpa>&pn=<name>&am=<amount>&cu=INR&tn=<note>
    """
    if not upi_id:
        return ''
    parts = [f'pa={quote(upi_id, safe="")}']
    if payee_name:
        parts.append(f'pn={quote(payee_name, safe="")}')
    if amount is not None:
        try:
            value = Decimal(str(amount)).quantize(Decimal('0.01'))
        except Exception:
            value = None
        if value is not None and value > 0:
            parts.append(f'am={value}')
    parts.append('cu=INR')
    if note:
        parts.append(f'tn={quote(note, safe="")}')
    return 'upi://pay?' + '&'.join(parts)


def is_valid_upi_id(value):
    """UPI VPA shape: name@bank, name may contain . _ - and digits."""
    if not value:
        return False
    return re.fullmatch(r'[A-Za-z0-9.\-_]{2,256}@[A-Za-z0-9.\-_]{2,64}', value.strip()) is not None


_QR_CACHE = {}
_QR_CACHE_MAX = 64


def upi_qr_data_uri(payload):
    """Return a PNG data-URI QR code encoding a UPI intent URI.

    The amount travels inside the QR itself, so scanning it pre-fills the
    amount in the customer's UPI app. Returns '' if qrcode is unavailable.
    """
    if not payload:
        return ''
    if payload in _QR_CACHE:
        return _QR_CACHE[payload]
    try:
        import qrcode
        from qrcode.constants import ERROR_CORRECT_M
    except ImportError:
        return ''
    try:
        qr = qrcode.QRCode(version=None, error_correction=ERROR_CORRECT_M, box_size=8, border=2)
        qr.add_data(payload)
        qr.make(fit=True)
        image = qr.make_image(fill_color='black', back_color='white')
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        data_uri = 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode('ascii')
    except Exception:
        return ''
    if len(_QR_CACHE) >= _QR_CACHE_MAX:
        _QR_CACHE.clear()
    _QR_CACHE[payload] = data_uri
    return data_uri
