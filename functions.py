import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

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

# print(get_chipdip("Магниторезистивный датчик цифровой"))


def get_datasheet(url):
    '''
    Позволяет получить ссылку для загрузки даташита элемента
    по ссылке на страницу элемента
    :param url: ссылка на страницу элемента
    :return: список с ссылками на файлы даташитов
    '''
    response = requests.get(url, headers=headers)
    parser = BeautifulSoup(response.content, "html.parser")
    datasheets = parser.find_all('a', attrs={'class': 'link download__link with-pdfpreview'})
    datasheet_urls = [sheet.get('href') for sheet in datasheets]
    return datasheet_urls

# print(get_datasheet("https://www.chipdip.ru/product/ld7522ps"))


def download_file(url, name=None):
    '''
    Позволяет сохранить файл на сервер
    :param url: ссылка на файл
    :param name: (опционально) задать имя файла в системе
    :return: True, если сохранение успешно, False – в ином случае
    '''
    response = requests.get(url)
    if name:
        file_path = name
    else:
        file_path = url.split('/')[-1]

    if response.status_code == 200:
        with open(os.path.join('downloads', file_path), 'wb') as file:
            file.write(response.content)
        return True
    return False

# print(download_file("https://static.chipdip.ru/lib/046/DOC003046561.pdf"))


def parse_bom(file: str):
    if file.endswith('.xlsx'):
        data = pd.read_excel(file, index_col='Index')
        return data
    elif file.endswith('.csv'):
        data = pd.read_csv(file, sep=';', index_col='index')
        return data
    elif file.endswith('.txt'):
        data = pd.read_csv(file, sep=';', index_col='Index')
        return data


# print(parse_bom('bom_examples/bom_example.xlsx'))