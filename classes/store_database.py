from classes.sell_item import SellItem


class StoreDatabase:
    def __init__(self):
        self.selling = {}
        self.last_sellid = 0

        # normally get selling items from the sql database!

    def add_selling_item(self, sellItem):
        self.last_sellid += 1
        self.selling[self.last_sellid] = sellItem

        # handle sql database!

    def delete_selling_item(self, sellid):
        if sellid in self.selling:
            del self.selling[sellid]

        # handle sql database!

    def get_selling_item(self, sellid):
        sellItem = self.selling.get(sellid)
        if sellItem is None:
            return None
        sellItem_new = SellItem(sellItem.item_name, sellItem.price, sellItem.seller, sellItem.n_questions, sellItem.n_answers, shortD=sellItem.shortD, image=sellItem.image)
        return sellItem_new

    def get_all_selling_items(self):
        sellingItems = []
        for sellid, sellItem in self.selling.items():
            sellItem_new = SellItem(sellItem.item_name, sellItem.price, sellItem.seller, sellItem.n_questions, sellItem.n_answers, shortD=sellItem.shortD, image=sellItem.image)
            sellingItems.append((sellid, sellItem_new))
        return sellingItems
