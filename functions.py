import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS, InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/111.0.0.0 Safari/537.36'}

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
    length_function=len
)

emb_model = HuggingFaceEmbeddings(model_name="cointegrated/LaBSE-en-ru")


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


def vectorize_file(path):
    '''
    Позволяет сплитовать и векторизовать pdf-файлы
    :param path: путь к файлу
    :return: путь к векторизованному файлу
    '''
    file_name = path.split('/')[-1]
    pdf_loader = PyPDFLoader(path)
    docs = pdf_loader.load()
    text_content = [doc.page_content for doc in docs]

    splitted_document = splitter.create_documents(text_content)

    vector_store = FAISS.from_documents(splitted_document, emb_model)
    vector_store.save_local(os.path.join('vectorization', file_name))

    return os.path.join('vectorization', file_name)


# print(vectorize_file("downloads/DOC003046561.pdf"))


def get_similarity_from_vectorization(path, query, k=3):
    '''
    Позволяет получить наиболее похожие части векторизованного файла на запрос
    :param path: путь к векторизованному файлу (dir)
    :param query: запрос
    :param k: количество возвращаемых результатов
    :return:
    '''
    vector_store = FAISS.load_local(path, emb_model, allow_dangerous_deserialization=True)
    content = [doc.page_content for doc in vector_store.similarity_search(query, k=k)]
    return content


# print(get_similarity_from_vectorization("vectorization/DOC003046561.pdf", "shutdown"))


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


def get_catalogs():
    '''
    Возвращает список объектов div, содержащих тематические каталоги из ChipDip
    :return: []
    '''
    response = requests.get("https://www.chipdip.ru/catalog", headers=headers)
    parser = BeautifulSoup(response.content, "html.parser")
    catalogs = parser.find_all('div', attrs={"class": "catalog__g1 clear"})
    return [str(catalog) for catalog in catalogs]


# print(get_catalogs())
# catalog0 = get_catalogs()[0]
# print(catalog0)
# print(type(catalog0))


def get_subcatalogs(catalog):
    '''
    Возвращает ссылки всех подкаталогов каталога
    :param catalog: str – html code
    :return: []
    '''
    parser = BeautifulSoup(catalog, "html.parser")
    subcatalogs = parser.find_all('a', attrs={"class": "link"})
    subcatalog_urls = [subcatalog.get('href') for subcatalog in subcatalogs]
    return subcatalog_urls[1:]


def get_subsubcatalogs(url):
    '''
    Возвращает ссылки всех подподкаталогов подкаталога
    :param url: url for subcatalog
    :return: []
    '''
    response = requests.get(url, headers=headers)
    catalog_div = BeautifulSoup(response.content, "html.parser").find("div", attrs={"class": "catalog"})
    parser = BeautifulSoup(str(catalog_div), "html.parser")
    subsubcatalogs = parser.find_all('a', attrs={"class": "link"})
    subsubcatalog_urls = [subsubcatalog.get('href') for subsubcatalog in subsubcatalogs]
    return subsubcatalog_urls


# print(get_subsubcatalogs("https://www.chipdip.ru/catalog/ic-chip"))


def get_items_of_subsubcatalof(url, page_number=0):
    if page_number != 0:
        url += f"?page={page_number}"

    print(page_number)

    response = requests.get(url, headers=headers)
    items_column_div = BeautifulSoup(response.content, "html.parser").find("div", attrs={"class": "items-column"})
    if not items_column_div:
        return []

    items = BeautifulSoup(str(items_column_div), "html.parser").find_all("a", attrs={"class": "link"})
    items_urls = [item.get("href") for item in items]
    return [items_urls] + get_items_of_subsubcatalof(url, page_number+1)


# print(get_items_of_subsubcatalof("https://www.chipdip.ru/catalog/ic-ac-dc-converters"))

# for catalog in get_catalogs():
#     subcatalogs = get_subcatalogs(catalog)
#     print(len(subcatalogs))
