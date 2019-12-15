class SellItem:
    def __init__(self, sellid, item_name, price, seller_name, seller_no, n_questions, n_answers, share_time, item_info=None, shortD=None, image=None):
        if(shortD == None):
            shortD = "No description."
        if(image == None):
            image = "no image available"

        self.sellid = sellid
        self.item_name = item_name
        self.price = price
        self.seller_name = seller_name
        self.seller_no = seller_no
        self.n_questions = n_questions
        self.n_answers = n_answers
        self.share_time = share_time
        self.item_info = item_info
        self.shortD = shortD
        self.image = image

    def set_nq(n_questions):
        self.n_questions = n_questions

    def set_na(n_answers):
        self.n_answers = n_answers
