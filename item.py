import pickle
import functions
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chat_models import init_chat_model

from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationChain, LLMChain
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
    length_function=len
)





def vectorize_file(path, emb_model):
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


def get_similarity_from_vectorization(path, query, emb_model, k=3):
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


class Item:
    vector_path = []
    def __init__(self, name, url, price=0, image="", description="", characteristics=None, availability=0, manufacturer="", params=None, quantity=0):
        if characteristics is None:
            characteristics = dict()
        self.name: str = name
        self.url: str = url
        self.price: int = price
        self.image: str = image
        self.description: str = description
        self.characteristics: dict = characteristics
        self.availability: int = availability

        self.manufacturer: str = manufacturer
        self.params: dict = params
        self.quantity: int = quantity

        # Инициализация моделей и эмбеддингов
        self.emb_model = HuggingFaceEmbeddings(model_name="cointegrated/LaBSE-en-ru")
        self.llm = init_chat_model("deepseek-r1-distill-llama-70b", model_provider="groq")
        llm2 = init_chat_model("llama3-8b-8192", model_provider="groq")

        # Инициализация памяти и цепочки
        self.memory = ConversationSummaryBufferMemory(llm=self.llm, k=3, return_messages=True, memory_key="chat_history", max_token_limit=300)
        prompt = ChatPromptTemplate.from_messages([
            ("system", llm2.invoke(f"Ты полезный ассистент, который поможет пользователю найти нужный товар и ответить на все вопросы, связанные с ним. Товар: {self.name}\nХарактеристики: {self.characteristics}\nОписание: {self.description}\nЦена: {self.price}\nКоличество: {self.quantity}".replace("{", "(").replace("}", ")")+"\n\nСтруктурируй и сократи информацию представленную здесь").content),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        self.conversation = LLMChain(llm=self.llm, prompt=prompt, memory=self.memory, verbose=False)


    def set_name(self, name):
        self.name = name

    def set_url(self, url):
        self.url = url

    def set_price(self, price):
        self.price = price

    def set_image(self, src):
        self.image = src

    def set_description(self, description):
        self.description = description

    def add_characteristic(self, characterictic, value):
        self.characteristics[characterictic] = value

    def remove_characteristic(self, characterictic):
        del self.characteristics[characterictic]

    def set_characterictics(self, characterictics):
        self.characteristics = characterictics

    def set_availability(self, availability):
        self.availability = availability

    def answer_question(self, question):
        # Проверка и загрузка векторных данных
        if not self.vector_path:
            datasheet_urls = functions.get_datasheet(self.url)
            for url in datasheet_urls:
                file_name = f"{url.split('/')[-1].split('.')[0]}-{'-'.join(self.name.split())}.pdf"
                if functions.download_file(url, name=file_name):
                    try:
                        vector_path = vectorize_file(os.path.join('downloads', file_name), emb_model=self.emb_model)
                        self.vector_path.append(vector_path)
                    except Exception as e:
                        print(f"Ошибка при векторизации файла {file_name}: {e}")

        # Формирование запроса к векторной базе
        query_prompt = f"У пользователя вопрос: {question}. Сгенерируй запрос к векторной базе данных, чтобы найти нужную информацию для ответа."
        query = self.llm.invoke(query_prompt).content

        # Поиск в векторном хранилище
        content = []
        for path in self.vector_path:
            try:
                results = get_similarity_from_vectorization(path, query, k=2, emb_model=self.emb_model)
                content.extend(results)
            except Exception as e:
                print(f"Ошибка при поиске в векторном хранилище {path}: {e}")

        # Формирование ответа
        additional_info = "\n".join(content[:2]).replace("{", "(").replace("}", ")")
        print(additional_info)
        llm2 = init_chat_model("llama3-8b-8192", model_provider="groq")

        response = self.conversation.predict(input=llm2.invoke(f"Дополнительная информация: {additional_info}\nВопрос пользователя: {question}"+"\n\nСократи этот текст до минимума, но чтобы осталась основная информация по вопросу и вопрос, который задаётся").content)
        return response



    def from_dict(self, dictionary: dict):
        keys = dictionary.keys()
        try:
            self.name = dictionary['name']
            self.url = dictionary['url']
            self.price = dictionary['price']
            self.image = dictionary['image'] if 'image' in keys else ""
            self.description = dictionary['description'] if 'description' in keys else ""
            self.characteristics = dictionary['characteristics'] if 'characteristics' in keys else ""
            self.availability = dictionary['availability'] if 'availability' in keys else ""
        except Exception as e:
            return e

    def as_dict(self):
        return {'name': self.name,
                'url': self.url,
                'price': self.price,
                'image': self.image,
                'description': self.description,
                'characteristics': self.characteristics,
                'availability': self.availability}

    def to_pickle(self):
        return pickle.dumps(self)
