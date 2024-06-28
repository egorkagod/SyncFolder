import os
import json
import requests

def f(a, b):
    print('Удали', (b - a))
    print('Добавь', (a - b))

a = {1, 3}
b = {1, 2}
f(a, b)