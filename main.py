import json
import math
from googleapiclient.discovery import build
import urllib.request
from urllib.error import HTTPError

dataJSON = json.load(open('data.json'))

# Saves images into a folder named images; if it fails, returns the image link
def saveImage(url: str, imageName: str):
    try:
        #Need to change to work with proxies
        urllib.request.urlretrieve(url, f'images/{imageName}.jpg')
    except HTTPError as e:
        print(f'Failed to scrape: {url}')
        return url

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

# imageData = getImagesData("Garbage Dump", 20)

# for i, image in enumerate(imageData):
#     saveImage(image['link'], f'image{i}')