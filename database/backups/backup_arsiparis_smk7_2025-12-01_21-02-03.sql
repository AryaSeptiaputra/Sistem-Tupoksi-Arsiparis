-- MySQL dump 10.13  Distrib 8.0.30, for Win64 (x86_64)
--
-- Host: localhost    Database: arsiparis_smk7
-- ------------------------------------------------------
-- Server version	8.0.36

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `backup`
--

DROP TABLE IF EXISTS `backup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `backup` (
  `id` int NOT NULL AUTO_INCREMENT,
  `filename` varchar(255) DEFAULT NULL,
  `status` varchar(50) NOT NULL,
  `message` text,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_backup_user_id` (`user_id`),
  KEY `ix_backup_id` (`id`),
  CONSTRAINT `backup_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `backup`
--

LOCK TABLES `backup` WRITE;
/*!40000 ALTER TABLE `backup` DISABLE KEYS */;
INSERT INTO `backup` VALUES (1,'backup_arsiparis_smk7_2025-12-01_20-48-18.sql','SUCCESS','Database backup created successfully.','2025-12-01 20:48:18',1),(2,'backup_arsiparis_smk7_2025-12-01_20-56-15.sql','SUCCESS','Database backup created successfully.','2025-12-01 20:56:15',1),(3,'backup_arsiparis_smk7_2025-12-01_21-00-56.sql','SUCCESS','Database backup created successfully.','2025-12-01 21:00:56',1);
/*!40000 ALTER TABLE `backup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `classification`
--

DROP TABLE IF EXISTS `classification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `classification` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `code` varchar(3) NOT NULL,
  `description` text,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_classification_name` (`name`),
  UNIQUE KEY `ix_classification_code` (`code`),
  KEY `ix_classification_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classification`
--

LOCK TABLES `classification` WRITE;
/*!40000 ALTER TABLE `classification` DISABLE KEYS */;
INSERT INTO `classification` VALUES (4,'Surat Undangan Resmi','UND',NULL,'2025-12-01 21:01:33','2025-12-01 21:01:37');
/*!40000 ALTER TABLE `classification` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `diploma`
--

DROP TABLE IF EXISTS `diploma`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `diploma` (
  `id` int NOT NULL AUTO_INCREMENT,
  `number` varchar(50) NOT NULL,
  `student_name` varchar(100) NOT NULL,
  `major` varchar(100) NOT NULL,
  `academic_year` varchar(9) NOT NULL,
  `is_collected` tinyint(1) NOT NULL,
  `collected_at` datetime DEFAULT NULL,
  `attachment_path` varchar(255) DEFAULT NULL,
  `user_id` int NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_diploma_number` (`number`),
  KEY `user_id` (`user_id`),
  KEY `ix_diploma_id` (`id`),
  KEY `ix_diploma_major` (`major`),
  KEY `ix_diploma_student_name` (`student_name`),
  KEY `ix_diploma_academic_year` (`academic_year`),
  CONSTRAINT `diploma_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `diploma`
--

LOCK TABLES `diploma` WRITE;
/*!40000 ALTER TABLE `diploma` DISABLE KEYS */;
INSERT INTO `diploma` VALUES (1,'DN-210155','Siswa SMK Test (Revisi)','Teknik Komputer Jaringan','2024/2025',1,'2025-12-01 21:02:02',NULL,1,'2025-12-01 21:01:58','2025-12-01 21:02:02');
/*!40000 ALTER TABLE `diploma` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `incoming_letter`
--

DROP TABLE IF EXISTS `incoming_letter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `incoming_letter` (
  `id` int NOT NULL AUTO_INCREMENT,
  `number` varchar(50) NOT NULL,
  `letter_date` datetime NOT NULL,
  `received_date` datetime NOT NULL,
  `sender` varchar(100) NOT NULL,
  `subject` varchar(255) NOT NULL,
  `attachment_path` varchar(255) DEFAULT NULL,
  `classification_id` int NOT NULL,
  `user_id` int NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_incoming_letter_number` (`number`),
  KEY `ix_incoming_letter_received_date` (`received_date`),
  KEY `ix_incoming_letter_sender` (`sender`),
  KEY `ix_incoming_letter_user_id` (`user_id`),
  KEY `ix_incoming_letter_classification_id` (`classification_id`),
  KEY `ix_incoming_letter_id` (`id`),
  KEY `ix_incoming_letter_letter_date` (`letter_date`),
  CONSTRAINT `incoming_letter_ibfk_1` FOREIGN KEY (`classification_id`) REFERENCES `classification` (`id`),
  CONSTRAINT `incoming_letter_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `incoming_letter`
--

LOCK TABLES `incoming_letter` WRITE;
/*!40000 ALTER TABLE `incoming_letter` DISABLE KEYS */;
INSERT INTO `incoming_letter` VALUES (4,'IN-210143','2025-12-01 00:00:00','2025-12-01 00:00:00','Dinas Pendidikan','Undangan Rapat REVISI',NULL,4,1,'2025-12-01 21:01:45','2025-12-01 21:01:49');
/*!40000 ALTER TABLE `incoming_letter` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `log`
--

DROP TABLE IF EXISTS `log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `action` text NOT NULL,
  `timestamp` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `ix_log_id` (`id`),
  KEY `ix_log_user_id` (`user_id`),
  KEY `ix_log_timestamp` (`timestamp`),
  CONSTRAINT `log_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `log`
--

LOCK TABLES `log` WRITE;
/*!40000 ALTER TABLE `log` DISABLE KEYS */;
INSERT INTO `log` VALUES (1,1,'Pengguna melakukan login.','2025-12-01 20:47:50'),(2,1,'Pengguna membuat user baru dengan NUPTK: \'9994756\'.','2025-12-01 20:47:58'),(3,1,'Pengguna memperbarui data (status) pengguna NUPTK: \'9994756\'.','2025-12-01 20:48:02'),(4,1,'Pengguna \'AryaSeptiaputra\' menambahkan surat masuk nomor: \'IN-204802\'.','2025-12-01 20:48:04'),(5,1,'Pengguna \'AryaSeptiaputra\' mengupdate data (subject) pada surat masuk nomor: \'IN-204802\'.','2025-12-01 20:48:09'),(6,1,'Pengguna \'AryaSeptiaputra\' menambahkan surat keluar nomor: \'OUT-204808\'.','2025-12-01 20:48:11'),(7,1,'Pengguna \'AryaSeptiaputra\' mengupdate (subject) surat keluar nomor: \'OUT-204808\'.','2025-12-01 20:48:15'),(8,1,'Pengguna \'AryaSeptiaputra\' menghapus surat masuk nomor: \'IN-204802\'.','2025-12-01 20:48:27'),(9,1,'Pengguna \'AryaSeptiaputra\' menghapus surat keluar nomor: \'OUT-204808\'.','2025-12-01 20:48:29'),(10,1,'Pengguna melakukan login.','2025-12-01 20:55:46'),(11,1,'Pengguna membuat user baru dengan NUPTK: \'9995552\'.','2025-12-01 20:55:55'),(12,1,'Pengguna memperbarui data (status) pengguna NUPTK: \'9995552\'.','2025-12-01 20:55:59'),(13,1,'Pengguna \'AryaSeptiaputra\' menambahkan surat masuk nomor: \'IN-205558\'.','2025-12-01 20:56:01'),(14,1,'Pengguna \'AryaSeptiaputra\' mengupdate data (subject) pada surat masuk nomor: \'IN-205558\'.','2025-12-01 20:56:05'),(15,1,'Pengguna \'AryaSeptiaputra\' menambahkan surat keluar nomor: \'OUT-205604\'.','2025-12-01 20:56:07'),(16,1,'Pengguna \'AryaSeptiaputra\' mengupdate (subject) surat keluar nomor: \'OUT-205604\'.','2025-12-01 20:56:11'),(17,1,'Pengguna \'AryaSeptiaputra\' menghapus surat masuk nomor: \'IN-205558\'.','2025-12-01 20:56:23'),(18,1,'Pengguna \'AryaSeptiaputra\' menghapus surat keluar nomor: \'OUT-205604\'.','2025-12-01 20:56:26'),(19,1,'Pengguna melakukan login.','2025-12-01 21:00:28'),(20,1,'Pengguna membuat user baru dengan NUPTK: \'9990033\'.','2025-12-01 21:00:36'),(21,1,'Pengguna memperbarui data (status) pengguna NUPTK: \'9990033\'.','2025-12-01 21:00:40'),(22,1,'Pengguna \'AryaSeptiaputra\' menambahkan surat masuk nomor: \'IN-210040\'.','2025-12-01 21:00:42'),(23,1,'Pengguna \'AryaSeptiaputra\' mengupdate data (subject) pada surat masuk nomor: \'IN-210040\'.','2025-12-01 21:00:46'),(24,1,'Pengguna \'AryaSeptiaputra\' menambahkan surat keluar nomor: \'OUT-210046\'.','2025-12-01 21:00:48'),(25,1,'Pengguna \'AryaSeptiaputra\' mengupdate (subject) surat keluar nomor: \'OUT-210046\'.','2025-12-01 21:00:53'),(26,1,'Pengguna \'AryaSeptiaputra\' menghapus surat masuk nomor: \'IN-210040\'.','2025-12-01 21:01:05'),(27,1,'Pengguna \'AryaSeptiaputra\' menghapus surat keluar nomor: \'OUT-210046\'.','2025-12-01 21:01:07'),(28,1,'Pengguna melakukan login.','2025-12-01 21:01:31'),(29,1,'Pengguna membuat user baru dengan NUPTK: \'9990137\'.','2025-12-01 21:01:39'),(30,1,'Pengguna memperbarui data (status) pengguna NUPTK: \'9990137\'.','2025-12-01 21:01:43'),(31,1,'Pengguna \'AryaSeptiaputra\' menambahkan surat masuk nomor: \'IN-210143\'.','2025-12-01 21:01:45'),(32,1,'Pengguna \'AryaSeptiaputra\' mengupdate data (subject) pada surat masuk nomor: \'IN-210143\'.','2025-12-01 21:01:49'),(33,1,'Pengguna \'AryaSeptiaputra\' menambahkan surat keluar nomor: \'OUT-210149\'.','2025-12-01 21:01:52'),(34,1,'Pengguna \'AryaSeptiaputra\' mengupdate (subject) surat keluar nomor: \'OUT-210149\'.','2025-12-01 21:01:56'),(35,1,'Pengguna \'AryaSeptiaputra\' menambahkan ijazah No: \'DN-210155\' atas nama \'Siswa SMK Test\'.','2025-12-01 21:01:58'),(36,1,'Pengguna \'AryaSeptiaputra\' mengupdate (is_collected, student_name) pada ijazah No: \'DN-210155\'.','2025-12-01 21:02:02');
/*!40000 ALTER TABLE `log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `outgoing_letter`
--

DROP TABLE IF EXISTS `outgoing_letter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `outgoing_letter` (
  `id` int NOT NULL AUTO_INCREMENT,
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
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `ix_outgoing_letter_letter_date` (`letter_date`),
  KEY `ix_outgoing_letter_is_decree` (`is_decree`),
  KEY `ix_outgoing_letter_user_id` (`user_id`),
  KEY `ix_outgoing_letter_destination` (`destination`),
  KEY `ix_outgoing_letter_number` (`number`),
  KEY `ix_outgoing_letter_id` (`id`),
  KEY `ix_outgoing_letter_sent_date` (`sent_date`),
  KEY `ix_outgoing_letter_classification_id` (`classification_id`),
  CONSTRAINT `outgoing_letter_ibfk_1` FOREIGN KEY (`classification_id`) REFERENCES `classification` (`id`),
  CONSTRAINT `outgoing_letter_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `outgoing_letter`
--

LOCK TABLES `outgoing_letter` WRITE;
/*!40000 ALTER TABLE `outgoing_letter` DISABLE KEYS */;
INSERT INTO `outgoing_letter` VALUES (4,'OUT-210149','2025-12-01 00:00:00','2025-12-01 00:00:00','Sekolah Cabang','Pemberitahuan Libur (REVISI)',0,NULL,4,1,'2025-12-01 21:01:51','2025-12-01 21:01:56');
/*!40000 ALTER TABLE `outgoing_letter` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nuptk` varchar(16) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(200) NOT NULL,
  `role` enum('headmaster','admin','teacher') NOT NULL,
  `status` enum('active','inactive') NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_user_nuptk` (`nuptk`),
  UNIQUE KEY `ix_user_username` (`username`),
  KEY `ix_user_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'152022190','AryaSeptiaputra','$argon2id$v=19$m=65536,t=3,p=4$2DsnpPTe+3+vNab03nvvnQ$rZ9T/Z51LpxQITQ3XYsjL+DZSLoN2cA9P6L4Gc1zrRY','admin','active','2025-12-01 20:47:36','2025-12-01 20:47:36'),(5,'9990137','testuser_0137','$argon2id$v=19$m=65536,t=3,p=4$ImSs9f6fE8L4X+v9HwOgFA$PrGjurdZAQlMQwRwILnvyWdXQRDR4LXDj3axWRl1UYg','teacher','inactive','2025-12-01 21:01:39','2025-12-01 21:01:43');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-01 21:02:04
