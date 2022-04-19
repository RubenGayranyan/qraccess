-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Хост: 127.0.0.1:3306
-- Время создания: Апр 15 2022 г., 12:00
-- Версия сервера: 5.7.33
-- Версия PHP: 7.4.27

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- База данных: `telegram`
--

-- --------------------------------------------------------

--
-- Структура таблицы `event1`
--

CREATE TABLE `event1` (
  `rKey` int(11) NOT NULL,
  `unicalID` varchar(24) COLLATE utf8mb4_unicode_ci NOT NULL,
  `userID` int(11) NOT NULL,
  `userName` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fName` varchar(24) COLLATE utf8mb4_unicode_ci NOT NULL,
  `lName` varchar(24) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `rDate` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `cDate` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `event1`
--
ALTER TABLE `event1`
  ADD PRIMARY KEY (`rKey`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `event1`
--
ALTER TABLE `event1`
  MODIFY `rKey` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
