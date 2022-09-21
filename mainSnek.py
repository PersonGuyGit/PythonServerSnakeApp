from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import re #For Regular Expression

# For API setup
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

# For Template String (Used for URL)
from string import Template
# Use These methods to prevent spoofing and make it appear more natural
from time import sleep
from random import randint

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/findmysnek/{countySelection}")
def getAllTheSneks(countySelection: str):
    templateLink = Template("https://${clistCounty}.craigslist.org/search/pet?query=ball+python&hasPic=1")
    newLink = templateLink.substitute(clistCounty=countySelection)


    response = get(newLink)
    sleep(randint(1,5))

    img = "https://images.craigslist.org/"

    html_soup = BeautifulSoup(response.text, 'html.parser')

    # Here is how I learned to get the images during a search
    # only problem is that I cannot get the source of the image, with the correct size.

    #Src to solution I found
    # https://stackoverflow.com/a/60622833/14386721

    sleep(randint(1,5))
    imgs = [f"{img}{item.get('data-ids').split(':')[1].split(',')[0]}_300x300.jpg"
            for item in html_soup.findAll("a", class_="result-image gallery")]

    posts = html_soup.find_all('li', class_= 'result-row')

    id = 0

    class Snek(object): 
        def __init__(self, idInput, titleInput, linkInput, dateTimeInput, imageURLInput):
            self.ID = idInput
            self.title = titleInput
            self.link = linkInput
            self.dateTime = dateTimeInput
            self.imageURL = imageURLInput
            
    outputSneksContainer = []

    for i in range(len(posts)):
        currentPost = posts[i]

        new_snek_title = currentPost.find('a', class_='result-title hdrlnk')
        new_snek_title_text = new_snek_title.text
        
    #    Use a Regex to filter for Ball Python listings, that contain ball python in the title
        if re.search("ball(-|\s+)python", new_snek_title_text, re.I):

            new_snek_link = new_snek_title['href']
            new_snek_id = id
            
            new_snek_time = currentPost.find('time', class_= 'result-date')
            new_snek_datetime = new_snek_time['datetime']
            
            new_snek_image_url = imgs[i]

            NewSnek = Snek(new_snek_id, new_snek_title_text, new_snek_link, new_snek_datetime, new_snek_image_url)
            outputSneksContainer.append(NewSnek)
            id += 1


    #How to Convert object items into a dataframe, Solution found here 
    # https://stackoverflow.com/a/72450976/14386721
    df = pd.DataFrame([vars(c) for c in outputSneksContainer])
    df.set_index('ID')
            
    return Response(df.to_json(orient="records"), media_type="application/json")

    