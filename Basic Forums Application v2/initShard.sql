DROP TABLE IF EXISTS posts;

CREATE TABLE posts (
	forum_id INT NOT NULL,
	thread_id INT NOT NULL,
	body TEXT NOT NULL,
	creator TEXT NOT NULL,
	created TEXT NOT NULL,
	FOREIGN KEY(creator) REFERENCES auth_users(username)
);