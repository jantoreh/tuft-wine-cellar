from typing import Annotated
from fastapi import FastAPI, Body
from pydantic import BaseModel
from utils import get_image, set_failed, set_ok
from chat import get_wine_suggestion, decipher_wine_label
from cellar import insert_data_to_google_sheet, update_quantity
import traceback

app = FastAPI()

@app.get("/add")
def _add():
    try:
        print("Got ADD request")
        image_path = get_image()
        status, data = decipher_wine_label(image_path)
        
        if status == "exist":
            update_quantity(data, 1)
            set_ok()
            return f"This type already exists, in row {data}. Quantity is adjusted"
        if status == "failed":
            set_failed()
            return f"Something went wrong adding the wine"
        if status == "not_readable":
            set_failed()
            return f"Wine label not readable"
        
        insert_data_to_google_sheet(data["name"], data["producer"], data["type"], data["grape"], data["year"], data["origin"], description=data["description"])
        set_ok()
        return f"Successfully added {data['name']} ({data['year']}) to the cellar with the following description: {data['description']}"
    except Exception:
        print(traceback.format_exc())
        set_failed()
        return "Something went wrong"
    
@app.get("/remove")
def _remove():
    try:
        print("Got REMOVE request")
        image_path = get_image()
        status, data = decipher_wine_label(image_path)
        
        if status == "exist":
            update_quantity(data, -1)
            set_ok()
            return f"Found the wine. Quantity is adjusted by -1."
        if status == "failed":
            set_failed()
            return f"Something went wrong removing the wine"
        if status == "not_readable":
            set_failed()
            return f"Wine label not readable"

        set_failed()
        return f"Did not find a match in the cellar."
    except Exception:
        print(traceback.format_exc())
        set_failed()
        return "Something went wrong"


class RequestBody(BaseModel):
    message: str
    key: str


@app.post("/suggestion")
async def _get_suggestion(input: Annotated[RequestBody, Body]):
    text = input.message
    print(f"Got prompt: {text}")
    output = get_wine_suggestion(text)
    set_ok()
    return output
