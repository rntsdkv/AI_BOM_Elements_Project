class Item:
    def __init__(self, name, url, image="", description="", characteristics=None, availability=0):
        if characteristics is None:
            characteristics = dict()
        self.name: str = name
        self.url: str = url
        self.image: str = image
        self.description: str = description
        self.characteristics: dict = characteristics
        self.availability: int = availability

    def set_name(self, name):
        self.name = name

    def set_url(self, url):
        self.url = url

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

    def from_dict(self, dictionary: dict):
        keys = dictionary.keys()
        try:
            self.name = dictionary['name']
            self.url = dictionary['url']
            self.image = dictionary['image'] if 'image' in keys else ""
            self.description = dictionary['description'] if 'description' in keys else ""
            self.characteristics = dictionary['characteristics'] if 'characteristics' in keys else ""
            self.availability = dictionary['availability'] if 'availability' in keys else ""
        except Exception as e:
            return e
