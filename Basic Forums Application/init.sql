CREATE TABLE USERS (
        username varchar(255)  NOT NULL,
        userpass password  NOT NULL
)


CREATE TABLE FORUMS()
        id       integer PRIMARY KEY,
        formname varchar(255)  NOT NULL,
        creator  varchar(255)
)

CREATE [UNIQUE] INDEX id on TABLE FORUMS(id)

INSERT INTO USERS (username, userpass)
    VALUES ('tim','password')

INSERT INTO USERS (id, formname, creator)
    VALUES (id,'cassandra', 'tim')
