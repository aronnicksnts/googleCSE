import json
import math
from googleapiclient.discovery import build
import urllib.request
from urllib.error import HTTPError
import logging

dataJSON = json.load(open('data.json'))

# Saves images into a folder named images; if it fails, logs url
def saveImage(url: str, imageName: str):
    try:
        #Need to change to work with proxies
        urllib.request.urlretrieve(url, f'images/{imageName}.jpg')
    except HTTPError as e:
        logging.error(f'Failed to save image: {url}')

# Puts image data from Google Search into an Array
def getImagesData(query: str, totalNumImages: int):
    totalNumImages = math.ceil(totalNumImages//10)
    service = build("customsearch", 'v1', developerKey=dataJSON['customSearchAPI'])
    allResponses = []

    for i in range(totalNumImages):
        response = service.cse().list(
            q=query,
            cx=dataJSON['searchEngineID'],
            searchType='image',
            num=10,
            imgType='photo',
            safe= 'off',
            start=10*i+1
        ).execute()
        allResponses.extend(response.get('items'))

    if not allResponses:
        return None
    else:
        return allResponses

imageData = getImagesData("mangoes on table", 20)
logging.basicConfig(filename='main.log', encoding='utf-8', level=logging.DEBUG)
for i, image in enumerate(imageData):
    logging.info(f'Saving image{i}: {image["link"]}')
    saveImage(image['link'], f'image{i}')
