--
-- Файл сгенерирован с помощью SQLiteStudio v3.4.1 в Чт мар 27 14:23:12 2025
--
-- Использованная кодировка текста: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Таблица: input
DROP TABLE IF EXISTS input;
CREATE TABLE IF NOT EXISTS input (
	id INTEGER NOT NULL, 
	telegram_id INTEGER NOT NULL, 
	chat_id INTEGER NOT NULL, 
	data JSON NOT NULL, 
	PRIMARY KEY (id)
);

-- Таблица: output
DROP TABLE IF EXISTS output;
CREATE TABLE IF NOT EXISTS output (
	id INTEGER NOT NULL, 
	telegram_id INTEGER NOT NULL, 
	chat_id INTEGER NOT NULL, 
	data JSON NOT NULL, 
	PRIMARY KEY (id)
);

-- Таблица: rejected
DROP TABLE IF EXISTS rejected;
CREATE TABLE IF NOT EXISTS rejected (
	id INTEGER NOT NULL, 
	telegram_id INTEGER NOT NULL, 
	chat_id INTEGER NOT NULL, 
	data JSON NOT NULL, 
	PRIMARY KEY (id)
);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
