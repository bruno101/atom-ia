-- This script runs automatically when the Oracle container is created for the first time.
-- It sets up a dedicated user and creates the table for storing vector data.
 
ALTER SESSION SET CONTAINER = FREEPDB1;
 
-- Note: The following command is often necessary to run scripts that create users.
ALTER SESSION SET "_ORACLE_SCRIPT"=true;
 
-- Create a new user/schema for our application
CREATE USER app_user IDENTIFIED BY yourAppPassword_456;
 
-- Grant necessary permissions to the new user
GRANT CONNECT, RESOURCE TO app_user;
GRANT UNLIMITED TABLESPACE TO app_user;
-- Grant permission to create and use vector indexes and data types
GRANT CREATE VECTOR, READ ANY VECTOR, WRITE ANY VECTOR TO app_user;
GRANT CREATE ANY VECTOR INDEX, ALTER ANY VECTOR INDEX, DROP ANY VECTOR INDEX TO app_user;
 
 
 
-- Create the 'documents' table under the 'app_user' schema
CREATE TABLE app_user.documents (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title VARCHAR2(255) NOT NULL,
    url VARCHAR2(2048),
    text CLOB,
    -- VECTOR type with 1024 dimensions using 32-bit floating point numbers
    -- This is ideal for storing embeddings from many popular AI models.
    vector VECTOR(1024, FLOAT32)
);
 
-- Exit the SQL*Plus session
EXIT;