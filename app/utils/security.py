import re

def validar_ci(ci):
    # Valida que CI sea numérico con 4 o más dígitos
    return re.match(r'^\d{4,}$', ci) is not None

def validar_password(password):
    # Al menos 6 caracteres
    return len(password) >= 6
