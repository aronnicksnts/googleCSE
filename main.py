import json
from googleapiclient.discovery import build
import urllib.request
from urllib.error import HTTPError
from googleapiclient.errors import HttpError
import logging
from multiprocessing import Pool
from itertools import repeat
import pandas as pd
from datetime import datetime
from os import mkdir

dataJSON = json.load(open('data.json'))

# The prompt that the code will use
imageQuery = dataJSON['imageQuery']

# Rounds down to the nearest 10s
numberOfImages = dataJSON['numberOfImages'] - dataJSON['numberOfImages']%10

# Time for CSV and logs and folder that the images would be stored in
currTime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

# Initialize logger
logging.basicConfig(filename=f'logs/{currTime}.log', encoding='utf-8', level=logging.INFO)
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

# Saves images into a folder named images/{time}; if it fails, logs url and returns the url link
def save_image(imageData: dict, imageNumber: str):
    try:
        #Need to change to work with proxies
        urllib.request.urlretrieve(imageData['link'], f'images/{currTime}/{imageData["query"]}_{imageNumber}.jpg')
        logging.info(f'Saved image_{imageNumber}: {imageData["link"]}')
    except HTTPError as e:
        logging.error(f'Failed to save image_{imageNumber}: {imageData["link"]} with error: {e}')
        return f"{imageData['link']}"


# Removes unnecessary data from the response and returns the cleaned response
def cleanse_data(response):
    unneededData = ['kind', 'htmlTitle', 'displayLink', 'snippet',
    'htmlSnippet', 'mime', 'fileFormat', 'image']
    for x in unneededData:
        response.pop(x, None)
    return response


# Puts image data from Google Search into an Array
def get_images_data(query: str, numberOfImages: int, pageNumber: int):
    logging.info(f'Getting image links of Query: {query}\nNumber of Images: {numberOfImages}\nPage Number: {pageNumber}')
    service = build("customsearch", 'v1', developerKey=dataJSON['customSearchAPI'])
    allResponses = []
    try:
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
    except HttpError as e:
        logging.error(f"get_images_data error: {e.reason}")
        return []

    #Save responses to CSV file
    for i, response in enumerate(allResponses):
        allResponses[i] = cleanse_data(response)
        allResponses[i]['query'] = query
        allResponses[i]['pageNumber'] = pageNumber
        allResponses[i]['currentIndex'] = i+1

    if not allResponses:
        return None
    else:
        return allResponses


# Implements multiprocessing to save images
if __name__ == "__main__":  
    pageNumbers = []
    for i in range((numberOfImages//10)):
        pageNumbers.append(i+dataJSON['startingPageNumber'])
    imageNumber = []
    for i in range(numberOfImages):
        imageNumber.append(f'{(dataJSON["startingPageNumber"]-1)*10+(i+1)}')


    with Pool(8) as p:
        
        print("Scraping Image Links")
        imageData = p.starmap(get_images_data, zip(repeat(imageQuery), repeat(10), pageNumbers))
        allImageData = []
        # Changes dimension of imageData from [[imageDict, imageDict2]] to [imageDict, imageDict2]
        for images in imageData:
            allImageData.extend(images)
        
        imageMetaData = pd.DataFrame(allImageData)
        imageMetaData['Save Status'] = 'Success'
        imageMetaData.index += 1
        mkdir(f'images/{currTime}')

        print("Saving Images gathered")
        unsaved_data = p.starmap(save_image, zip(allImageData, imageNumber))
        print("Finished Saving Images")

        print("Saving dataframe to CSV")
        for unsaved in unsaved_data:
            imageMetaData.loc[imageMetaData['link'] == unsaved, 'Save Status'] = 'Error'
        imageMetaData.to_csv(f'saved_metadata/{currTime}.csv')
        print("Finished Saving to CSV")