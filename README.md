## 数据库结构

```mysql
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for admin
-- ----------------------------
DROP TABLE IF EXISTS `admin`;
CREATE TABLE `admin`  (
  `admin_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `name` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `password` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `permission` int(11) NOT NULL,
  PRIMARY KEY (`admin_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for book
-- ----------------------------
DROP TABLE IF EXISTS `book`;
CREATE TABLE `book`  (
  `book_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `ISBN` varchar(15) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `name` varchar(200) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `author` varchar(100) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `price` float NOT NULL,
  `press` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`book_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for bookslip
-- ----------------------------
DROP TABLE IF EXISTS `bookslip`;
CREATE TABLE `bookslip`  (
  `slip_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `book_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `card_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `borrowing_time` int(11) NOT NULL,
  `due_time` int(11) NOT NULL,
  `return_time` int(11) NULL DEFAULT NULL,
  `is_repaid` tinyint(1) NOT NULL,
  PRIMARY KEY (`slip_id`, `book_id`) USING BTREE,
  INDEX `card_id`(`card_id`) USING BTREE,
  INDEX `book_id`(`book_id`) USING BTREE,
  CONSTRAINT `bookslip_ibfk_1` FOREIGN KEY (`card_id`) REFERENCES `card` (`card_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `bookslip_ibfk_2` FOREIGN KEY (`book_id`) REFERENCES `book` (`book_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for card
-- ----------------------------
DROP TABLE IF EXISTS `card`;
CREATE TABLE `card`  (
  `card_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `date` int(11) NOT NULL,
  `cardholder` varchar(10) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `telephone` varchar(11) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `email` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`card_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_bin ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;	
```