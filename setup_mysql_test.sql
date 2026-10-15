-- Prepare the test MySQL database and user.
CREATE DATABASE IF NOT EXISTS hbnb_test_db;

CREATE USER IF NOT EXISTS 'hbnb_test'@'localhost'
IDENTIFIED BY 'hbnb_test_pwd';

ALTER USER 'hbnb_test'@'localhost'
IDENTIFIED BY 'hbnb_test_pwd';

-- Ensure an existing user has no privileges outside the requested databases.
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'hbnb_test'@'localhost';

GRANT ALL PRIVILEGES ON hbnb_test_db.* TO 'hbnb_test'@'localhost';
GRANT SELECT ON performance_schema.* TO 'hbnb_test'@'localhost';
