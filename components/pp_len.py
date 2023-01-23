import hashlib


def get_pp_len(nickname: str) -> int:
    # Create a new sha256 hash object
    sha256 = hashlib.sha256()
    # Update the hash object with the input string
    sha256.update(nickname.encode())
    # Get the hexadecimal representation of the hash
    hashed_nickname = sha256.hexdigest()
    # Convert the hexadecimal string to an integer
    hashed_nickname = int(hashed_nickname, 16)
    # Use the abs() function to make sure the number is positive
    # and the math.fmod() function to get the remainder when
    # dividing by 25
    return abs(hashed_nickname % 25) + 1
