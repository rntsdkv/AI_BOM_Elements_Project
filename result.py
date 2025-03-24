from item import Item
import pandas as pd
from main import check_folders

class Result:
    def __init__(self, titles=[], items=[]):
        self.list_of_items = []
        for i in range(len(titles)):
            self.list_of_items.append((titles[i], items[i]))

    def replace_item(self, index: int, item: Item):
        if index >= len(self.list_of_items): return 0
        self.list_of_items[index] = (self.list_of_items[index][0], item)
        return self

    def add_item(self, title: str, item: Item):
        self.list_of_items.append((title, item))
        return self

    def delete_item(self, index: int):
        if index >= len(self.list_of_items): return 0
        del self.list_of_items[index]
        return self

    def as_list(self):
        list_of_items = [(title, item.as_dict()) for title, item in self.list_of_items]
        return list_of_items

    def from_list(self, list_of_items: list):
        self.list_of_items = list_of_items
        return self

    def generate_report(self, user_id):
        check_folders()
        data = []
        for title, item in self.list_of_items:
            data.append((item.name, item.url, item.description, item.price, item.characteristics))
        print(data)
        df = pd.DataFrame(data=data, columns=["name", "url", "description", "price", "characteristics"])
        df.to_excel("uploads/" + user_id)
        return df


if __name__ == "__main__":
    result = Result().from_list([("Магниторезистентный цифровой вольтметр", Item("Конструктор прибор, вольтметр+амперметр цифровой, SVAL0013PW",
                                                    "https://www.chipdip.ru/product0/8031325911", price=100,
                                                    image="https://static.chipdip.ru/lib/304/DOC045304074.jpg")),
                                ("Миллиомметр", Item("DT-5302, Миллиомметр", "https://www.chipdip.ru/product/dt-5302",
                                                     price=1425,
                                                    image="https://static.chipdip.ru/lib/249/DOC005249889.jpg"))])
    df = result.generate_report()
    print(df)