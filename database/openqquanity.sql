-- Create user
CREATE USER openq_user WITH PASSWORD 'postgres1234';

-- Create database
CREATE DATABASE openquantify;

-- Grant access
GRANT ALL PRIVILEGES ON DATABASE openquantify TO openq_user;
