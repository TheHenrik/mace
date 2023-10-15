import asyncio
from os import listdir

import requests
from bs4 import BeautifulSoup, ResultSet


async def _download(link: ResultSet, downloaded: set, path: str, url: str):
    file_name = link.get("href")

    if ".dat" not in file_name:
        return
    if file_name in downloaded:
        return

    r = requests.get(url + file_name, stream=True)
    with open(path + file_name, "wb") as f:
        f.write(r.content)


async def _async(soup: BeautifulSoup, downloaded: set, path: str, url: str):
    async with asyncio.TaskGroup() as tg:
        tasks = [
            tg.create_task(_download(link, downloaded, path, url))
            for link in soup.find_all("a")
        ]


def populate_airfoils(path="./././data/airfoils/", asynchronus=True):
    url = "https://m-selig.ae.illinois.edu/ads/coord_seligFmt/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    downloaded = set(listdir(path))

    if asynchronus:
        asyncio.run(_async(soup, downloaded, path, url))
        return

    for link in soup.find_all("a"):
        file_name = link.get("href")
        if ".dat" not in file_name:
            continue
        if file_name in downloaded:
            continue
        r = requests.get(url + file_name, stream=True)
        with open(path + file_name, "wb") as f:
            f.write(r.content)


if __name__ == "__main__":
    populate_airfoils()
