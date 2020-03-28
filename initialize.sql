-- Initialization script for testing purposes
DROP DATABASE IF EXISTS budgetBook;
CREATE DATABASE budgetBook;
USE budgetBook;
SOURCE tables.sql;
SET FOREIGN_KEY_CHECKS=0;