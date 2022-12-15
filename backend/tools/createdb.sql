CREATE TABLE `users` (
	`id` INT(16) NOT NULL AUTO_INCREMENT,
	`username` varchar(255) NOT NULL UNIQUE,
	`password` varchar(255) NOT NULL,
	`salt` varchar(255) NOT NULL,
	`email` varchar(255) NOT NULL UNIQUE,
	PRIMARY KEY (`id`)
);