DROP TABLE IF EXISTS posts;

CREATE TABLE posts (
	guid varchar(50) PRIMARY KEY,
	forum_id INT NOT NULL,
	thread_id INT NOT NULL,
	body TEXT NOT NULL,
	creator TEXT NOT NULL,
	created datetime NOT NULL
);

-- INSERT INTO posts VALUES(1, 1, "I'm trying to connect to MongoDB, but it doesn't seem to be running.", "bob", "Tue, 04 Sep 2018 15:42:28 GMT");
-- INSERT INTO posts VALUES(1, 1, "Ummm. maybe 'sudo service start mongodb'?", "bob", "Tue, 04 Sep 2018 15:45:36 GMT");
-- INSERT INTO posts VALUES(1, 2, "I need help with it", "charlie", "Tue, 06 Sep 2018 17:18:43 GMT");
-- INSERT INTO posts VALUES(2, 1, "It is some new framework for Redis.. disregard..", "charlie", "Tue, 04 Sep 2018 13:49:36 GMT");

