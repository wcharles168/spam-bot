from twilio.rest import Client
from config import *
import requests
from bs4 import BeautifulSoup
import random
import urllib.request

def get_soup(url,header):
    return BeautifulSoup(urllib.request.urlopen(urllib.request.Request(url,headers=header)),'html.parser')


client = Client(TWILIO_SID, TWILIO_AUTH)
poor_soul = '+1510-282-6433'
cursed_search = "https://www.google.co.in/search?q=%22+dogs+%22&source=lnms&tbm=isch&gws_rd=ssl"
header={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
soup = get_soup(cursed_search ,header)
links = soup('img', class_='rg_i')

if __name__ == "__main__":
    while True:
        index = random.randint(0, len(links) - 1)
        img = links[index]
        print(img)
        if img.has_attr("data-src"):
            src = img["data-src"]
        else:
            continue
        body = " \n"
        client.messages.create(to=poor_soul, from_=FROM_NUMBER, body=body, media_url=[src])
        print("Message sent")
    time.sleep(10)
