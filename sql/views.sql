
-- DOD_INSTANCES View
CREATE VIEW DOD_INSTANCES AS
SELECT USERNAME, DB_NAME, E_GROUP, CATEGORY, CREATION_DATE, EXPIRY_DATE, DB_TYPE, 0 DB_SIZE, 0 NO_CONNECTIONS, PROJECT, DESCRIPTION, VERSION, MASTER, SLAVE, HOST, STATE, STATUS
FROM fo_instance;

