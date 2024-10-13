from random import random
import math
from langdetect import detect_langs

def gcd(a, b):
    while not a == b:
        if a > b:
            a = a + b
        else:
            b = b - a
    return a

def odd_or_even():
    input_number = input("enter a number:\n")
    number = eval(input_number)
    if number % 2 == 0:
        print("the number is even")
    elif number % 2 == 1:
        print("the number is odd")

def fizzbuzz():
    print(
        ["FizzBuzz" if x % 15 == 0 else "Fizz" if x % 3 == 0 else "Buzz" if x % 5 == 0 else x for x in range(1, 101)]
    )

def estimate_pi(precision):
    points = []
    while True:
        points.append((random(), random()))
        points_in_circle = [(x,y) for x,y in points if (x-0.5)**2 + (y-0.5)**2 < 0.25]
        estimated_pi = 4 * len(points_in_circle) / len(points)
        if abs(math.pi - estimated_pi) < pow(10, -precision):
            return estimated_pi

def break_cipher(text):
    LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ALPHABET_LENGTH = 26
    def shift_letter(letter, n):
        position = LETTERS.find(letter)
        new_position = (position + n) % ALPHABET_LENGTH
        return LETTERS[new_position]
    def shift_string(string, n):
        return "".join([shift_letter(letter, n) for letter in string])

    possible_answers = [shift_string(text, i) for i in range(26)]

    def get_english_likeliness_score(text):
        languages = detect_langs(text)
        score = 1
        for language in languages:
            lang = language.lang
            prob = language.prob
            if lang == "en":
                score = prob
        return score

    result = [(answer, get_english_likeliness_score(answer)) for answer in possible_answers]
    print(result)