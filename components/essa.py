def calculate_essa_level(nickname: str) -> int:
    # Get the number of vowels in the nickname
    num_of_vowels = 0
    for letter in nickname:
        if letter in 'aeiou':
            num_of_vowels += 1

    # Calculate the essa level
    essa_level = (len(nickname) ** 69 + num_of_vowels) % 100
    return essa_level
