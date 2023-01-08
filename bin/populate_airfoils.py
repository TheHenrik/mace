import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import requests


def main():
    path = './data/airfoils/'
    url = 'https://m-selig.ae.illinois.edu/ads/coord_seligFmt/'
    r = requests.get(url)

    soup = BeautifulSoup(r.text, 'html.parser')

    for link in tqdm(soup.find_all('a')):
        file_name = link.get('href')
        if '.dat' not in file_name:
            continue
        r = requests.get(url+file_name, stream=True)
        with open(path+file_name, 'wb') as f:
            f.write(r.content)


if __name__ == '__main__':
    main()
