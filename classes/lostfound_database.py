from copy import copy

class LFPost():
	def __init__(self, title, description, userid, LF, location=None, imageid=None):
		self.title = title
		self.description = description
		self.userid = userid
		self.LF = LF
		self.location = location
		self.imageid = imageid


class LFDatabase():
	# Constructor
	def __init__(self, postlist=None):
		self.posts = {}
		self.last_postid = 0

	# Database management methods
	def	add_post(self, lfpost):
		self.last_postid += 1
		self.posts[self.last_postid] = lfpost

	def delete_post(self, postid):
		if postid in self.posts:
			del self.posts[postid]

	def get_post(self, postid):
		lfpost = copy(self.posts.get(postid))
		return lfpost

	def get_all_posts(self):
		posts = copy(self.posts)
		return posts
