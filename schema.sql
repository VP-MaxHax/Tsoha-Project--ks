Users table:
CREATE TABLE users (
	user_id serial PRIMARY KEY,
	username VARCHAR ( 50 ) UNIQUE NOT NULL,
	password VARCHAR NOT NULL,
	is_sub BOOLEAN NOT NULL,
	sub_exp TIMESTAMP,
	is_active BOOLEAN NOT NULL,
	is_staff BOOLEAN NOT NULL,
    last_login TIMESTAMP 
);

Messages table:
CREATE TABLE messages (
	id serial PRIMARY KEY,
	content VARCHAR ( 100 ),
	posted_by INTEGER,
	is_for_members BOOLEAN NOT NULL
	hidden BOOLEAN
);

Comments table:
CREATE TABLE comments (
	comment_id serial PRIMARY KEY,
	content VARCHAR ( 100 ),
	source_msg INTEGER,
	posted_by VARCHAR,
	hidden BOOLEAN
);

follows table:
CREATE TABLE follows (
	id serial PRIMARY KEY,
	user_id INTEGER NOT NULL,
	following_id INTEGER NOT NULL
);