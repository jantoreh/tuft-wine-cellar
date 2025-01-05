import os
import re
import requests
from openai import OpenAI
from cellar import get_data_from_google_sheet


SECRET = os.getenv("OPENAI_SECRET")

client = OpenAI(api_key=SECRET)


def get_wine_suggestion(message):
    data = get_data_from_google_sheet()
    response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
        "role": "system",
        "content": f"You will be provided with a question related to a list of data, and your task is to find the best wine from the list, given the user preference. The input may be provided in norwegian, but answer in english anyways. Here is the data: {data}"
        },
        {
        "role": "user",
        "content": message
        }
    ],
    temperature=1,
    max_tokens=256,
    top_p=1
    )

    return response.choices[0].message.content


def decipher_wine_label(image_path):
    import base64
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")
    image_data = "data:image/png;base64," + image_data
    data = get_data_from_google_sheet()
    response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
        "role": "system",
        "content": f"You will be given an image of a wine label. The user want to know the following properties: Name, Producer, Year, Type, Grape, Origin, Short Description. The short description should contain some basic information about the wine (for instance if it is dry) and which food it pairs well with. If the wine is already listed in the dataset (also with 0 quantity), return ALREADY EXISTS, and in which row. If you are not able to read the wine label or there is no wine in the photo, return NOT READABLE. If you cannot determine the year, return 999 as the year. If you cannot determine the type of grape(s), set it to unknown. Here is the data: {data}"
        },
        {
        "role": "user",
        "content": [{"type": "image_url", "image_url": {"url": image_data, "detail": "auto"}}]
        }
    ],
    temperature=1,
    max_tokens=256,
    top_p=1
    )

    message = response.choices[0].message.content
    print("Got response message:", message)
    if "ALREADY EXISTS" in message.upper() and "ROW" in message.upper():
        row = int(float(re.search(r"rows?\s(\d+)", message).group(1)))
        print(f"Already exists in row {row}")
        return "exist", row
    if "NOT READABLE" in message.upper() or "NOT FULLY READABLE" in message.upper():
        return "not_readable", None

    message = message.replace("**", "")
    name = re.search(r"Name: (.+)", message).group(1)
    year = int(re.search(r"Year: (\d+)", message).group(1))
    if year == 999:
        year = "unknown"
    producer = re.search(r"Producer: (.+)", message).group(1)
    type = re.search(r"Type: (.+)", message).group(1)
    grape = re.search(r"Grape: (.+)", message).group(1)
    origin = re.search(r"Origin: (.+)", message).group(1)
    description = re.search(r"Short Description: (.+)", message).group(1)
    
    return "success", {"name": name, "year": year, "producer": producer, "type": type, "grape": grape, "origin": origin, "description": description}
