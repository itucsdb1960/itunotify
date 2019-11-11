import os
import sys

import psycopg2 as dbapi2


INIT_STATEMENTS = [
    "CREATE TABLE IF NOT EXISTS DUMMY (NUM INTEGER)",
    "INSERT INTO DUMMY VALUES (42)",

    """
	CREATE TABLE IF NOT EXISTS users (
		userid serial primary key,
    	name varchar(40),
    	department varchar(80),
    	studentno varchar(10),
    	grade integer
	);""",

    """
	CREATE TABLE IF NOT EXISTS image (
		imageid serial primary key,
    	image varchar(100)
	);""",

    """
    CREATE TABLE IF NOT EXISTS lostfound (
		postid SERIAL primary key,
		title VARCHAR(32) NOT NULL,
		description VARCHAR(512) NOT NULL,
		userid INTEGER references users(userid),
		LF boolean NOT NULL,
		location VARCHAR(32),
		imageid INTEGER references image(imageid)
	);""",

    """
	CREATE TABLE IF NOT EXISTS responses (
		respid SERIAL primary key,
		postid INTEGER references lostfound(postid),
		response VARCHAR(512) NOT NULL,
		userid INTEGER references users(userid),
		ord integer NOT NULL
	);""",

    """
	CREATE TABLE IF NOT EXISTS item (
		itemid serial primary key,
    	name varchar(100)
	);""",


    """
	CREATE TABLE IF NOT EXISTS message (
		messageid serial primary key,
    	body varchar(500)
	);""",

    """
	CREATE TABLE IF NOT EXISTS selling (
		sellid serial primary key,
    	itemid integer references item(itemid),
	    imageid integer references image(imageid),
	    seller integer references users(userid),
	    shortD varchar(50),
	    price integer
	);""",

    """
	CREATE TABLE IF NOT EXISTS question (
		questionid serial primary key,
	    sellid integer references selling(sellid),
	    messageid integer references message(messageid),
	    ord integer
	);""",

    """
	CREATE TABLE IF NOT EXISTS answer (
		answerid serial primary key,
	    sellid integer references selling(sellid),
	    questionid integer references question(questionid),
	    messageid integer references message(messageid),
	    ord integer
	);""",

    """
	CREATE TABLE IF NOT EXISTS item_info (
	    sellid integer references selling(sellid),
	    messageid integer references message(messageid),
	    primary key (sellid, messageid)
	);"""

]


def initialize(url):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for statement in INIT_STATEMENTS:
            cursor.execute(statement)
        cursor.close()


if __name__ == "__main__":
    url = os.getenv("DATABASE_URL")
    if url is None:
        print("Usage: DATABASE_URL=url python dbinit.py", file=sys.stderr)
        sys.exit(1)
    initialize(url)
