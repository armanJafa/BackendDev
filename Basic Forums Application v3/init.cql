--Dropping tables to clear data from DB for testing--
DROP KEYSPACE IF EXISTS forum;
CREATE KEYSPACE forum
	WITH REPLICATION = {
		'class' : 'SimpleStrategy',
		'replication_factor': 3
		};


USE forum;

DROP TABLE IF EXISTS forums;
DROP TABLE IF EXISTS threads;
DROP TABLE IF EXISTS auth_users;
DROP TABLE IF EXISTS posts;

CREATE TABLE forums (
	id int,
	name text,
	creator text,
	PRIMARY KEY (id)
);

CREATE TABLE threads (
	id int,
	forum_id int,
	title text,
	creator text,
	time_created text,
	PRIMARY KEY(id)
);

CREATE TABLE auth_users (
	username text,
	password text,
	PRIMARY KEY(username)
);

--Generating test cases--
INSERT INTO auth_users VALUES("alice", "Gr3atPA$$W0Rd");
INSERT INTO auth_users VALUES("bob", "Gr3attPA$$W0Rd");
INSERT INTO auth_users VALUES("charlie", "Gr3attPA$$W0Rd");
INSERT INTO forums VALUES(1, "redis", "alice");
INSERT INTO forums VALUES(2, "GENERAL", "bob");
INSERT INTO threads VALUES(1, 1, "Does anyone know how to start Redis?", "bob", "Wed, 05 Sep 2018 16:22:29 GMT");
INSERT INTO threads VALUES(2, 1, "Has anyone heard of Edis?", "charlie", "Tue, 04 Sep 2018 13:18:43 GMT");
INSERT INTO threads VALUES(3, 1, "Ask MongoDB questeions here!", "alice", "Tue, 06 Sep 2018 17:18:43 GMT");
INSERT INTO threads VALUES(4, 1, "Ask C++ questeions here!", "alice", "Tue, 06 Sep 2018 17:18:43 GMT");
INSERT INTO threads VALUES(1, 2, "Ask PYTHON questeions here!", "alice", "Tue, 06 Sep 2018 17:18:43 GMT");
INSERT INTO threads VALUES(2, 2, "Ask Java questeions here!", "alice", "Tue, 06 Sep 2018 17:18:43 GMT");
INSERT INTO threads VALUES(3, 2, "Ask JS questeions here!", "bob", "Tue, 06 Sep 2018 17:18:43 GMT");
INSERT INTO threads VALUES(4, 2, "Ask Redis questeions here!", "charlie", "Tue, 06 Sep 2018 17:18:43 GMT");
INSERT INTO threads VALUES(5, 2, "Ask C questeions here!", "alice", "Tue, 06 Sep 2018 17:18:43 GMT");
INSERT INTO threads VALUES(6, 2, "Ask FOO questeions here!", "alice", "Tue, 06 Sep 2018 17:18:43 GMT");
