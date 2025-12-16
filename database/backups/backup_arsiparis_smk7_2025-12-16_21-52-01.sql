-- MySQL dump 10.13  Distrib 8.4.3, for Win64 (x86_64)
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
  KEY `ix_backup_id` (`id`),
  KEY `ix_backup_user_id` (`user_id`),
  CONSTRAINT `backup_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `backup`
--

LOCK TABLES `backup` WRITE;
/*!40000 ALTER TABLE `backup` DISABLE KEYS */;
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
  `code` varchar(10) NOT NULL,
  `description` text,
  `retention_active_period` int NOT NULL,
  `retention_inactive_period` int NOT NULL,
  `final_action` varchar(50) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_classification_code` (`code`),
  UNIQUE KEY `ix_classification_name` (`name`),
  KEY `ix_classification_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classification`
--

LOCK TABLES `classification` WRITE;
/*!40000 ALTER TABLE `classification` DISABLE KEYS */;
INSERT INTO `classification` VALUES (1,'Klasifikasi 1','CL-01','Klasifikasi dummy',1,2,'destroyed','2025-12-13 02:54:52','2025-12-16 12:32:04'),(2,'Klasifikasi 2','CL-02','Klasifikasi dummy',1,2,'destroyed','2025-12-13 02:54:52','2025-12-16 12:32:10'),(3,'Klasifikasi 3','CL-03','Klasifikasi dummy',1,2,'destroy','2025-12-13 02:54:52','2025-12-13 02:54:52'),(4,'Klasifikasi 4','CL-04','Klasifikasi dummy',1,2,'destroy','2025-12-13 02:54:52','2025-12-13 02:54:52'),(5,'Klasifikasi 5','CL-05','Klasifikasi dummy',1,2,'destroy','2025-12-13 02:54:52','2025-12-13 02:54:52'),(6,'Klasifikasi 6','CL-06','Klasifikasi dummy',1,2,'destroy','2025-12-13 02:54:52','2025-12-13 02:54:52'),(7,'Klasifikasi 7','CL-07','Klasifikasi dummy',1,2,'destroy','2025-12-13 02:54:52','2025-12-13 02:54:52'),(8,'Klasifikasi 8','CL-08','Klasifikasi dummy',1,2,'destroy','2025-12-13 02:54:52','2025-12-13 02:54:52'),(9,'Klasifikasi 9','CL-09','Klasifikasi dummy',1,2,'destroy','2025-12-13 02:54:52','2025-12-13 02:54:52'),(10,'Klasifikasi 10','CL-10','Klasifikasi dummy',1,2,'destroy','2025-12-13 02:54:52','2025-12-13 02:54:52');
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
  `storage_location_id` int DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_diploma_number` (`number`),
  KEY `storage_location_id` (`storage_location_id`),
  KEY `ix_diploma_student_name` (`student_name`),
  KEY `ix_diploma_major` (`major`),
  KEY `ix_diploma_id` (`id`),
  KEY `ix_diploma_academic_year` (`academic_year`),
  CONSTRAINT `diploma_ibfk_1` FOREIGN KEY (`storage_location_id`) REFERENCES `storage_location` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `diploma`
--

LOCK TABLES `diploma` WRITE;
/*!40000 ALTER TABLE `diploma` DISABLE KEYS */;
INSERT INTO `diploma` VALUES (1,'IJZ-0001','Siswa 1','Rekayasa Perangkat Lunak','2023/2024',0,NULL,NULL,8,'2025-12-13 02:54:53','2025-12-14 16:59:16'),(2,'IJZ-0002','Siswa 2','IPS','2023/2024',0,NULL,NULL,3,'2025-12-13 02:54:53','2025-12-13 02:54:53'),(3,'IJZ-0003','Siswa 3','IPA','2023/2024',0,NULL,NULL,5,'2025-12-13 02:54:53','2025-12-13 02:54:53'),(4,'IJZ-0004','Siswa 4','IPS','2023/2024',0,NULL,NULL,3,'2025-12-13 02:54:53','2025-12-13 02:54:53'),(5,'IJZ-0005','Siswa 5','IPA','2023/2024',0,NULL,NULL,8,'2025-12-13 02:54:53','2025-12-13 02:54:53'),(6,'IJZ-0006','Siswa 6','IPS','2023/2024',0,NULL,NULL,2,'2025-12-13 02:54:53','2025-12-13 02:54:53'),(7,'IJZ-0007','Siswa 7','IPA','2023/2024',0,NULL,NULL,9,'2025-12-13 02:54:53','2025-12-13 02:54:53'),(8,'IJZ-0008','Siswa 8','IPS','2023/2024',0,NULL,NULL,1,'2025-12-13 02:54:53','2025-12-13 02:54:53'),(9,'IJZ-0009','Siswa 9','IPA','2023/2024',0,NULL,NULL,8,'2025-12-13 02:54:53','2025-12-13 02:54:53'),(10,'IJZ-0010','Siswa 10','IPS','2023/2024',0,NULL,NULL,6,'2025-12-13 02:54:53','2025-12-13 02:54:53');
/*!40000 ALTER TABLE `diploma` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `employee_archive`
--

DROP TABLE IF EXISTS `employee_archive`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employee_archive` (
  `id` int NOT NULL AUTO_INCREMENT,
  `document_name` varchar(255) NOT NULL,
  `document_type` varchar(50) NOT NULL,
  `document_year` int DEFAULT NULL,
  `description` text,
  `attachment_path` varchar(255) DEFAULT NULL,
  `owner_id` int NOT NULL,
  `storage_location_id` int DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `storage_location_id` (`storage_location_id`),
  KEY `ix_employee_archive_owner_id` (`owner_id`),
  KEY `ix_employee_archive_id` (`id`),
  CONSTRAINT `employee_archive_ibfk_1` FOREIGN KEY (`owner_id`) REFERENCES `teacher` (`id`) ON DELETE CASCADE,
  CONSTRAINT `employee_archive_ibfk_2` FOREIGN KEY (`storage_location_id`) REFERENCES `storage_location` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employee_archive`
--

LOCK TABLES `employee_archive` WRITE;
/*!40000 ALTER TABLE `employee_archive` DISABLE KEYS */;
INSERT INTO `employee_archive` VALUES (1,'Dokumen Pegawai 1','ijazah',2011,'Arsip pegawai dummy',NULL,7,8,'2025-12-13 02:54:53','2025-12-13 02:54:53'),(2,'Dokumen Pegawai 2','ijazah',2012,'Arsip pegawai dummy',NULL,10,5,'2025-12-13 02:54:53','2025-12-13 02:54:53'),(3,'Dokumen Pegawai 3','ijazah',2013,'Arsip pegawai dummy',NULL,6,8,'2025-12-13 02:54:53','2025-12-13 02:54:53'),(4,'Dokumen Pegawai 4','ijazah',2014,'Arsip pegawai dummy',NULL,11,2,'2025-12-13 02:54:53','2025-12-13 02:54:53'),(5,'Dokumen Pegawai 5','ijazah',2015,'Arsip pegawai dummy',NULL,10,5,'2025-12-13 02:54:53','2025-12-13 02:54:53'),(6,'Dokumen Pegawai 6','ijazah',2016,'Arsip pegawai dummy',NULL,2,9,'2025-12-13 02:54:53','2025-12-13 02:54:53'),(7,'Dokumen Pegawai 7','ijazah',2017,'Arsip pegawai dummy',NULL,2,1,'2025-12-13 02:54:53','2025-12-13 02:54:53'),(8,'Dokumen Pegawai 8','ijazah',2018,'Arsip pegawai dummy',NULL,9,5,'2025-12-13 02:54:53','2025-12-13 02:54:53'),(9,'Dokumen Pegawai 9','ijazah',2019,'Arsip pegawai dummy',NULL,7,4,'2025-12-13 02:54:53','2025-12-13 02:54:53'),(10,'Dokumen Pegawai 10','ijazah',2020,'Arsip pegawai dummy',NULL,8,8,'2025-12-13 02:54:53','2025-12-13 02:54:53');
/*!40000 ALTER TABLE `employee_archive` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `finance_archive`
--

DROP TABLE IF EXISTS `finance_archive`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `finance_archive` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `fiscal_year` int NOT NULL,
  `period_month` int DEFAULT NULL,
  `category` varchar(50) NOT NULL,
  `amount` bigint DEFAULT NULL,
  `description` text,
  `attachment_path` varchar(255) DEFAULT NULL,
  `classification_id` int NOT NULL,
  `storage_location_id` int DEFAULT NULL,
  `archive_status` varchar(20) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `classification_id` (`classification_id`),
  KEY `storage_location_id` (`storage_location_id`),
  KEY `ix_finance_archive_fiscal_year` (`fiscal_year`),
  KEY `ix_finance_archive_id` (`id`),
  CONSTRAINT `finance_archive_ibfk_1` FOREIGN KEY (`classification_id`) REFERENCES `classification` (`id`),
  CONSTRAINT `finance_archive_ibfk_2` FOREIGN KEY (`storage_location_id`) REFERENCES `storage_location` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `finance_archive`
--

LOCK TABLES `finance_archive` WRITE;
/*!40000 ALTER TABLE `finance_archive` DISABLE KEYS */;
INSERT INTO `finance_archive` VALUES (1,'Laporan Keuangan 1',2021,2,'bos_reguler',1000000,'Laporan dummy',NULL,7,1,'inactive','2025-12-13 02:54:53','2025-12-14 00:01:00'),(2,'Laporan Keuangan 2',2022,3,'bos_reguler',2000000,'Laporan dummy',NULL,7,5,'inactive','2025-12-13 02:54:53','2025-12-14 00:01:00'),(3,'Laporan Keuangan 3',2023,4,'bos_reguler',3000000,'Laporan dummy',NULL,4,10,'inactive','2025-12-13 02:54:53','2025-12-14 00:01:00'),(4,'Laporan Keuangan 4',2024,5,'bos_reguler',4000000,'Laporan dummy',NULL,3,3,'active','2025-12-13 02:54:53','2025-12-13 02:54:53'),(5,'Laporan Keuangan 5',2020,6,'bos_reguler',5000000,'Laporan dummy',NULL,5,1,'inactive','2025-12-13 02:54:53','2025-12-14 00:01:00'),(6,'Laporan Keuangan 6',2021,7,'bos_reguler',6000000,'Laporan dummy',NULL,4,8,'inactive','2025-12-13 02:54:53','2025-12-14 00:01:00'),(7,'Laporan Keuangan 7',2022,8,'bos_reguler',7000000,'Laporan dummy',NULL,4,10,'inactive','2025-12-13 02:54:53','2025-12-14 00:01:00'),(8,'Laporan Keuangan 8',2023,9,'bos_reguler',8000000,'Laporan dummy',NULL,10,2,'inactive','2025-12-13 02:54:53','2025-12-14 00:01:00'),(9,'Laporan Keuangan 9',2024,10,'bos_reguler',9000000,'Laporan dummy',NULL,2,4,'active','2025-12-13 02:54:53','2025-12-13 02:54:53'),(10,'Laporan Keuangan 10',2020,11,'bos_reguler',10000000,'Laporan dummy',NULL,5,2,'inactive','2025-12-13 02:54:53','2025-12-14 00:01:00');
/*!40000 ALTER TABLE `finance_archive` ENABLE KEYS */;
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
  `storage_location_id` int DEFAULT NULL,
  `archive_status` varchar(20) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_incoming_letter_number` (`number`),
  KEY `ix_incoming_letter_letter_date` (`letter_date`),
  KEY `ix_incoming_letter_id` (`id`),
  KEY `ix_incoming_letter_received_date` (`received_date`),
  KEY `ix_incoming_letter_sender` (`sender`),
  KEY `ix_incoming_letter_storage_location_id` (`storage_location_id`),
  KEY `ix_incoming_letter_classification_id` (`classification_id`),
  CONSTRAINT `incoming_letter_ibfk_1` FOREIGN KEY (`classification_id`) REFERENCES `classification` (`id`),
  CONSTRAINT `incoming_letter_ibfk_2` FOREIGN KEY (`storage_location_id`) REFERENCES `storage_location` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `incoming_letter`
--

LOCK TABLES `incoming_letter` WRITE;
/*!40000 ALTER TABLE `incoming_letter` DISABLE KEYS */;
INSERT INTO `incoming_letter` VALUES (1,'SM-001/2024','2025-12-13 00:00:00','2025-12-13 00:00:00','Instansi 1','Surat Masuk 1',NULL,2,3,'active','2025-12-13 02:54:53','2025-12-13 19:03:33'),(2,'SM-002/2024','2025-12-13 00:00:00','2025-12-13 00:00:00','Instansi 2','Surat Masuk 2 .',NULL,8,6,'active','2025-12-13 02:54:53','2025-12-14 12:19:06'),(3,'SM-003/2024','2025-12-13 00:00:00','2025-12-13 00:00:00','Instansi 3','Surat Masuk 3',NULL,9,10,'active','2025-12-13 02:54:53','2025-12-14 15:24:42'),(4,'SM-004/2024','2025-12-13 00:00:00','2025-12-13 00:00:00','Instansi 4','Surat Masuk 4',NULL,7,3,'inactive','2025-12-13 02:54:53','2025-12-14 16:12:48'),(5,'SM-005/2024','2025-12-13 00:00:00','2025-12-13 00:00:00','Instansi 5','Surat Masuk 5',NULL,2,9,'destroyed','2025-12-13 02:54:53','2025-12-14 16:12:58'),(6,'SM-006/2024','2025-12-13 02:54:53','2025-12-13 02:54:53','Instansi 6','Surat Masuk 6',NULL,3,6,'active','2025-12-13 02:54:53','2025-12-13 02:54:53'),(7,'SM-007/2024','2025-12-13 02:54:53','2025-12-13 02:54:53','Instansi 7','Surat Masuk 7',NULL,5,10,'active','2025-12-13 02:54:53','2025-12-13 02:54:53'),(8,'SM-008/2024','2025-12-13 02:54:53','2025-12-13 02:54:53','Instansi 8','Surat Masuk 8',NULL,7,5,'active','2025-12-13 02:54:53','2025-12-13 02:54:53'),(9,'SM-009/2024','2025-12-13 02:54:53','2025-12-13 02:54:53','Instansi 9','Surat Masuk 9',NULL,8,1,'active','2025-12-13 02:54:53','2025-12-13 02:54:53'),(10,'SM-010/2024','2025-12-13 02:54:53','2025-12-13 02:54:53','Instansi 10','Surat Masuk 10',NULL,4,5,'active','2025-12-13 02:54:53','2025-12-13 02:54:53');
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
  `action` text NOT NULL,
  `timestamp` datetime NOT NULL DEFAULT (now()),
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_log_id` (`id`),
  KEY `ix_log_user_id` (`user_id`),
  KEY `ix_log_timestamp` (`timestamp`),
  CONSTRAINT `log_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `log`
--

LOCK TABLES `log` WRITE;
/*!40000 ALTER TABLE `log` DISABLE KEYS */;
INSERT INTO `log` VALUES (1,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-13 02:41:45',1),(2,'Melakukan aksi dummy 1','2025-12-13 02:54:53',1),(3,'Melakukan aksi dummy 2','2025-12-13 02:54:53',1),(4,'Melakukan aksi dummy 3','2025-12-13 02:54:53',1),(5,'Melakukan aksi dummy 4','2025-12-13 02:54:53',1),(6,'Melakukan aksi dummy 5','2025-12-13 02:54:53',1),(7,'Melakukan aksi dummy 6','2025-12-13 02:54:53',1),(8,'Melakukan aksi dummy 7','2025-12-13 02:54:53',1),(9,'Melakukan aksi dummy 8','2025-12-13 02:54:53',1),(10,'Melakukan aksi dummy 9','2025-12-13 02:54:53',1),(11,'Melakukan aksi dummy 10','2025-12-13 02:54:53',1),(12,'Memperbarui akun pengguna: \'Guru Contoh 2\'.','2025-12-13 02:55:10',1),(13,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-13 05:58:13',1),(14,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-13 06:29:17',1),(15,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-13 11:34:45',1),(16,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-13 11:53:21',1),(17,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-13 12:12:18',1),(18,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-13 12:38:37',1),(19,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-13 16:34:26',1),(20,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-13 17:38:12',1),(21,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-13 18:23:22',1),(22,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-13 18:47:49',1),(23,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-13 19:03:23',1),(24,'Update surat masuk No: \'SM-001/2024\'','2025-12-13 19:03:33',1),(25,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-13 21:42:46',1),(26,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-13 22:23:34',1),(27,'Update Ijazah: Siswa 1','2025-12-13 22:37:43',1),(28,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-13 22:40:22',1),(29,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-13 23:00:54',1),(30,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-13 23:16:41',1),(31,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-13 23:36:07',1),(32,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-14 06:34:43',1),(33,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-14 11:01:27',1),(34,'Update Ijazah: Siswa 1','2025-12-14 11:01:39',1),(35,'Update Ijazah: Siswa 1','2025-12-14 11:01:49',1),(36,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-14 12:14:08',1),(37,'Update surat masuk No: \'SM-002/2024\'','2025-12-14 12:19:06',1),(38,'Update surat keluar No: \'SK-001/2024\'','2025-12-14 12:28:20',1),(39,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-14 13:11:19',1),(40,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-14 13:28:12',1),(41,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-14 13:56:44',1),(42,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-14 14:15:11',1),(43,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-14 15:24:11',1),(44,'Update surat masuk No: \'SM-003/2024\'','2025-12-14 15:24:42',1),(45,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-14 15:43:48',1),(46,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-14 15:53:16',1),(47,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-14 16:04:33',1),(48,'Update surat masuk No: \'SM-004/2024\'','2025-12-14 16:12:49',1),(49,'Update surat masuk No: \'SM-005/2024\'','2025-12-14 16:12:58',1),(50,'Update Ijazah: Siswa 1','2025-12-14 16:16:48',1),(51,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-14 16:24:31',1),(52,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-14 16:59:02',1),(53,'Update Ijazah: Siswa 1','2025-12-14 16:59:16',1),(54,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-14 17:13:55',1),(55,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-14 17:39:57',1),(56,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-14 18:12:21',1),(57,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-14 18:12:22',1),(58,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-14 18:41:10',1),(59,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-14 19:01:45',1),(60,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-14 19:31:03',1),(61,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-14 21:02:29',1),(62,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-15 06:24:07',1),(63,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-15 06:42:54',1),(64,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-15 07:00:26',1),(65,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-16 12:28:18',1),(66,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-16 13:46:08',1),(67,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-16 21:22:23',1),(68,'Pengguna \'Arya Septiaputra\' melakukan login.','2025-12-16 21:51:43',1);
/*!40000 ALTER TABLE `log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `master_reference`
--

DROP TABLE IF EXISTS `master_reference`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `master_reference` (
  `id` int NOT NULL AUTO_INCREMENT,
  `category` enum('school_major','teacher_emp_status','teacher_active_status','teacher_rank','finance_category','emp_doc_type','letter_approval_status','archive_status','final_action') NOT NULL,
  `code` varchar(50) NOT NULL,
  `name` varchar(150) NOT NULL,
  `sort_order` int DEFAULT NULL,
  `description` text,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `ix_master_reference_id` (`id`),
  KEY `ix_master_reference_category` (`category`),
  KEY `ix_master_reference_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `master_reference`
--

LOCK TABLES `master_reference` WRITE;
/*!40000 ALTER TABLE `master_reference` DISABLE KEYS */;
/*!40000 ALTER TABLE `master_reference` ENABLE KEYS */;
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
  `archive_status` varchar(20) NOT NULL,
  `approval_status` varchar(20) NOT NULL,
  `classification_id` int NOT NULL,
  `storage_location_id` int DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `storage_location_id` (`storage_location_id`),
  KEY `ix_outgoing_letter_sent_date` (`sent_date`),
  KEY `ix_outgoing_letter_classification_id` (`classification_id`),
  KEY `ix_outgoing_letter_id` (`id`),
  KEY `ix_outgoing_letter_number` (`number`),
  KEY `ix_outgoing_letter_destination` (`destination`),
  KEY `ix_outgoing_letter_is_decree` (`is_decree`),
  KEY `ix_outgoing_letter_letter_date` (`letter_date`),
  CONSTRAINT `outgoing_letter_ibfk_1` FOREIGN KEY (`classification_id`) REFERENCES `classification` (`id`),
  CONSTRAINT `outgoing_letter_ibfk_2` FOREIGN KEY (`storage_location_id`) REFERENCES `storage_location` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `outgoing_letter`
--

LOCK TABLES `outgoing_letter` WRITE;
/*!40000 ALTER TABLE `outgoing_letter` DISABLE KEYS */;
INSERT INTO `outgoing_letter` VALUES (1,'SK-001/2024','2025-12-13 00:00:00','2025-12-13 00:00:00','Lembaga 1','Surat Keluar 1',0,NULL,'active','approved',1,1,'2025-12-13 02:54:53','2025-12-14 12:28:20'),(2,'SK-002/2024','2025-12-13 02:54:53','2025-12-13 02:54:53','Lembaga 2','Surat Keluar 2',0,NULL,'active','pending',10,1,'2025-12-13 02:54:53','2025-12-13 02:54:53'),(3,'SK-003/2024','2025-12-13 02:54:53','2025-12-13 02:54:53','Lembaga 3','Surat Keluar 3',0,NULL,'active','approved',3,6,'2025-12-13 02:54:53','2025-12-13 02:54:53'),(4,'SK-004/2024','2025-12-13 02:54:53','2025-12-13 02:54:53','Lembaga 4','Surat Keluar 4',0,NULL,'active','pending',10,3,'2025-12-13 02:54:53','2025-12-13 02:54:53'),(5,'SK-005/2024','2025-12-13 02:54:53','2025-12-13 02:54:53','Lembaga 5','Surat Keluar 5',0,NULL,'active','approved',10,8,'2025-12-13 02:54:53','2025-12-13 02:54:53'),(6,'SK-006/2024','2025-12-13 02:54:53','2025-12-13 02:54:53','Lembaga 6','Surat Keluar 6',0,NULL,'active','pending',4,3,'2025-12-13 02:54:53','2025-12-13 02:54:53'),(7,'SK-007/2024','2025-12-13 02:54:53','2025-12-13 02:54:53','Lembaga 7','Surat Keluar 7',0,NULL,'active','approved',9,8,'2025-12-13 02:54:53','2025-12-13 02:54:53'),(8,'SK-008/2024','2025-12-13 02:54:53','2025-12-13 02:54:53','Lembaga 8','Surat Keluar 8',0,NULL,'active','pending',7,4,'2025-12-13 02:54:53','2025-12-13 02:54:53'),(9,'SK-009/2024','2025-12-13 02:54:53','2025-12-13 02:54:53','Lembaga 9','Surat Keluar 9',0,NULL,'active','approved',4,1,'2025-12-13 02:54:53','2025-12-13 02:54:53'),(10,'SK-010/2024','2025-12-13 02:54:53','2025-12-13 02:54:53','Lembaga 10','Surat Keluar 10',0,NULL,'active','pending',7,5,'2025-12-13 02:54:53','2025-12-13 02:54:53');
/*!40000 ALTER TABLE `outgoing_letter` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `storage_location`
--

DROP TABLE IF EXISTS `storage_location`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `storage_location` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` text,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_storage_location_name` (`name`),
  KEY `ix_storage_location_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `storage_location`
--

LOCK TABLES `storage_location` WRITE;
/*!40000 ALTER TABLE `storage_location` DISABLE KEYS */;
INSERT INTO `storage_location` VALUES (1,'Lemari-1','Lemari penyimpanan nomor 1','2025-12-13 02:54:52','2025-12-13 02:54:52'),(2,'Lemari-2','Lemari penyimpanan nomor 2','2025-12-13 02:54:52','2025-12-13 02:54:52'),(3,'Lemari-3','Lemari penyimpanan nomor 3','2025-12-13 02:54:52','2025-12-13 02:54:52'),(4,'Lemari-4','Lemari penyimpanan nomor 4','2025-12-13 02:54:52','2025-12-13 02:54:52'),(5,'Lemari-5','Lemari penyimpanan nomor 5','2025-12-13 02:54:52','2025-12-13 02:54:52'),(6,'Lemari-6','Lemari penyimpanan nomor 6','2025-12-13 02:54:52','2025-12-13 02:54:52'),(7,'Lemari-7','Lemari penyimpanan nomor 7','2025-12-13 02:54:52','2025-12-13 02:54:52'),(8,'Lemari-8','Lemari penyimpanan nomor 8','2025-12-13 02:54:52','2025-12-13 02:54:52'),(9,'Lemari-9','Lemari penyimpanan nomor 9','2025-12-13 02:54:52','2025-12-13 02:54:52'),(10,'Lemari-10','Lemari penyimpanan nomor 10','2025-12-13 02:54:52','2025-12-13 02:54:52');
/*!40000 ALTER TABLE `storage_location` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teacher`
--

DROP TABLE IF EXISTS `teacher`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teacher` (
  `id` int NOT NULL AUTO_INCREMENT,
  `identity_number` varchar(50) NOT NULL,
  `full_name` varchar(150) NOT NULL,
  `gender` varchar(20) NOT NULL,
  `employment_status` varchar(50) NOT NULL,
  `rank` varchar(20) DEFAULT NULL,
  `status` varchar(50) NOT NULL,
  `address` text,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_teacher_identity_number` (`identity_number`),
  KEY `ix_teacher_id` (`id`),
  KEY `ix_teacher_full_name` (`full_name`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teacher`
--

LOCK TABLES `teacher` WRITE;
/*!40000 ALTER TABLE `teacher` DISABLE KEYS */;
INSERT INTO `teacher` VALUES (1,'112022190','Arya Septiaputra','L','PNS',NULL,'Aktif','Bandung','2025-12-13 02:16:59','2025-12-13 02:16:59'),(2,'198801001','Guru Contoh 1','L','PNS','III/a','Aktif','Alamat Guru 1','2025-12-13 02:54:52','2025-12-13 02:54:52'),(3,'198802001','Guru Contoh 2','P','Honorer','III/a','Aktif','Alamat Guru 2','2025-12-13 02:54:52','2025-12-13 02:54:52'),(4,'198803001','Guru Contoh 3','L','PNS','III/a','Aktif','Alamat Guru 3','2025-12-13 02:54:52','2025-12-13 02:54:52'),(5,'198804001','Guru Contoh 4','P','Honorer','III/a','Aktif','Alamat Guru 4','2025-12-13 02:54:52','2025-12-13 02:54:52'),(6,'198805001','Guru Contoh 5','L','PNS','III/a','Aktif','Alamat Guru 5','2025-12-13 02:54:52','2025-12-13 02:54:52'),(7,'198806001','Guru Contoh 6','P','Honorer','III/a','Aktif','Alamat Guru 6','2025-12-13 02:54:52','2025-12-13 02:54:52'),(8,'198807001','Guru Contoh 7','L','PNS','III/a','Aktif','Alamat Guru 7','2025-12-13 02:54:52','2025-12-13 02:54:52'),(9,'198808001','Guru Contoh 8','P','Honorer','III/a','Aktif','Alamat Guru 8','2025-12-13 02:54:52','2025-12-13 02:54:52'),(10,'198809001','Guru Contoh 9','L','PNS','III/a','Aktif','Alamat Guru 9','2025-12-13 02:54:52','2025-12-13 02:54:52'),(11,'1988010001','Guru Contoh 10','P','Honorer','III/a','Aktif','Alamat Guru 10','2025-12-13 02:54:52','2025-12-13 02:54:52');
/*!40000 ALTER TABLE `teacher` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `teacher_id` int NOT NULL,
  `password` varchar(200) NOT NULL,
  `role` enum('headmaster','admin','teacher') NOT NULL,
  `status` enum('active','inactive') NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `teacher_id` (`teacher_id`),
  KEY `ix_user_id` (`id`),
  CONSTRAINT `user_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teacher` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,1,'$argon2id$v=19$m=65536,t=3,p=4$G0NICaF0bm1NidGaU6q1Ng$lEBS8UV+RdTFzga+yUeeJuZHwpapW+kIWK5gluCKgtg','admin','active','2025-12-13 02:16:59','2025-12-13 02:16:59'),(2,2,'$argon2id$v=19$m=65536,t=3,p=4$VoqRkjJmDOFcK2VMiXGuNQ$65L3Ah8EkL/bM82o/17e16eWU3/YdNXygeeo95JfINQ','admin','active','2025-12-13 02:54:53','2025-12-13 02:54:53'),(3,3,'$argon2id$v=19$m=65536,t=3,p=4$PQdgTMmZc07pnTPmXGttzQ$1u8udYiBKE2ivi3MS7/WBAgOATdEXwIC7wiHR5ld4KY','headmaster','active','2025-12-13 02:54:53','2025-12-13 02:55:10'),(4,4,'$argon2id$v=19$m=65536,t=3,p=4$q9Vai9Hae+/9f08JQQhhjA$ncCLqEmKE/UTaurOLE/4xHYsw8MHri7lq36tNSsSqMs','teacher','active','2025-12-13 02:54:53','2025-12-13 02:54:53'),(5,5,'$argon2id$v=19$m=65536,t=3,p=4$GYNw7h0jhDAGIEQIwdh7Lw$p1pRA5dhoc/0gQoYcE6+GJqHzTOxTIvNLo/K0b/APkw','teacher','active','2025-12-13 02:54:53','2025-12-13 02:54:53'),(6,6,'$argon2id$v=19$m=65536,t=3,p=4$XmstRYhxrjXm3BuDMGbM+Q$Q4fIjQKHpUHGbcqwsn1tDGzfFLBp1acpfb03MCtlEtc','teacher','active','2025-12-13 02:54:53','2025-12-13 02:54:53'),(7,7,'$argon2id$v=19$m=65536,t=3,p=4$N0ZoTcmZM4awttbae6+V8g$JNsrb60d3/bSE1S+IPo5rUebjZZhaN8I0Vi8OxCL6ws','teacher','active','2025-12-13 02:54:53','2025-12-13 02:54:53'),(8,8,'$argon2id$v=19$m=65536,t=3,p=4$nBOi1JrzXguBMKbUGuN8Lw$mF0YiWpEEg0ZuGAnQmoyzl96OCR8WQxX544qMBV7cfw','teacher','active','2025-12-13 02:54:53','2025-12-13 02:54:53'),(9,9,'$argon2id$v=19$m=65536,t=3,p=4$odT6n/O+F4LQOuc8Z4zRWg$Ssm6HmvIYS605SvVBRqXY2+RdHCIHtkwcSl5Z78bHUc','teacher','active','2025-12-13 02:54:53','2025-12-13 02:54:53'),(10,10,'$argon2id$v=19$m=65536,t=3,p=4$4zzHGGOM0fp/j3FuDSFESA$uSkk1ukMnl78vjtVyzXwv4L/AvX/mWK+KQmGxr6W4FU','teacher','active','2025-12-13 02:54:53','2025-12-13 02:54:53'),(11,11,'$argon2id$v=19$m=65536,t=3,p=4$QYgxZmzN+R9DyLm3dm7tXQ$bYcLi5STiLeloCI7uhXrFCnvyh49p+iDGeEX7QCpPMw','teacher','active','2025-12-13 02:54:53','2025-12-13 02:54:53');
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

-- Dump completed on 2025-12-16 21:52:01
