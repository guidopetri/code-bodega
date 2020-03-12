#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


def factorial(number):
    """calculates factorial recursively"""
    if number == 0:
        return 1
    else:
        return number * factorial(number - 1)


while True:
    user_input = input('what number would you like the factorial for?\n')
    try:
        inp = int(user_input)
        print(f'result is {factorial(inp):.2g}\n')
        break
    except ValueError:
        print('user input not valid')
