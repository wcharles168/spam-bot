from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.orm import sessionmaker
from dateutil.parser import parse
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
from config import *

engine = create_engine("postgresql://localhost:5432/postings")

Base = declarative_base()

class Posting(Base):
    __tablename__ = "postings"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    date_created = Column(DateTime)
    url = Column(String, unique=True)
    price = Column(Float)
    p_id = Column(String, unique=True)

    def __repr__(self):
        return "Posting: %s \n %s \n" % (self.title, self.url)


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
client = Client(TWILIO_SID, TWILIO_AUTH)


# Scrape URL(s) for posting information
def get_postings():
    postings = []
    for url in URLS:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        links = soup('p', class_='result-info')
        for link in links:
            title = link.find('a', class_='result-title')
            price = link.find('span', class_='result-price')
            date = link.find('time', class_='result-date')
            result = {}
            result["id"] = title["data-id"]
            result["name"] = title.text
            result["url"] = title["href"]
            result["date"] = date["title"]
            if price is not None:
                result["price"] = price.text
            else:
                result["price"] = "N/A"
            parsed_price = 0
            try:
                price = float(result["price"].replace("$", ""))
            except Exception:
                pass
            result["price"] = parsed_price
            postings.append(result)
    return postings


# Only add and return new postings
def store_postings():
    all_postings = get_postings()
    new_postings = []
    for post in all_postings:
        post_check = session.query(Posting).filter(Posting.p_id == post["id"]).first()
        if post_check is None:
            posting = Posting(
                title = post["name"],
                date_created = parse(post["date"]),
                url = post["url"],
                price = post["price"],
                p_id = post["id"]
            )
            session.add(posting)
            session.commit()
            new_postings.append(posting)
    return new_postings

# Perform scrape and sends new results by SMS
def scrape():
    new_postings = store_postings()
    if len(new_postings) > 0:
        print("New postings found")
        send_text(new_postings)


def send_text(postings):
    body = "There are new postings that you might be interested in. \n"
    for post in postings:
        body = body + str(post) + "\n"
    for number in TO_NUMBERS:
        client.messages.create(to=number, from_=FROM_NUMBER, body=body)
    print("Message sent")
