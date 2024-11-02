from pymongo import MongoClient
from bson.objectid import ObjectId
import requests
from bs4 import BeautifulSoup
import json

client = MongoClient("mongodb://localhost:27017/")
db = client["cat_and_quotes_database"]
cats_collection = db["cats"]
quotes_collection = db["quotes"]
authors_collection = db["authors"]

def create_cat(name, age, features):
    cat = {
        "name": name,
        "age": age,
        "features": features
    }
    result = cats_collection.insert_one(cat)
    print(f"Кот добавлен с id {result.inserted_id}")

def read_all_cats():
    cats = cats_collection.find()
    for cat in cats:
        print(cat)

def read_cat_by_name(name):
    cat = cats_collection.find_one({"name": name})
    if cat:
        print(cat)
    else:
        print("Кот не найден")

def update_cat_age(name, new_age):
    result = cats_collection.update_one({"name": name}, {"$set": {"age": new_age}})
    if result.modified_count:
        print(f"Возраст кота '{name}' обновлен до {new_age}")
    else:
        print("Кот не найден")

def add_feature(name, feature):
    result = cats_collection.update_one({"name": name}, {"$push": {"features": feature}})
    if result.modified_count:
        print(f"Характеристика '{feature}' добавлена к коту '{name}'")
    else:
        print("Кот не найден")

def delete_cat_by_name(name):
    result = cats_collection.delete_one({"name": name})
    if result.deleted_count:
        print(f"Кот '{name}' удален")
    else:
        print("Кот не найден")

def delete_all_cats():
    result = cats_collection.delete_many({})
    print(f"Удалено {result.deleted_count} котов")


def scrape_and_save_quotes():
    base_url = "http://quotes.toscrape.com"
    page_url = "/page/1/"
    quotes = []
    authors = {}

    while page_url:
        response = requests.get(base_url + page_url)
        soup = BeautifulSoup(response.text, "html.parser")

        quote_elements = soup.select(".quote")
        for quote_element in quote_elements:
            text = quote_element.find(class_="text").get_text()
            author_name = quote_element.find(class_="author").get_text()
            tags = [tag.get_text() for tag in quote_element.find_all(class_="tag")]

            quote_data = {
                "quote": text,
                "author": author_name,
                "tags": tags
            }
            quotes.append(quote_data)

            if author_name not in authors:
                author_url = base_url + quote_element.find("a")["href"]
                author_response = requests.get(author_url)
                author_soup = BeautifulSoup(author_response.text, "html.parser")

                author_info = {
                    "fullname": author_name,
                    "born_date": author_soup.find(class_="author-born-date").get_text(),
                    "born_location": author_soup.find(class_="author-born-location").get_text(),
                    "description": author_soup.find(class_="author-description").get_text().strip()
                }
                authors[author_name] = author_info

        next_button = soup.select_one(".next > a")
        page_url = next_button["href"] if next_button else None

    quotes_collection.insert_many(quotes)
    authors_collection.insert_many(list(authors.values()))
    print("Цитаты и авторы успешно сохранены в MongoDB")


if __name__ == "__main__":
    print("CRUD операции для коллекции котов:")
    create_cat("barsik", 3, ["ходит в капці", "дає себе гладити", "рудий"])
    read_all_cats()
    read_cat_by_name("barsik")
    update_cat_age("barsik", 4)
    add_feature("barsik", "мурлычет")
    delete_cat_by_name("barsik")
    delete_all_cats()
    print("\nСкрапинг цитат и авторов:")
    scrape_and_save_quotes()
