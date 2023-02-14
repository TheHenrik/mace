import requests

def populate_airfoils(path = "./././data/airfoils/"):
    url = "https://m-selig.ae.illinois.edu/ads/coord_seligFmt/"
    r = requests.get(url)
    pass
