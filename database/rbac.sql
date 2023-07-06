-- 管理员表
CREATE TABLE user (
  id int(11) NOT NULL AUTO_INCREMENT,
  username varchar(30) UNIQUE NOT NULL DEFAULT '' COMMENT '用户名',
  password char(32) NOT NULL DEFAULT '' COMMENT '密码',
  PRIMARY KEY(id)
)ENGINE= InnoDB DEFAULT CHARSET=utf8;

-- 角色表
CREATE TABLE role(
  id int(11) NOT NULL AUTO_INCREMENT,
  role_name varchar(30) UNIQUE NOT NULL DEFAULT '' COMMENT '角色名称',
  PRIMARY KEY(id)
)ENGINE= InnoDB DEFAULT CHARSET=utf8;


-- 用户角色的中间表
CREATE TABLE user_role(
  id int(11) NOT NULL AUTO_INCREMENT,
  user_id int(11) NOT NULL DEFAULT 0 COMMENT '用户ID',
  role_id int(11) NOT NULL DEFAULT 0 COMMENT '角色ID',
  PRIMARY KEY(id)
)ENGINE= InnoDB DEFAULT CHARSET=utf8;

-- 权限表
CREATE TABLE rule(
  id int(11) NOT NULL AUTO_INCREMENT,
  rule_name varchar(30) UNIQUE NOT NULL DEFAULT '' COMMENT '权限名称',
  module_name varchar(30) NOT NULL DEFAULT '' COMMENT '模型名称',
  controller_name varchar(30) NOT NULL DEFAULT '' COMMENT '控制器名称',
  action_name varchar(30) NOT NULL DEFAULT '' COMMENT '方法名称',
  parent_id int(11) not NULL DEFAULT 0 COMMENT '上级权限ID 0表示顶级权限',
  is_show tinyint(1) not NULL DEFAULT 1 COMMENT '是否导航菜单显示 1显示 0不显示',
  PRIMARY KEY(id)
)ENGINE= InnoDB DEFAULT CHARSET=utf8;

-- 角色权限中间表
CREATE TABLE role_rule(
  id int(11) NOT NULL AUTO_INCREMENT,
  role_id int(11) NOT NULL DEFAULT 0 COMMENT '角色ID',
  rule_id int(11) NOT NULL DEFAULT 0 COMMENT '权限ID',
  PRIMARY KEY(id)
)ENGINE= InnoDB DEFAULT CHARSET=utf8;

