import re
import json

class PageManager:
    def __init__(self):
        self.page_data = ["No page data here", []]

    def interpret_page(self, page, gavbot):
        split = re.split("<title>", page)
        title = "<b>" + split[1] + "</b>"
        split = re.split("<text>", split[2])
        text = split[1]
        text = re.sub("\n\n", "<p>", text)
        text = "<p>" + text
        choices = re.split("<choice>", split[2])
        choices.pop(0)
        choices = [tuple(re.split("<page>", re.sub("\n", "", x))) for x in choices]
        choices = [tuple([x[0]] + (re.split("<req>", x[1]))) for x in choices]
        choices = [(x[0], x[1], re.split("/", x[2])) for x in choices]
        choices = [x for x in choices if [y for y in x[2] if y in gavbot.traits + gavbot.inventory] == x[2] or x[2] == [""]]
        page_data = [title, text, choices]
        return page_data

    def load_page(self, gavbot):
        file_path = "pages/act_" + str(gavbot.current_act) + "/" + str(gavbot.current_page) + ".txt"
        with open(file_path, "r") as file:
            raw_text = file.read()
        page_data = self.interpret_page(raw_text, gavbot)
        return page_data

class Gavbot:
    def __init__(self, owner):
        try:
            self.manager = PageManager()
            self.load_gav(owner)
            self.pic = "static/images/gavbot.jpg"
            self.health_pic = "static/images/heart.jpg"
        except FileNotFoundError:
            self.owner = owner
            self.manager = PageManager()
            self.health = 3
            self.pic = "static/images/gavbot.jpg"
            self.health_pic = "static/images/heart.jpg"
            self.traits = []
            self.inventory = []
            self.current_act = 1
            self.current_page = "intro"
            self.manual_update_page(self.current_page)
            self.save_gav()

    def manual_update_page(self, page_name):
        self.page_data = self.manager.load_page(self)
        self.valid_choices = [x[1] for x in self.page_data[2]]
        self.save_gav()

    def update_page(self, page_name):
        if page_name in self.valid_choices:
            self.current_page = page_name
            self.page_data = self.manager.load_page(self)
            self.valid_choices = [x[1] for x in self.page_data[2]]
            self.save_gav()
        else:
            print("NOT VALID PAGE CHOICE")

    def reset_gavbot(self):
        self.manager = PageManager()
        self.health = 3
        self.pic = "static/images/gavbot.jpg"
        self.health_pic = "static/images/heart.jpg"
        self.traits = []
        self.inventory = []
        self.current_act = 1
        self.current_page = "intro"
        self.manual_update_page(self.current_page)
        self.save_gav()

    def save_gav(self):
        file_name = "saved_gavbots/" + self.owner + ".json"
        data = {
            "owner": self.owner,
            "health": self.health,
            "traits": self.traits,
            "inventory": self.inventory,
            "act": self.current_act,
            "page": self.current_page}
        data_dumps = json.dumps(data)
        with open (file_name, "w") as file:
            file.write(data_dumps)

    def load_gav(self, owner):
        file_name = "saved_gavbots/" + owner + ".json"
        with open(file_name, "r") as file:
            data = json.loads(file.read())
        self.owner = data["owner"]
        self.health = data["health"]
        self.traits = data["traits"]
        self.inventory = data["inventory"]
        self.current_act = data["act"]
        self.current_page = data["page"]
        self.manual_update_page(self.current_page)


if __name__ == "__main__":
    manager = PageManager()
    page = manager.load_page("pages/act_1/page_1.txt")
    print(page)
