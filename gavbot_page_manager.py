import re
import json
import codecs


class PageManager:
    def __init__(self):
        self.page_data = ["No page data here", []]

    def interpret_page(self, page, gavbot):
        """Take a .txt page from the book, and returns the data in the following list:
            [0] Page Title
            [1] Page text
            [2] Items gained or lost on accessing this page
            [3] A list of potential redirects if certain items are possessed
            [4] A list of special actions for this scrpit to perform
            [5] A list of choices for the reader, sepertated as follows:
                [0] Choice text
                [1] File name of page choice leads to
                [2] Item requirements for choice to be displayed"""
        split = re.split("<title>", page)
        title = "<b>" + split[1] + "</b>"
        split = re.split("<text>", split[2])
        text = split[1]
        text = re.sub("\n\n", "<p>", text)
        text = "<p>" + text
        split = re.split("<items>", split[2])
        items = split[1]
        split = re.split("<bounce>", split[2])
        bounce = split[1]
        split = re.split("<special>", split[2])
        special = split[1]
        choices = re.split("<choice>", split[2])
        choices.pop(0) #now we have choices serialised
        for i in range(len(choices)):
            choices[i] = re.sub("\n", "", choices[i])
            choices[i] = re.sub("<page>", "<>", choices[i])
            choices[i] = re.sub("<req>", "<>", choices[i])
            choices[i] = re.split("<>", choices[i])
        page_data = [title, text, items, bounce, choices, special]
        return page_data

    def load_page(self, gavbot):
        """Take a file name and pass the corresponding document string to interpret_page"""
        file_path = "{}pages/act_{}/{}.txt".format(gavbot.path, str(gavbot.current_act), str(gavbot.current_page))
        with codecs.open(file_path, "r") as file:
            raw_text = file.read()
        page_data = self.interpret_page(raw_text, gavbot)
        return page_data

class GavStat:
    def __init__(self):
        self.type = None

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        if self.type:
            if type(value) == type(self.value):
                self.value = value
            else:
                raise AttributeError("Expected type {}, got type {}".format(self.type, type(value)))
        else:
            self.value = value
            self.type = type(value)

class Gavbot:
    def __init__(self, owner, path="/"):
        """Attempt to load a saved gavbot with the name provided; create a new gavbot with specific attributes
        if no such gavbot exists"""
        self.path = path
        self.manager = PageManager()
        try:
            self.load_gav(owner)
        except FileNotFoundError:
            self.owner = owner
            self.health = 3
            self.max_health = 3
            self.meta = []
            self.traits = []
            self.inventory = []
            self.current_act = 0
            self.current_page = "intro"
            self.update_page()
            self.save_gav()
        self.item_lists = {
            "meta": self.meta,
            "trait": self.traits,
            "inventory": self.inventory
            }
        self.pic = "/gavbot_static/images/gavbot.jpg"
        self.health_pic = "/gavbot_static/images/heart.jpg"
        self.empty_health_pic = "/gavbot_static/images/empty_heart.jpg"
        self.update_page()

    def user_update_page(self, page_name):
        """Method is called by the server to move to the appropriate page when the user makes a choice.
        Makes sure that the choice is, in fact, a choice the user is able to make"""
        if page_name in self.valid_choices:
            self.current_page = page_name
            self.update_page()
        else:
            print("NOT VALID PAGE CHOICE")

    def update_page(self):
        """Gets parsed page data from PageManager, then updates the appropriate Gavbot attributes
            Calls update_items and refine_choices to accomplish this"""
        page_data = self.manager.load_page(self)
        print("gavbot:", page_data[3])
        print("CURRENT INVENTORY:", self.meta)
        if page_data[3]:
            bounce = self.bounce_check(page_data[3])
            if bounce:
                self.current_page = bounce
                self.update_page()
                return
        self.page_title = page_data[0]
        self.page_text = page_data[1]
        self.page_items = page_data[2]
        if self.page_items: self.update_items()
        self.page_choices = self.refine_choices(page_data[4])
        self.valid_choices = [x[1] for x in self.page_choices if x[3]] if self.page_choices else None #Set possible page choices for user
        self.save_gav()

    def refine_choices(self, choices):
        """This function is passed a list of choices in the form [Choice text, destination, requirements], and
        will append a bool to the end of the list if all the choice requirements are satisfied"""
        item_list = self.meta + self.inventory + self.traits
        print(choices)
        if choices == [["", "", ""]]: return None
        for choice in choices:
            choice.append(True)
            choice[2] = re.split("\|", choice[2]) #Split up serperate requirements
            if choice[2] != [""]:
                for req in choice[2]:
                    req = re.split("\_", req) #Split up the item, and whether it is required or forbidden
                    if req[1] in item_list:
                        if req[0] == "no": choice[3] = False
                    else:
                        if req[0] == "have": choice[3] = False
        return(choices)

    def bounce_check(self, bounces):
        """Check conditions passed for bounces (redirecting to other pages)
            Bounces should be in format:
                have_item one/no_item two/redirect|no_item one/redirect"""
        item_list = self.meta + self.inventory + self.traits
        print("bounces:", item_list)
        print("bounces:", bounces)
        bounces = re.sub("\\n", "", bounces)
        print("bounces:", bounces)
        bounces = re.split ("\|", bounces)
        print("bounces:", bounces)
        for i in range(len(bounces)):
            bounce = bounces[i]
            bounce = re.split("/", bounce)
            bounce_items = bounce[:-1]
            bounce = [bounce[-1]]
            for i in range(len(bounce_items)):
                item = bounce_items[i]
                item = re.split("\_", item)
                if item[1] in item_list:
                    item = False if item[0] == "no" else True
                else:
                    item = False if item[0] == "have" else True
                bounce_items[i] = item
            print(bounce_items)
            bounce_items = [x for x in bounce_items if x]
            bounce.append(len(bounce_items))
            bounces[i] = bounce
        bounces = sorted([x for x in bounces if x[1] != 0], key=lambda x: x[1])
        if bounces:
            return(bounces[-1][0])
        else:
            return None

    def update_items(self):
        """Take the list of items gained and lost and updates the gavs attributes as required"""
        item_list = re.split("\|", self.page_items)
        for item in item_list:
            item_commands = re.split("\_", item)
            item_name = item_commands[2]
            print(item_commands)
            if item_commands[0] == "gain":
                the_list = self.item_lists[item_commands[1]]
                if item_name not in self.item_lists[item_commands[1]]: #if item_name not in
                    self.item_lists[item_commands[1]].append(item_name)
            elif item_commands[0] == "lose":
                if item_name in self.item_lists[item_commands[1]]:
                    self.item_lists[item_commands[1]].pop(item_name)

    def reset_gavbot(self):
        """Restore Gavbot to factory settings"""
        self.manager = PageManager()
        self.health = 2
        self.max_health = 3
        self.meta = []
        self.traits = []
        self.inventory = []
        #Note: Getting a very strange error here, if I dont set item lists like this, then item lists remembers the
        #previous gavs items, instead of updating properly? Possibly something to do with attributes.
        self.item_lists = {
            "meta": self.meta,
            "trait": self.traits,
            "inventory": self.inventory
            }
        self.current_act = 0
        self.current_page = "intro"
        self.update_page()
        self.save_gav()
        print(self.meta)
        print(self.item_lists)

    def save_gav(self):
        file_name = "{}saved_gavbots/{}.json".format(self.path, self.owner)
        data = {
            "owner": self.owner,
            "health": self.health,
            "max_health": self.max_health,
            "meta": self.meta,
            "traits": self.traits,
            "inventory": self.inventory,
            "act": self.current_act,
            "page": self.current_page}
        data_dumps = json.dumps(data)
        with open (file_name, "w") as file:
            file.write(data_dumps)

    def load_gav(self, owner):
        file_name = "{}saved_gavbots/{}.json".format(self.path, owner)
        with open(file_name, "r") as file:
            data = json.loads(file.read())
        self.owner = data["owner"]
        self.health = data["health"]
        self.max_health = data["max_health"]
        self.meta = data["meta"]
        self.traits = data["traits"]
        self.inventory = data["inventory"]
        self.current_act = data["act"]
        self.current_page = data["page"]

    path = GavStat()
    owner = GavStat()
    health = GavStat()
    meta = GavStat()
    traits = GavStat()
    inventory = GavStat()
    current_act = GavStat()
    current_page = GavStat()
    pic = GavStat()
    health_pic = GavStat()



if __name__ == "__main__":
    manager = PageManager()
    gav = Gavbot("scripttest", path="")
    gav.path = ""
    gav.current_page = "lobby_chase_yes"
    gav.update_page()
    page = manager.load_page(gav)
    print(page)
    print(gav.meta)
    print(gav.traits)
