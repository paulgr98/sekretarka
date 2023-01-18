from components import converters as conv


def convert(method: str, text: str) -> str:
    match method:
        case 's2b':
            return conv.str_to_binary(text)
        case 'b2s':
            return conv.binary_to_str(text)
        case 's2h':
            return conv.str_to_hex(text)
        case 'h2s':
            return conv.hex_to_str(text)
        case 's2b64':
            return conv.str_to_base64(text)
        case 'b642s':
            return conv.base64_to_str(text)
        case _:
            return 'Niepoprawna metoda konwersji. Możliwe wartości: s2b, b2s, s2h, h2s, s2b64, b642s'
