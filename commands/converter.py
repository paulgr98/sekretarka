from components import converters as conv


def convert(method: str, text: str) -> str:
    if method == 's2b':
        return conv.str_to_binary(text)
    elif method == 'b2s':
        return conv.binary_to_str(text)
    elif method == 's2h':
        return conv.str_to_hex(text)
    elif method == 'h2s':
        return conv.hex_to_str(text)
    elif method == 's2b64':
        return conv.str_to_base64(text)
    elif method == 'b642s':
        return conv.base64_to_str(text)
    else:
        return 'Niepoprawna metoda konwersji. Możliwe wartości: s2b, b2s, s2h, h2s, s2b64, b642s'

