import json
from googleapiclient.discovery import build
import urllib.request
from urllib.error import HTTPError
import logging
from multiprocessing import Pool
from p_tqdm import p_map
from itertools import repeat

dataJSON = json.load(open('data.json'))
imageQuery = 'oranges on table'
#Rounds down to the nearest 10s
numberOfImages = 20
logging.basicConfig(filename='main.log', encoding='utf-8', level=logging.INFO)
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

# Saves images into a folder named images; if it fails, logs url
def saveImage(imageData: dict, imageName: str):
    try:
        #Need to change to work with proxies
        urllib.request.urlretrieve(imageData['link'], f'images/{imageName}.jpg')
        logging.info(f'Saved image{i}: {imageData["link"]}')
    except HTTPError as e:
        logging.error(f'Failed to save image: {imageData["link"]}')

# Puts image data from Google Search into an Array
def getImagesData(query: str, numberOfImages: int, pageNumber: int):
    logging.info(f'Getting image links of Query: {query}\nNumber of Images: {numberOfImages}\nPage Number: {pageNumber}')
    service = build("customsearch", 'v1', developerKey=dataJSON['customSearchAPI'])
    allResponses = []
    
    response = service.cse().list(
        q=query,
        cx=dataJSON['searchEngineID'],
        searchType='image',
        num=numberOfImages,
        imgType='photo',
        safe= 'off',
        start=pageNumber
    ).execute()
    allResponses.extend(response.get('items'))

    if not allResponses:
        return None
    else:
        return allResponses



# Implements multiprocessing to save images
if __name__ == "__main__":
    print(f"Getting images of {imageQuery}")
    pageNumbers = []
    for i in range((numberOfImages//10)):
        pageNumbers.append(i+1)
    imageNames = []
    for i in range(numberOfImages):
        imageNames.append(f'image{i+1}')

    with Pool(6) as p:
        imageData = p.starmap(getImagesData, zip(repeat(imageQuery), repeat(10), pageNumbers))
        allImageData = []
        for images in imageData:
            allImageData.extend(images)
        p.starmap(saveImage, zip(allImageData, imageNames))

    print("Finished Saving all Images")

