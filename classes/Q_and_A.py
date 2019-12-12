class Question:
    def __init__(self, questionid, q_body, user_no, user_name, sellid, share_time):

        self.questionid = questionid
        self.q_body = q_body
        self.user_no = user_no
        self.user_name = user_name
        self.sellid = sellid
        self.share_time = share_time


class Answer:
    def __init__(self, answerid, questionid, ans_body, user_no, user_name, sellid, share_time):

        self.answerid = answerid
        self.questionid = questionid
        self.ans_body = ans_body
        self.user_no = user_no
        self.user_name = user_name
        self.sellid = sellid
        self.share_time = share_time
