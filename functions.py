import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/111.0.0.0 Safari/537.36'}


def get_chipdip_items(query):
    query = query.replace(' ', '+')

    # ! важно передавать headers
    response = requests.get(f"https://www.chipdip.ru/search?searchtext={query}", headers=headers)
    items = BeautifulSoup(response.content, "html.parser").find_all('a', attrs={'class': ['link']})
    items = [item.get('href') for item in items if 'product' in item.get('href')]
    return items


def get_chipdip_item_info(href):
    print('ITEM INFO:', 'https://www.chipdip.ru' + href)
    response = requests.get('https://www.chipdip.ru' + href, headers=headers)
    parser = BeautifulSoup(response.content, "html.parser")
    name = parser.find('h1', attrs={'itemprop': ['name']}).text
    image_url = parser.find('img', attrs={'class': 'product__image-preview'}).get('src')
    return {'name': name, 'image_url': image_url}


def get_chipdip(query):
    items = get_chipdip_items(query)
    items_dict = {}

    for i in range(len(items)):
        items_dict[items[i]] = get_chipdip_item_info(items[i])

    return items_dict

# for item in get_chipdip_items("Магниторезистивный датчик"):
#     if 'product' in item.get('href'):
#         print(item)
#         print(item.get('href'))
#         print()
#     # res = BeautifulSoup(item, "html.parser").find('a', attrs={'class': ['link']})
#     # print(res)

print(get_chipdip("Магниторезистивный датчик цифровой"))