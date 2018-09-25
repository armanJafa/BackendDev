--Dropping tables to clear data from DB for testing--
DROP TABLE IF EXISTS forums;
DROP TABLE IF EXISTS threads;
DROP TABLE IF EXISTS auth_users;
DROP TABLE IF EXISTS posts;

PRAGMA foreign_keys = ON;

CREATE TABLE forums (
	id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	name TEXT NOT NULL,
	creator TEXT NOT NULL,
	FOREIGN KEY(creator) REFERENCES auth_users(username)
);

CREATE TABLE threads (
	id INTEGER NOT NULL,
	forum_id INT NOT NULL,
	title TEXT NOT NULL,
	creator TEXT NOT NULL,
	time_created TEXT NOT NULL,
	FOREIGN KEY(creator) REFERENCES auth_users(username)
);

CREATE TABLE posts (
	forum_id INT NOT NULL,
	thread_id INT NOT NULL,
	body TEXT NOT NULL,
	creator TEXT NOT NULL, 
	created TEXT NOT NULL,
	FOREIGN KEY(creator) REFERENCES auth_users(username)
);

CREATE TABLE auth_users (
	username TEXT PRIMARY KEY NOT NULL UNIQUE,
	password TEXT NOT NULL
);

--Generating test cases--
INSERT INTO auth_users VALUES("alice", "Gr3atPA$$W0Rd");
INSERT INTO auth_users VALUES("bob", "Gr3attPA$$W0Rd");
INSERT INTO auth_users VALUES("charlie", "Gr3attPA$$W0Rd");
INSERT INTO forums VALUES(1, "redis", "alice");
INSERT INTO forums VALUES(2, "mongodb", "bob");
INSERT INTO threads VALUES(1, 1, "Does anyone know how to start Redis?", "bob", "Wed, 05 Sep 2018 16:22:29 GMT");
INSERT INTO threads VALUES(2, 1, "Has anyone heard of Edis?", "charlie", "Tue, 04 Sep 2018 13:18:43 GMT");
INSERT INTO threads VALUES(1, 2, "Ask MongoDB questeions here!", "alice", "Tue, 06 Sep 2018 17:18:43 GMT");
INSERT INTO posts VALUES(1, 1, "I'm trying to connect to MongoDB, but it doesn't seem to be running.", "bob", "Tue, 04 Sep 2018 15:42:28 GMT");
INSERT INTO posts VALUES(1, 1, "Ummm. maybe 'sudo service start mongodb'?", "bob", "Tue, 04 Sep 2018 15:45:36 GMT");
INSERT INTO posts VALUES(2, 1, "It is some new framework for Redis.. disregard..", "charlie", "Tue, 04 Sep 2018 13:49:36 GMT");
