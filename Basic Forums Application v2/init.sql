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
	id INTEGER,
	forum_id INT NOT NULL ,
	title TEXT NOT NULL,
	creator TEXT NOT NULL,
	time_created datetime NOT NULL,
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
INSERT INTO forums VALUES(2, "GENERAL", "bob");
