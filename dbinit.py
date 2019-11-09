import os
import sys

import psycopg2 as dbapi2


INIT_STATEMENTS = [
    "CREATE TABLE IF NOT EXISTS DUMMY (NUM INTEGER)",
    "INSERT INTO DUMMY VALUES (42)",

    """
    CREATE TABLE IF NOT EXISTS lostfound (
		postid SERIAL primary key,
		title VARCHAR(32) NOT NULL,
		description VARCHAR(512) NOT NULL,
		userid INTEGER references user,
		LF boolean NOT NULL,
		location VARCHAR(32),
		imageid INTEGER references image,
	);""",

	"""
	CREATE TABLE IF NOT EXISTS responses (
		respid SERIAL primary key,
		postid INTEGER references lostfound,
		response VARCHAR(512) NOT NULL,
		userid INTEGER references user,
		order integer NOT NULL
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
