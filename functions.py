import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import math
import numpy as np
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS, InMemoryVectorStore
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain.chat_models import init_chat_model
from langchain_huggingface import HuggingFaceEmbeddings
import config
import re

import sql

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/111.0.0.0 Safari/537.36'}

if not os.environ.get("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = config.Grock

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
    length_function=len
)

emb_model = HuggingFaceEmbeddings(model_name="cointegrated/LaBSE-en-ru")


def capcha_fix(url):
    print("\n" * 10)
    print('WARNING:', 'https://www.chipdip.ru' + url)
    input("Пройдите капчу по ссылке и нажмиет Enter")


def get_chipdip_items(query):
    query = query.replace(' ', '+')

    # ! важно передавать headers
    response = requests.get(f"https://www.chipdip.ru/search?searchtext={query}", headers=headers)
    items = BeautifulSoup(response.content, "html.parser").find_all('a', attrs={'class': ['link']})
    items = [item.get('href') for item in items if 'product' in item.get('href')]
    return items


def get_chipdip_item_info(href, capcha=capcha_fix):
    print('ITEM INFO:', 'https://www.chipdip.ru' + href)
    response = requests.get('https://www.chipdip.ru' + href, headers=headers)
    parser = BeautifulSoup(response.content, "html.parser")
    try:
        meta_tag = parser.find('meta', attrs={'name': 'keywords'})
        name = meta_tag.get('content', '') if meta_tag else 'Не найдено'
        description = parser.find('meta', attrs={'name': 'description'}).get('content', '')

        table = parser.find("table", class_="product__params ptext", id="productparams")

        params = {}
        if table:
            for row in table.find_all("tr"):
                name_tag = row.find("td", class_="product__param-name")
                value_tag = row.find("td", class_="product__param-value")

                if name_tag and value_tag:
                    name_p = name_tag.text.strip()
                    value = value_tag.text.strip()
                    params[name_p] = value

        availability_tag = parser.find("span", class_="item__avail")

        # Извлекаем текст из тега <b>
        if availability_tag:
            bold_tag = availability_tag.find("b")
            if bold_tag:
                # Достаём число с помощью регулярного выражения
                match = re.search(r"\d+", bold_tag.text)
                if match:
                    stock = int(match.group())  # Преобразуем в число
                    print(f"В наличии: {stock} шт.")

    except:
        capcha(href)
        return get_chipdip_item_info(href=href, capcha=capcha)
    image_url = parser.find('img', attrs={'class': 'product__image-preview'}).get('src')
    return {'name': name, 'image_url': image_url, 'description': description, "params": params, "availability": stock,
            "href": href}


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
        data = pd.read_excel(file)
        return data
    elif file.endswith('.csv'):
        data = pd.read_csv(file, sep=';')
        return data
    elif file.endswith('.txt'):
        data = pd.read_csv(file, sep=';')
        return data


def parse_characteristics(char_str):
    if pd.isna(char_str):
        return []  # Если характеристик нет, возвращаем пустой словарь
    return [{"name": item.split(": ")[0], "num": item.split(": ")[1]} for item in char_str.split(", ")]


def read_data(data):
    print(data)
    data["characteristics"] = data["characteristics"].apply(parse_characteristics)

    # Преобразуем в словарь
    result = data.set_index("name").to_dict(orient="index")
    return result


def llm_search(object, key):
    prompt = """
    Если гдето в моём сообщении будешь видеть nan - значит там пусто

    У меня есть задача найти такой электрический компанент: {name}
    Вот от такой фабрики: {manufacturer}
    У него обязательно должны быть вот такие характеристики:
    {characteristics}

    Я ищю это всё в магазине, на их сайте есть поиск, что я должен ввести, не используя фильтры, чтобы нашёлся нужный мне компанент.

    Примеры запросов:
    "Резистор 100 Ом 50 Вт" - Резистор номиналом 100 Ом, потребляющий максимально 50 Вт
    "Стабилизатор напряжения 5V 1A" = Стабилизатор напряжения 5 В, выдающий максимально 1 А, но я подавал ещё характеристику, что на вход максимум подаётся 6-36V, но этого в запросе нет, так как это лишняя информация
    "Чип 78L05 TO-92" - Я в названии уже указал конкретный чип в корпусе TO-92. И только если я не найду его в оригинале, то буду делать запрос на поиск аналогов. 

    Подумай над этим запросом шаг за шагом, он должен быть коротким и лаконичным. 
"""
    exmpls_prompt = """
    {name}: {num}
"""
    characteristics = FewShotPromptTemplate(
        examples=object['characteristics'],
        prefix="",
        example_prompt=PromptTemplate(
            template=exmpls_prompt,
            input_variables=["name", "num"],
            example_separator="\n------------\n"
        ),
        suffix="",
        input_variables=[]
    ).format()
    prompt = PromptTemplate(
        template=prompt,
        input_variables=["name", "manufacturer", "characteristics"],
    ).format(name=key, manufacturer=object["manufacturer"], characteristics=characteristics)
    llm = init_chat_model("deepseek-r1-distill-llama-70b", model_provider="groq")
    llm2 = init_chat_model("llama3-8b-8192", model_provider="groq")
    search = llm2.invoke("Ты думал вот так:" + llm.invoke(
        prompt).content + "\nВыдели из этих рассуждений финальный ответ(запрос в поисковим) и верни мне только ЕГО:")
    chip = get_chipdip(search.content)

    chip_availability = []

    for i in chip.keys():
        if (chip[i]["availability"] >= object["quantity"]):
            chip_availability.append(chip[i])

    return {}


def search_BOM(path):
    data = read_data(parse_bom(path))
    result = {}
    print(data)
    for i in data.keys():
        print(i)
        if (data[i]["url"] != data[i]["url"]):
            result[i] = llm_search(data[i], i)
            result[i]["history"] = result[i].get("history", list())
            result[i]["history"].append({"type": "sys", 'msg': "Найдено по характеристикам в таблице"})
        else:
            req = get_chipdip_item_info(data[i]["url"])
            print("\\/ " * 20)
            print("Название: ", req["name"])
            print("Описание: ", req["description"])
            print("Наличие: ", req["availability"])
            print("\nПараметры\n", "-" * 30)
            for j in req["params"].keys():
                print(j, ": ", req["params"][j])
            print("/\\ " * 20)
            print("\n\n")
            result[i] = req
            result[i]["history"] = result[i].get("history", list())
            result[i]["history"].append({"type": "sys", 'msg': "Взято по ссылке из таблицы"})
            if (req["availability"] < data[i]["quantity"]):
                result[i] = llm_search(data[i], i)
                result[i]["history"] = result[i].get("history", list())
                result[i]["history"].append(
                    {"type": "sys", 'msg': "Оригинала слишком мало: " + str(req["availability"])})
    return result


# print(parse_bom('bom_examples/bom_example.xlsx'))


"""
ТЕСТОВАЯ ФУНКЦИЯ, ПОТОМ УБРАТЬ
"""
def llm_invoke(message_id, query):
    llm = init_chat_model("llama3-8b-8192", model_provider="groq")
    answer = llm.invoke(f"""
    Поговори с пользователем, он написал:
    {query}
    """).content
    sql.add_message_answer(message_id, answer)


if __name__ == "__main__":
    print(search_BOM('bom_examples/bom_example.csv'))

    # Генератор красивого отчёта
#    chip = get_chipdip("Стабилизатор напряжения 5V; 6V-36V input")
#    print("\n"*5)
#    for i in chip.keys():
#        print(i)
#        print("Название: ",chip[i]["name"])
#        print("Описание: ",chip[i]["description"])
#        print("Наличие: ", chip[i]["availability"])
#        print("\nПараметры\n","-"*30)
#        for j in chip[i]["params"].keys():
#            print(j, ": ", chip[i]["params"][j])
#        print("\n\n")
