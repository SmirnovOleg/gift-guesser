import urllib.parse

import requests
from bs4 import BeautifulSoup


def parse_gifts():
    base_url = 'https://podarki.ru'
    gifts_url = 'https://podarki.ru/idei/Podarki-Lyubimoy-5253'
    page = requests.get(gifts_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    cards = soup.find_all('div', class_='goods-block__item good-card')
    gifts = []
    for card in cards:
        gifts.append({
            'name': card.find('div', class_='good-card__name').text,
            'price': card.find('div', class_='good-card__price').text,
            'link': urllib.parse.urljoin(base_url,
                                         card.find('a', class_='good-card__link-product')['href'])
        })

    return gifts
