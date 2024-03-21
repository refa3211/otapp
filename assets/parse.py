import re
from datetime import date

today = date.today()

def parse_otpauth_uri(uri):
    match = re.match(r'otpauth://totp/([^?]+)\?secret=([A-Z0-9]+)', uri)
    simple_secret_match = re.match(r'otpauth://totp/[^:]+:([^?]+)\?secret=([A-Z0-9]+)', uri)
    secret_match = re.match(r'([A-Z0-9]+)', uri)
    another = re.match(r'^otpauth://totp/(?P<account_name>[^?]+)\?digits=(?P<digits>\d+)&secret=(?P<secret>[^&]+)&algorithm=(?P<algorithm>[^&]+)&issuer=(?P<issuer>[^&]+)&period=(?P<period>\d+)$', uri)

    if match:
        name = match.group(1)
        secret = match.group(2)
        return name, secret
    elif secret_match:
        name = f"Default- {today.strftime('%d/%m/%Y')}"
        secret = secret_match.group(1)
        return name, secret
    elif simple_secret_match:
        name = simple_secret_match.group(1)
        secret = simple_secret_match.group(2)
        return name, secret
    elif another:
        name = another.group('account_name')
        secret = another.group('secret')
        return name, secret
    else:
        raise ValueError("Invalid otpauth URI format")
