import json
import base64
from random import choice, shuffle 


def image2json(image): 
    data = {}
    with open(image, mode='rb') as file:
        image = file.read()
    data['image'] = base64.encodebytes(image).decode('utf-8')
    return data 
