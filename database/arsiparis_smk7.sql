-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Nov 29, 2025 at 02:07 PM
-- Server version: 8.0.36
-- PHP Version: 8.1.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `arsiparis_smk7`
--

-- --------------------------------------------------------

--
-- Table structure for table `classification`
--

CREATE TABLE `classification` (
  `id` int NOT NULL,
  `name` varchar(50) NOT NULL,
  `code` varchar(3) NOT NULL,
  `description` text,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now())
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `incoming_letter`
--

CREATE TABLE `incoming_letter` (
  `id` int NOT NULL,
  `number` varchar(50) NOT NULL,
  `letter_date` datetime NOT NULL,
  `received_date` datetime NOT NULL,
  `sender` varchar(100) NOT NULL,
  `subject` varchar(255) NOT NULL,
  `attachment_path` varchar(255) DEFAULT NULL,
  `classification_id` int NOT NULL,
  `user_id` int NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now())
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `log`
--

CREATE TABLE `log` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `action` text NOT NULL,
  `timestamp` datetime NOT NULL DEFAULT (now())
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `log`
--

INSERT INTO `log` (`id`, `user_id`, `action`, `timestamp`) VALUES
(1, 1, 'Pengguna melakukan login.', '2025-11-29 20:38:34'),
(2, 1, 'Pengguna membuat user baru dengan NUPTK: \'9993839\'.', '2025-11-29 20:38:42'),
(3, 1, 'Pengguna memperbarui data (status) pengguna NUPTK: \'9993839\'.', '2025-11-29 20:38:46'),
(4, 1, 'Pengguna \'AryaSeptiaputra\' menambahkan surat masuk nomor: \'IN-203846\'.', '2025-11-29 20:38:48'),
(5, 1, 'Pengguna \'AryaSeptiaputra\' mengupdate data (subject) pada surat masuk nomor: \'IN-203846\'.', '2025-11-29 20:38:50'),
(6, 1, 'Pengguna \'AryaSeptiaputra\' menambahkan surat keluar nomor: \'OUT-203850\'.', '2025-11-29 20:38:52'),
(7, 1, 'Pengguna \'AryaSeptiaputra\' menghapus surat masuk nomor: \'IN-203846\'.', '2025-11-29 20:38:54'),
(8, 1, 'Pengguna \'AryaSeptiaputra\' menghapus surat keluar nomor: \'OUT-203850\'.', '2025-11-29 20:38:57'),
(9, 1, 'Menghapus user NUPTK: 9993839', '2025-11-29 20:38:59');

-- --------------------------------------------------------

--
-- Table structure for table `outgoing_letter`
--

CREATE TABLE `outgoing_letter` (
  `id` int NOT NULL,
  `number` varchar(50) NOT NULL,
  `letter_date` datetime NOT NULL,
  `sent_date` datetime NOT NULL,
  `destination` varchar(100) NOT NULL,
  `subject` varchar(255) DEFAULT NULL,
  `is_decree` tinyint(1) NOT NULL,
  `attachment_path` varchar(255) DEFAULT NULL,
  `classification_id` int NOT NULL,
  `user_id` int NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now())
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id` int NOT NULL,
  `nuptk` varchar(16) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(200) NOT NULL,
  `role` enum('headmaster','admin','teacher') NOT NULL,
  `status` enum('active','inactive') NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now())
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id`, `nuptk`, `username`, `password`, `role`, `status`, `created_at`, `updated_at`) VALUES
(1, '152022190', 'AryaSeptiaputra', '$2b$12$SZDnDLS9AqC1dSPDvmG2pOx1YjkzGUkcjidTlgeqftvGBwJSMwXmG', 'admin', 'active', '2025-11-29 20:38:28', '2025-11-29 20:38:28');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `classification`
--
ALTER TABLE `classification`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_classification_name` (`name`),
  ADD UNIQUE KEY `ix_classification_code` (`code`),
  ADD KEY `ix_classification_id` (`id`);

--
-- Indexes for table `incoming_letter`
--
ALTER TABLE `incoming_letter`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_incoming_letter_number` (`number`),
  ADD KEY `ix_incoming_letter_letter_date` (`letter_date`),
  ADD KEY `ix_incoming_letter_classification_id` (`classification_id`),
  ADD KEY `ix_incoming_letter_user_id` (`user_id`),
  ADD KEY `ix_incoming_letter_sender` (`sender`),
  ADD KEY `ix_incoming_letter_id` (`id`),
  ADD KEY `ix_incoming_letter_received_date` (`received_date`);

--
-- Indexes for table `log`
--
ALTER TABLE `log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_log_id` (`id`),
  ADD KEY `ix_log_user_id` (`user_id`),
  ADD KEY `ix_log_timestamp` (`timestamp`);

--
-- Indexes for table `outgoing_letter`
--
ALTER TABLE `outgoing_letter`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_outgoing_letter_classification_id` (`classification_id`),
  ADD KEY `ix_outgoing_letter_sent_date` (`sent_date`),
  ADD KEY `ix_outgoing_letter_number` (`number`),
  ADD KEY `ix_outgoing_letter_id` (`id`),
  ADD KEY `ix_outgoing_letter_destination` (`destination`),
  ADD KEY `ix_outgoing_letter_user_id` (`user_id`),
  ADD KEY `ix_outgoing_letter_is_decree` (`is_decree`),
  ADD KEY `ix_outgoing_letter_letter_date` (`letter_date`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_user_nuptk` (`nuptk`),
  ADD UNIQUE KEY `ix_user_username` (`username`),
  ADD KEY `ix_user_id` (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `classification`
--
ALTER TABLE `classification`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `incoming_letter`
--
ALTER TABLE `incoming_letter`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `log`
--
ALTER TABLE `log`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `outgoing_letter`
--
ALTER TABLE `outgoing_letter`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `incoming_letter`
--
ALTER TABLE `incoming_letter`
  ADD CONSTRAINT `incoming_letter_ibfk_1` FOREIGN KEY (`classification_id`) REFERENCES `classification` (`id`),
  ADD CONSTRAINT `incoming_letter_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);

--
-- Constraints for table `log`
--
ALTER TABLE `log`
  ADD CONSTRAINT `log_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);

--
-- Constraints for table `outgoing_letter`
--
ALTER TABLE `outgoing_letter`
  ADD CONSTRAINT `outgoing_letter_ibfk_1` FOREIGN KEY (`classification_id`) REFERENCES `classification` (`id`),
  ADD CONSTRAINT `outgoing_letter_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
