CREATE TABLE USERS {
        username varchar(255)  NOT NULL,
        userpass password  NOT NULL
};


CREATE TABLE FORMS{
        id       integer PRIMARY KEY,
        formname varchar(255)  NOT NULL,
        creator  varchar(255)
};

CREATE [unique] INDEX id on TABLE FORMS(id)

INSERT INTO USERS (username, userpass)
    VALUES ('tim','password')

INSERT INTO USERS (id, formname, creator)
    VALUES (id,'cassandra', 'tim')