-- Owner account
CREATE USER 'admin'@'%' IDENTIFIED BY 'pass';
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%' WITH GRANT OPTION;
ALTER USER 'admin'@'%' PASSWORD EXPIRE;

-- Set the password for root and anonymous user. Required for MySQL 5.7.x
SET PASSWORD FOR 'root'@'localhost' = PASSWORD('pass');

FLUSH PRIVILEGES;
