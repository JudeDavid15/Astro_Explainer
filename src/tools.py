import os
import requests
from langchain_core.tools import tool

@tool
def get_img_of_day():
    """Fetch today's Astronomy Picture of the Day, including the title and explanation."""
    api_key = os.environ.get('NASA_API_KEY')
    resp = requests.get(
        "https://api.nasa.gov/planetary/apod",
        params={"api_key": api_key},
        timeout=15,
    )
    data = resp.json()
    if resp.status_code != 200 or 'title' not in data:
        return f"Couldn't fetch today's picture (status {resp.status_code}): {data}"
    return (
        f'<img src="{data["url"]}" width="500"><br><br>'
        f'### {data["title"]}\n\n{data["explanation"]}'
    )