import base64


def str_to_binary(string: str) -> str:
    binary_string = ' '.join(format(ord(c), '08b') for c in string)
    return binary_string


def binary_to_str(binary_string: str) -> str:
    binary_string = binary_string.replace(' ', '')
    utf8_string = ''.join(chr(int(binary_string[i:i + 8], 2)) for i in range(0, len(binary_string), 8))
    return utf8_string


def str_to_hex(string: str) -> str:
    return ''.join(format(ord(i), 'x') for i in string)


def hex_to_str(hex_str: str) -> str:
    return ''.join(chr(int(hex_str[i:i + 2], 16)) for i in range(0, len(hex_str), 2))


def str_to_base64(string: str) -> str:
    return base64.b64encode(string.encode('utf-8')).decode('utf-8')


def base64_to_str(base64_str: str) -> str:
    return base64.b64decode(base64_str).decode('utf-8')
