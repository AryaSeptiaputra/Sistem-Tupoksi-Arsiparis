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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `backup`
--

LOCK TABLES `backup` WRITE;
/*!40000 ALTER TABLE `backup` DISABLE KEYS */;
INSERT INTO `backup` VALUES (1,'backup_arsiparis_smk7_2025-11-30_23-26-43.sql','FAILED','mysqldump execution failed.','2025-11-30 23:26:54',1),(2,'unknown','FAILED','mysqldump execution failed.','2025-11-30 23:26:54',1);
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
  UNIQUE KEY `ix_classification_code` (`code`),
  UNIQUE KEY `ix_classification_name` (`name`),
  KEY `ix_classification_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classification`
--

LOCK TABLES `classification` WRITE;
/*!40000 ALTER TABLE `classification` DISABLE KEYS */;
INSERT INTO `classification` VALUES (3,'Surat Undangan Resmi','UND',NULL,'2025-11-30 23:28:10','2025-11-30 23:28:14');
/*!40000 ALTER TABLE `classification` ENABLE KEYS */;
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
  KEY `ix_incoming_letter_id` (`id`),
  KEY `ix_incoming_letter_sender` (`sender`),
  KEY `ix_incoming_letter_user_id` (`user_id`),
  KEY `ix_incoming_letter_classification_id` (`classification_id`),
  KEY `ix_incoming_letter_letter_date` (`letter_date`),
  CONSTRAINT `incoming_letter_ibfk_1` FOREIGN KEY (`classification_id`) REFERENCES `classification` (`id`),
  CONSTRAINT `incoming_letter_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `incoming_letter`
--

LOCK TABLES `incoming_letter` WRITE;
/*!40000 ALTER TABLE `incoming_letter` DISABLE KEYS */;
INSERT INTO `incoming_letter` VALUES (3,'IN-232820','2025-11-30 00:00:00','2025-11-30 00:00:00','Dinas Pendidikan','Undangan Rapat REVISI',NULL,3,1,'2025-11-30 23:28:22','2025-11-30 23:28:27');
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
  KEY `ix_log_user_id` (`user_id`),
  KEY `ix_log_timestamp` (`timestamp`),
  KEY `ix_log_id` (`id`),
  CONSTRAINT `log_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `log`
--

LOCK TABLES `log` WRITE;
/*!40000 ALTER TABLE `log` DISABLE KEYS */;
INSERT INTO `log` VALUES (1,1,'Pengguna melakukan login.','2025-11-30 23:09:56'),(2,1,'Pengguna \'AryaSeptiaputra\' menambahkan surat masuk nomor: \'IN-231008\'.','2025-11-30 23:10:10'),(3,1,'Pengguna \'AryaSeptiaputra\' mengupdate data (subject) pada surat masuk nomor: \'IN-231008\'.','2025-11-30 23:10:14'),(4,1,'Pengguna \'AryaSeptiaputra\' menambahkan surat keluar nomor: \'OUT-231014\'.','2025-11-30 23:10:16'),(5,1,'Pengguna \'AryaSeptiaputra\' mengupdate (subject) surat keluar nomor: \'OUT-231014\'.','2025-11-30 23:10:20'),(6,1,'Pengguna \'AryaSeptiaputra\' menambahkan raport siswa \'Siswa Test API\' (No: RC-231020).','2025-11-30 23:10:22'),(7,1,'Pengguna \'AryaSeptiaputra\' mengupdate data (student_name) pada raport nomor: \'RC-231020\'.','2025-11-30 23:10:26'),(8,1,'Pengguna \'AryaSeptiaputra\' menghapus surat masuk nomor: \'IN-231008\'.','2025-11-30 23:10:37'),(9,1,'Pengguna \'AryaSeptiaputra\' menghapus surat keluar nomor: \'OUT-231014\'.','2025-11-30 23:10:39'),(10,1,'Pengguna \'AryaSeptiaputra\' menghapus raport nomor: \'RC-231020\'.','2025-11-30 23:10:41'),(11,1,'Pengguna melakukan login.','2025-11-30 23:26:11'),(12,1,'Pengguna \'AryaSeptiaputra\' menambahkan surat masuk nomor: \'IN-232622\'.','2025-11-30 23:26:25'),(13,1,'Pengguna \'AryaSeptiaputra\' mengupdate data (subject) pada surat masuk nomor: \'IN-232622\'.','2025-11-30 23:26:29'),(14,1,'Pengguna \'AryaSeptiaputra\' menambahkan surat keluar nomor: \'OUT-232629\'.','2025-11-30 23:26:31'),(15,1,'Pengguna \'AryaSeptiaputra\' mengupdate (subject) surat keluar nomor: \'OUT-232629\'.','2025-11-30 23:26:35'),(16,1,'Pengguna \'AryaSeptiaputra\' menambahkan raport siswa \'Siswa Test API\' (No: RC-232635).','2025-11-30 23:26:37'),(17,1,'Pengguna \'AryaSeptiaputra\' mengupdate data (student_name) pada raport nomor: \'RC-232635\'.','2025-11-30 23:26:41'),(18,1,'Pengguna \'AryaSeptiaputra\' menghapus surat masuk nomor: \'IN-232622\'.','2025-11-30 23:27:03'),(19,1,'Pengguna \'AryaSeptiaputra\' menghapus surat keluar nomor: \'OUT-232629\'.','2025-11-30 23:27:05'),(20,1,'Pengguna \'AryaSeptiaputra\' menghapus raport nomor: \'RC-232635\'.','2025-11-30 23:27:07'),(21,1,'Pengguna melakukan login.','2025-11-30 23:28:08'),(22,1,'Pengguna \'AryaSeptiaputra\' menambahkan surat masuk nomor: \'IN-232820\'.','2025-11-30 23:28:22'),(23,1,'Pengguna \'AryaSeptiaputra\' mengupdate data (subject) pada surat masuk nomor: \'IN-232820\'.','2025-11-30 23:28:27'),(24,1,'Pengguna \'AryaSeptiaputra\' menambahkan surat keluar nomor: \'OUT-232826\'.','2025-11-30 23:28:29'),(25,1,'Pengguna \'AryaSeptiaputra\' mengupdate (subject) surat keluar nomor: \'OUT-232826\'.','2025-11-30 23:28:33'),(26,1,'Pengguna \'AryaSeptiaputra\' menambahkan raport siswa \'Siswa Test API\' (No: RC-232832).','2025-11-30 23:28:35'),(27,1,'Pengguna \'AryaSeptiaputra\' mengupdate data (student_name) pada raport nomor: \'RC-232832\'.','2025-11-30 23:28:39');
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
  KEY `ix_outgoing_letter_sent_date` (`sent_date`),
  KEY `ix_outgoing_letter_id` (`id`),
  KEY `ix_outgoing_letter_number` (`number`),
  KEY `ix_outgoing_letter_destination` (`destination`),
  KEY `ix_outgoing_letter_user_id` (`user_id`),
  KEY `ix_outgoing_letter_is_decree` (`is_decree`),
  KEY `ix_outgoing_letter_letter_date` (`letter_date`),
  KEY `ix_outgoing_letter_classification_id` (`classification_id`),
  CONSTRAINT `outgoing_letter_ibfk_1` FOREIGN KEY (`classification_id`) REFERENCES `classification` (`id`),
  CONSTRAINT `outgoing_letter_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `outgoing_letter`
--

LOCK TABLES `outgoing_letter` WRITE;
/*!40000 ALTER TABLE `outgoing_letter` DISABLE KEYS */;
INSERT INTO `outgoing_letter` VALUES (3,'OUT-232826','2025-11-30 00:00:00','2025-11-30 00:00:00','Sekolah Cabang','Pemberitahuan Libur (REVISI)',0,NULL,3,1,'2025-11-30 23:28:29','2025-11-30 23:28:33');
/*!40000 ALTER TABLE `outgoing_letter` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `report_card`
--

DROP TABLE IF EXISTS `report_card`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `report_card` (
  `id` int NOT NULL AUTO_INCREMENT,
  `number` varchar(50) NOT NULL,
  `student_name` varchar(100) NOT NULL,
  `class_name` varchar(50) NOT NULL,
  `academic_year` varchar(9) NOT NULL,
  `attachment_path` varchar(255) DEFAULT NULL,
  `user_id` int NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_report_card_number` (`number`),
  KEY `user_id` (`user_id`),
  KEY `ix_report_card_class_name` (`class_name`),
  KEY `ix_report_card_id` (`id`),
  KEY `ix_report_card_academic_year` (`academic_year`),
  KEY `ix_report_card_student_name` (`student_name`),
  CONSTRAINT `report_card_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `report_card`
--

LOCK TABLES `report_card` WRITE;
/*!40000 ALTER TABLE `report_card` DISABLE KEYS */;
INSERT INTO `report_card` VALUES (3,'RC-232832','Siswa Test API (Updated)','XII-RPL','2024/2025',NULL,1,'2025-11-30 23:28:35','2025-11-30 23:28:39');
/*!40000 ALTER TABLE `report_card` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'152022190','AryaSeptiaputra','$argon2id$v=19$m=65536,t=3,p=4$xHhvrZXSmhOiVAphzBkDAA$Y+wI7TBB01Y33RbWiAbxO6SY9m9jfJ+NP2o3rkfnZdQ','admin','active','2025-11-30 23:09:46','2025-11-30 23:09:46'),(4,'9992814','testuser_2814','$argon2id$v=19$m=65536,t=3,p=4$BACgVIoxRggB4JzTGuNcCw$h8/rWLjm0HuQcws/O6CIXYCyKSL5drqvaNaIHbzYUls','teacher','inactive','2025-11-30 23:28:16','2025-11-30 23:28:20');
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

-- Dump completed on 2025-11-30 23:28:41
