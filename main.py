import json
import re
from itertools import count
from time import sleep

import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://novosibirsk.n1.ru'
BUILDING_PAGE_TEMPLATE = 'https://novosibirsk.n1.ru/building/{}/'


def get_flats(url):
    flats = {}
    for page in count(start=1):
        search_url = f'{url}&page={page}'

        response = requests.get(search_url)
        response.raise_for_status()

        new_flats = parse_search_results(response.text)

        if not new_flats:
            return flats

        flats |= new_flats


def parse_search_results(html):
    soup = BeautifulSoup(html, 'lxml')

    cards = soup.find_all('div', class_='living-list-card__main-container')

    if not cards:
        return None

    flats = {}

    for card in cards:
        main_info = card.find('div', class_='living-list-card__col _main')
        rel_url = main_info.find('div', class_='card-title living-list-card__inner-block')\
            .find('a')['href']

        area_and_unit = card.find(
            class_='living-list-card__area living-list-card-area living-list-card__inner-block'
        )
        area, _unit = area_and_unit.text.split()

        num_of_floors_info = card.find(
            class_='living-list-card__floor living-list-card-floor living-list-card__inner-block'
        )

        apartment_floor, _sep, max_floor, _ = num_of_floors_info.text.split()

        material = card.find(
            class_='living-list-card__material living-list-card-material living-list-card__inner-block'
        )

        material = material.text if material else ''

        price = card.find(
            class_='living-list-card-price__item _object'
        ).text

        _, flat_id = rel_url.strip('/').split('/')

        flats[int(flat_id)] = {
            'url': f'{BASE_URL}{rel_url}',
            'area': float(area),
            'apartment_floor': int(apartment_floor),
            'max_floor': int(max_floor),
            'material': material,
            'price': int(price.replace(' ', '')),
        }

        sleep(0.5)

    return flats


def get_building_page(building_id):
    url = BUILDING_PAGE_TEMPLATE.format(building_id)

    response = requests.get(url)
    response.raise_for_status()

    return response.text


def title_to_address(title):
    splitted = title.split('ул. ')

    if len(splitted) == 1:
        splitted = title.split('Новосибирск, ')

    return splitted[1].split(' - ')[0]


def normalize_year(raw_year, year_length=4):
    if len(raw_year) != year_length:
        return int(raw_year.split()[-2])
    return int(raw_year)


def parse_building_page(html):
    soup = BeautifulSoup(html, 'lxml')

    search_page = soup.find('a', class_='ui-kit-link _type-common _color-blue')['href']

    address = title_to_address(soup.title.text)

    raw_year = soup.\
        find('div', class_='object-main-params__col _release-date').\
        find('p', class_='object-main-params__text').text

    year = normalize_year(raw_year)

    lon_pattern = re.compile(r'"longitude":(\d+\.\d+),')
    lat_pattern = re.compile(r'"latitude":(\d+\.\d+),')

    script = soup.find('script', text=lon_pattern)

    lon = lon_pattern.search(script.string).group(1)
    lat = lat_pattern.search(script.string).group(1)

    return {
        'search_url': f'{BASE_URL}{search_page}',
        'year': year,
        'address': address,
        'lon': lon,
        'lat': lat,
    }


def main():
    buildings_ids = []
    buildings_filename = 'buildings.txt'

    with open(buildings_filename) as f:
        for row in f:
            building_id, *_ = row.split()
            buildings_ids.append(building_id)

    buildings = {}
    for building_id in buildings_ids:
        buildings[building_id] = parse_building_page(get_building_page(building_id))
        buildings[building_id]['flats'] = get_flats(buildings[building_id]['search_url'])
        sleep(1)

    with open('buildings.json', 'w', encoding='utf-8') as f:
        json.dump(buildings, f, ensure_ascii=False)


if __name__ == '__main__':
    main()
