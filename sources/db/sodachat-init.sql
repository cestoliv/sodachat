BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS users (
	uid	TEXT UNIQUE,
	name	TEXT,
	username	TEXT UNIQUE,
	password_hash	TEXT,
	type	TEXT,
	PRIMARY KEY(uid, username)
);
CREATE TABLE IF NOT EXISTS messages (
	id	TEXT,
	timestamp	TIMESTAMP,
	sender_uid	TEXT,
	receiver_uid	TEXT,
	content	TEXT,
	seen	INT,
	PRIMARY KEY(id),
	FOREIGN KEY (sender_uid) REFERENCES users(uid),
	FOREIGN KEY (receiver_uid) REFERENCES users(uid)
);
CREATE TABLE IF NOT EXISTS contacts (
	uid	TEXT,
	timestamp	TIMESTAMP,
	contact_uid	TEXT,
	blocked	INTEGER,
	FOREIGN KEY(contact_uid) REFERENCES users(uid)
);
COMMIT;

