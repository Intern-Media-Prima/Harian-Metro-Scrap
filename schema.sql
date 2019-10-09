DROP SCHEMA IF EXISTS hmetro;

CREATE SCHEMA hmetro;
USE hmetro;

DROP TABLE IF EXISTS category;

CREATE TABLE category (
	ID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	value VARCHAR(255) NOT NULL
);

INSERT INTO category (value) VALUES (
	'utama'
),(
	'mutakhir'
),(
	'global'
),(
	'arena'
),(
	'rap'
),(
	'bisnes'
),(
	'metrotv'
),(
	'belanjawan2020'
);

DROP TABLE IF EXISTS article;

CREATE TABLE article (
	ID VARCHAR(100) PRIMARY KEY NOT NULL,
	category_id INT NOT NULL,
	year INT NOT NULL,
	month INT NOT NULL, 
	title VARCHAR(255) NOT NULL,
	content TEXT NOT NULL,
	FOREIGN KEY(category_id) REFERENCES category(ID)
);