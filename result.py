from item import Item


class Result:
    def __init__(self, titles: list[str], items: list[Item]):
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

    def from_list(self, list_of_items: list[(str, Item)]):
        self.list_of_items = list_of_items
        return self