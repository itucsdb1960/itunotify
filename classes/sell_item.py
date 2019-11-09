class SellItem:
    def __init__(self, item_name, price, seller, n_questions, n_answers, shortD=None, image=None):
        if(shortD == None):
            shortD = "No description."
        if(image == None):
            image = "No image available."

        self.item_name = item_name
        self.price = price
        self.seller = seller
        self.n_questions = n_questions
        self.n_answers = n_answers
        self.shortD = shortD
        self.image = image

    def set_nq(n_questions):
        self.n_questions = n_questions

    def set_na(n_answers):
        self.n_answers = n_answers
