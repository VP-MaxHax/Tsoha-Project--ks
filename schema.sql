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

CREATE TABLE messages (
	id serial PRIMARY KEY,
	content VARCHAR ( 100 ),
	posted_by INTEGER,
	is_for_members BOOLEAN NOT NULL
	hidden BOOLEAN
);

CREATE TABLE comments (
	comment_id serial PRIMARY KEY,
	content VARCHAR ( 100 ),
	source_msg INTEGER,
	posted_by VARCHAR,
	poster_id INTEGER,
	hidden BOOLEAN
);

CREATE TABLE follows (
	id serial PRIMARY KEY,
	user_id INTEGER NOT NULL,
	following_id INTEGER NOT NULL
);

CREATE TABLE user_log (
	id serial PRIMARY KEY,
	user_id INTEGER,
	action VARCHAR,
	time TIMESTAMP
);