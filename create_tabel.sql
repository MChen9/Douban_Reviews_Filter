
CREATE TABLE testdb.Douban_Users(
  #`id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(50) DEFAULT NULL,
  `status` tinyint(1) DEFAULT '1',
  `user_name` varchar(50) DEFAULT NULL,
  `intro` text,
  `followers` varchar(50) DEFAULT NULL,
  `follow` varchar(50) DEFAULT NULL,
  `watched_movies` varchar(50) DEFAULT NULL,
  #PRIMARY KEY (`id`),
  UNIQUE KEY (`user_id`),
  KEY `weiyi` (`user_name`) USING BTREE
) ENGINE=InnoDB  AUTO_INCREMENT=0000000 DEFAULT CHARSET=utf8
#AUTO_INCREMENT=0000000