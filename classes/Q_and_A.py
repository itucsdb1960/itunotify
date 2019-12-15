class Question:
    def __init__(self, questionid, q_body, user_no, user_name, sellid, color, last_update, share_time, anonymous):

        self.questionid = questionid
        self.q_body = q_body
        self.user_no = user_no
        self.user_name = user_name
        self.sellid = sellid
        self.color = color
        self.last_update = last_update
        self.share_time = share_time
        self.anonymous = anonymous


class Answer:
    def __init__(self, answerid, questionid, ans_body, user_no, user_name, sellid, color, last_update, share_time, anonymous):

        self.answerid = answerid
        self.questionid = questionid
        self.ans_body = ans_body
        self.user_no = user_no
        self.user_name = user_name
        self.sellid = sellid
        self.color = color
        self.last_update = last_update
        self.share_time = share_time
        self.anonymous = anonymous
