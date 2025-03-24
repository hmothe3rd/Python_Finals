def CountVowels(s):
    vowels = "aeiouAEIOU"
    count = 0
    for char in s:
        if char in vowels:
            count += 1
    return count

def CountConsonants(s):
    consonants = "bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ"
    count = 0
    for char in s:
        if char in consonants:
            count += 1
    return count

def CountNumbers(s):
    count = 0
    for char in s:
        if char.isdigit():
            count += 1
    return count

def main():
    user_input = input("Enter a string: ")

    vowels_count = CountVowels(user_input)
    consonants_count = CountConsonants(user_input)
    numbers_count = CountNumbers(user_input)

    print(f"There are {vowels_count} vowels, {consonants_count} consonants and {numbers_count} numbers in the string.")

if __name__ == "__main__":
    main()
