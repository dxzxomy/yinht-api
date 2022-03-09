-- ----------------------------
-- 资源建设管理平台数据表结构
-- Database structure for kscrcdn
-- ----------------------------

-- mysql -h120.92.215.37 -ukscrcdn -P13306 -p
-- password by mingguangzhen
--

-- kscrcdn!@#1243

-- DROP DATABASE IF EXISTS `yinht`;
-- CREATE DATABASE `yinht` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `yinht`;

-- ----------------------------
-- Table structure for navi_list
-- ----------------------------
DROP TABLE IF EXISTS `navi_list`;
CREATE TABLE `navi_list` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(28) NOT NULL COMMENT '名称',
  `url` varchar(128) DEFAULT NULL COMMENT '地址',
  `icon` varchar(256) DEFAULT NULL COMMENT '图片',
  `pnode` int(11) NOT NULL  COMMENT '父节点',
  `level` int(11) NOT NULL COMMENT '节点层级',
  `descr` text DEFAULT NULL COMMENT '描述',
  `ctime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `utime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='导航管理';

-- ----------------------------
-- Table structure for news
-- ----------------------------
DROP TABLE IF EXISTS `news`;
CREATE TABLE `news` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(64) NOT NULL COMMENT '标题',
  `image` varchar(128) DEFAULT NULL COMMENT '图片',
  `description` varchar(128) DEFAULT NULL COMMENT '描述',
  `ctime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `utime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='导航管理';