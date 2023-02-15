import json
from googleapiclient.discovery import build
import urllib.request
from urllib.error import HTTPError
import logging
from multiprocessing import Pool
from p_tqdm import p_map
from itertools import repeat
import pandas as pd

dataJSON = json.load(open('data.json'))

#The prompt that the code will use
imageQuery = dataJSON['imageQuery']
#Rounds down to the nearest 10s
numberOfImages = dataJSON['numberOfImages']

logging.basicConfig(filename='main.log', encoding='utf-8', level=logging.INFO)
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

# Saves images into a folder named images; if it fails, logs url
def save_image(imageData: dict, imageName: str):
    try:
        #Need to change to work with proxies
        urllib.request.urlretrieve(imageData['link'], f'images/{imageData["query"]}{imageName}.jpg')
        logging.info(f'Saved image{i}: {imageData["link"]}')
    except HTTPError as e:
        logging.error(f'Failed to save image: {imageData["link"]}')

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
    imageNames = []
    for i in range(numberOfImages):
        imageNames.append(f'{(dataJSON["startingPageNumber"]-1)*10+(i+1)}')

    with Pool(6) as p:
        print("Scraping Image Links")
        imageData = p.starmap(get_images_data, zip(repeat(imageQuery), repeat(10), pageNumbers))
        allImageData = []
        # Changes dimension of imageData from [[imageDict, imageDict2]] to [imageDict, imageDict2]
        for images in imageData:
            allImageData.extend(images)
        if dataJSON['saveDataToCSV']:
            try:
                currentCSV = pd.read_csv('data.csv')
                df = pd.concat([currentCSV, pd.DataFrame(allImageData)])
                df.reset_index(drop=True, inplace=True)
                df.to_csv('data.csv')
            except:
                pd.DataFrame(allImageData).to_csv('data.csv')
        print("Saving Images gathered")
        p.starmap(save_image, zip(allImageData, imageNames))

    print("Finished Saving all Images")

