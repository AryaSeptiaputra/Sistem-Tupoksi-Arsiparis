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
INSERT INTO `backup` VALUES (1,'backup_arsiparis_smk7_2025-12-03_16-10-09.sql','SUCCESS','Database backup created successfully.','2025-12-03 16:10:09',1),(2,'backup_arsiparis_smk7_2025-12-03_16-27-54.sql','SUCCESS','Database backup created successfully.','2025-12-03 16:27:54',1),(3,'backup_arsiparis_smk7_2025-12-03_20-29-56.sql','SUCCESS','Database backup created successfully.','2025-12-03 20:29:56',1);
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
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_classification_code` (`code`),
  UNIQUE KEY `ix_classification_name` (`name`),
  KEY `ix_classification_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classification`
--

LOCK TABLES `classification` WRITE;
/*!40000 ALTER TABLE `classification` DISABLE KEYS */;
INSERT INTO `classification` VALUES (3,'Lambang, Logo & Identitas Sekolah','001.2',NULL,'2025-12-03 19:04:29','2025-12-05 07:16:46'),(4,'Pelayanan Umum & Informasi','002',NULL,'2025-12-03 19:04:29','2025-12-03 19:04:29'),(5,'Keprotokolan & Upacara','003',NULL,'2025-12-03 19:04:29','2025-12-03 19:04:29'),(6,'Pemerintahan','100','Kebijakan dan hubungan dengan pemerintah','2025-12-03 19:04:29','2025-12-03 19:04:29'),(7,'Peraturan & Kebijakan Pemerintah','111',NULL,'2025-12-03 19:04:29','2025-12-03 19:04:29'),(8,'Surat Edaran & Instruksi','112',NULL,'2025-12-03 19:04:29','2025-12-03 19:04:29'),(9,'Pelaporan ke Dinas Pendidikan','113',NULL,'2025-12-03 19:04:29','2025-12-03 19:04:29'),(10,'Politik','200','Hubungan politik dalam konteks kelembagaan pendidikan','2025-12-03 19:04:29','2025-12-03 19:04:29'),(11,'Keamanan & Ketertiban','300','Penanganan keamanan dan ketertiban sekolah','2025-12-03 19:04:29','2025-12-03 19:04:29'),(12,'Tata Tertib Sekolah','311',NULL,'2025-12-03 19:04:29','2025-12-03 19:04:29'),(13,'Penanganan Kasus & Serahan Polisi','312',NULL,'2025-12-03 19:04:29','2025-12-03 19:04:29'),(14,'Kesejahteraan Rakyat','400','Fokus bidang kesehatan, pendidikan dan sosial','2025-12-03 19:04:29','2025-12-03 19:04:29'),(15,'Pendidikan','421','Administrasi akademik dan pembelajaran','2025-12-03 19:04:29','2025-12-03 19:04:29'),(16,'Kurikulum','421.1','Dokumen kurikulum, struktur program','2025-12-03 19:04:29','2025-12-03 19:04:29'),(17,'Administrasi Akademik','421.2','Absensi, jadwal, kalender akademik','2025-12-03 19:04:29','2025-12-03 19:04:29'),(18,'Penilaian & Rapor','421.3','Kisi-kisi, leger nilai, rapor','2025-12-03 19:04:29','2025-12-03 19:04:29'),(19,'PPDB','421.4','Penerimaan Peserta Didik Baru','2025-12-03 19:04:29','2025-12-03 19:04:29'),(20,'Ujian & Sertifikasi Kompetensi','421.5','USBK, UKK, sertifikat','2025-12-03 19:04:29','2025-12-03 19:04:29'),(21,'Kenaikan Kelas & Kelulusan','421.6','SK kelulusan, daftar alumni','2025-12-03 19:04:29','2025-12-03 19:04:29'),(22,'Kegiatan Belajar Mengajar','421.7','Jurnal mengajar, RPP','2025-12-03 19:04:29','2025-12-03 19:04:29'),(23,'Layanan BK','421.8','Kasus Siswa, layanan konseling','2025-12-03 19:04:29','2025-12-03 19:04:29'),(24,'Kelembagaan Sekolah','422','Status akreditasi, izin operasional','2025-12-03 19:04:29','2025-12-03 19:04:29'),(25,'Akreditasi','422.1','Dokumen pendukung BAN-SM','2025-12-03 19:04:29','2025-12-03 19:04:29'),(26,'Kerja Sama Industri (PSG/PKL)','422.2','MoU, surat penempatan PKL','2025-12-03 19:04:29','2025-12-03 19:04:29'),(27,'Komite Sekolah','422.3',NULL,'2025-12-03 19:04:29','2025-12-03 19:04:29'),(28,'Kesiswaan','423','Ekstrakurikuler & OSIS','2025-12-03 19:04:29','2025-12-03 19:04:29'),(29,'Ekstrakurikuler','423.1',NULL,'2025-12-03 19:04:29','2025-12-03 19:04:29'),(30,'OSIS & Organisasi Siswa','423.2',NULL,'2025-12-03 19:04:29','2025-12-03 19:04:29'),(31,'Prestasi Siswa','423.3',NULL,'2025-12-03 19:04:29','2025-12-03 19:04:29'),(32,'Perekonomian','500',NULL,'2025-12-03 19:04:55','2025-12-03 19:04:55'),(33,'Pekerjaan Umum dan Sarpras','600','Prasarana dan fasilitas sekolah','2025-12-03 19:04:55','2025-12-03 19:04:55'),(34,'Tanah & Bangunan','611','Sertifikat, denah','2025-12-03 19:04:55','2025-12-03 19:04:55'),(35,'Ruang Kelas & Laboratorium','612',NULL,'2025-12-03 19:04:55','2025-12-03 19:04:55'),(36,'Inventaris & Aset','613','KIB A-F','2025-12-03 19:04:55','2025-12-03 19:04:55'),(37,'Pemeliharaan Sarpras','614','Renovasi, perbaikan fasilitas','2025-12-03 19:04:55','2025-12-03 19:04:55'),(38,'Administrasi Keuangan','700','Anggaran & pembiayaan sekolah','2025-12-03 19:04:55','2025-12-03 19:04:55'),(39,'RKAS','711','Rencana Kegiatan & Anggaran Sekolah','2025-12-03 19:04:55','2025-12-03 19:04:55'),(40,'Dana BOS','712','SPJ BOS, laporan realisasi','2025-12-03 19:04:55','2025-12-03 19:04:55'),(41,'BAST','713','Berita Acara Serah Terima Barang','2025-12-03 19:04:55','2025-12-03 19:04:55'),(42,'Gaji & Honor','714',NULL,'2025-12-03 19:04:55','2025-12-03 19:04:55'),(43,'Kepegawaian','800','Administrasi guru & tenaga pendidik','2025-12-03 19:04:55','2025-12-03 19:04:55'),(44,'Pengangkatan & SK Pegawai','811',NULL,'2025-12-03 19:04:55','2025-12-03 19:04:55'),(45,'Cuti & Ketidakhadiran','812',NULL,'2025-12-03 19:04:55','2025-12-03 19:04:55'),(46,'Kenaikan Pangkat','813',NULL,'2025-12-03 19:04:55','2025-12-03 19:04:55'),(47,'Kinerja & Penilaian Guru','814',NULL,'2025-12-03 19:04:55','2025-12-03 19:04:55'),(48,'Sertifikasi Guru','815','PLPG, PPG, Tunjangan profesi','2025-12-03 19:04:55','2025-12-03 19:04:55'),(49,'Organisasi & Ketatalaksanaan','900',NULL,'2025-12-03 19:04:55','2025-12-03 19:04:55'),(50,'Struktur Organisasi','911',NULL,'2025-12-03 19:04:55','2025-12-03 19:04:55'),(51,'SOP & Tata Kelola','912',NULL,'2025-12-03 19:04:55','2025-12-03 19:04:55'),(52,'Surat Keputusan Kepala Sekolah','913',NULL,'2025-12-03 19:04:55','2025-12-03 19:04:55'),(53,'Surat Cinta','101.2','Surat cinta untuk starla','2025-12-05 07:17:23','2025-12-05 07:17:23');
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
  KEY `ix_diploma_student_name` (`student_name`),
  KEY `ix_diploma_major` (`major`),
  KEY `ix_diploma_academic_year` (`academic_year`),
  CONSTRAINT `diploma_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `diploma`
--

LOCK TABLES `diploma` WRITE;
/*!40000 ALTER TABLE `diploma` DISABLE KEYS */;
INSERT INTO `diploma` VALUES (4,'DOC/IJZ/2024/003','Citra Lestari','Akuntansi dan Keuangan Lembaga','2023/2024',1,'2024-06-16 10:15:00',NULL,1,'2025-12-03 20:36:50','2025-12-03 20:36:50'),(5,'DOC/IJZ/2023/089','Dedi Kurniawan','Teknik Kendaraan Ringan','2022/2023',0,NULL,NULL,1,'2025-12-03 20:36:50','2025-12-03 20:36:50'),(6,'DOC/IJZ/2024/004','Eka Putri','Teknik Komputer dan Jaringan','2023/2024',1,'2024-06-20 14:00:00','uploads/receipt_eka_004.jpg',1,'2025-12-03 20:36:50','2025-12-03 20:36:50'),(7,'DOC/IJZ/2024/005','Fajar Nugraha','Rekayasa Perangkat Lunak','2023/2024',0,NULL,NULL,1,'2025-12-03 20:36:50','2025-12-03 20:36:50'),(8,'DOC/IJZ/2024/006','Gita Permata','Perhotelan','2023/2024',1,'2024-07-01 08:45:00','uploads/receipt_gita_006.pdf',1,'2025-12-03 20:36:50','2025-12-03 20:36:50'),(9,'DOC/IJZ/2024/007','Hendra Wijaya','Teknik Kendaraan Ringan','2023/2024',0,NULL,NULL,1,'2025-12-03 20:36:50','2025-12-03 20:36:50'),(10,'DOC/IJZ/2024/008','Indah Sari','Akuntansi dan Keuangan Lembaga','2023/2024',1,'2024-08-10 11:20:00','uploads/receipt_indah_008.png',1,'2025-12-03 20:36:50','2025-12-03 20:36:50'),(11,'DOC/IJZ/2024/009','Joko Susilo','Teknik Komputer dan Jaringan','2023/2024',0,NULL,NULL,1,'2025-12-03 20:36:50','2025-12-03 20:36:50'),(12,'DOC/IJZ/2024/011','Andi Saputra','RPL','2024/2025',0,NULL,NULL,1,'2025-12-05 00:06:50','2025-12-05 00:06:50');
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
) ENGINE=InnoDB AUTO_INCREMENT=104 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `incoming_letter`
--

LOCK TABLES `incoming_letter` WRITE;
/*!40000 ALTER TABLE `incoming_letter` DISABLE KEYS */;
INSERT INTO `incoming_letter` VALUES (92,'420/001/SMK/2025','2025-01-10 00:00:00','2025-01-11 00:00:00','Dinas Pendidikan Kota','Edaran Pelaksanaan Ujian Sekolah','/uploads/edaran-us.pdf',22,1,'2025-12-03 20:18:33','2025-12-03 20:18:33'),(93,'421/015/SMK/2025','2025-01-12 00:00:00','2025-01-13 00:00:00','Komite Sekolah','Rapat Penyusunan RKAS',NULL,40,1,'2025-12-03 20:18:33','2025-12-03 20:18:33'),(94,'600/004/SMK/2025','2025-02-01 00:00:00','2025-02-01 00:00:00','CV Bangun Jaya','Penawaran Renovasi Laboratorium','/uploads/penawaran-renovasi.pdf',36,1,'2025-12-03 20:18:33','2025-12-03 20:18:33'),(95,'700/008/SMK/2025','2025-02-05 00:00:00','2025-02-06 00:00:00','Bendahara BOS','Laporan Penggunaan Dana BOS Januari','/uploads/laporan-bos-jan.pdf',40,1,'2025-12-03 20:18:33','2025-12-03 20:18:33'),(96,'800/021/SMK/2025','2025-02-10 00:00:00','2025-02-11 00:00:00','BKD Provinsi','Pemberitahuan Usulan Kenaikan Pangkat Guru',NULL,46,1,'2025-12-03 20:18:33','2025-12-03 20:18:33'),(98,'421/040/SMK/2025','2025-03-08 00:00:00','2025-03-09 00:00:00','Orang Tua/Wali Murid','Permohonan Surat Keterangan Aktif',NULL,17,1,'2025-12-03 20:18:33','2025-12-03 20:18:33'),(99,'311/009/SMK/2025','2025-03-15 00:00:00','2025-03-15 00:00:00','Polsek Setempat','Undangan Sosialisasi Anti Bullying','/uploads/sosialisasi-bully.pdf',11,1,'2025-12-03 20:18:33','2025-12-03 20:18:33'),(100,'500/028/SMK/2025','2025-04-01 00:00:00','2025-04-02 00:00:00','Koperasi Sekolah','Permohonan Pembelian ATK Semester Baru',NULL,36,1,'2025-12-03 20:18:33','2025-12-03 20:18:33'),(102,'900/014/SMK/2022','2025-12-04 00:00:00','2025-12-04 00:00:00','Mahasiswa','',NULL,16,1,'2025-12-04 22:53:47','2025-12-04 22:58:28'),(103,'423/017/SMK/2025','2025-12-04 00:00:00','2025-12-04 00:00:00','Ketua OSIS','',NULL,15,1,'2025-12-04 23:07:10','2025-12-04 23:07:10');
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
  KEY `ix_log_timestamp` (`timestamp`),
  KEY `ix_log_user_id` (`user_id`),
  KEY `ix_log_id` (`id`),
  CONSTRAINT `log_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `log`
--

LOCK TABLES `log` WRITE;
/*!40000 ALTER TABLE `log` DISABLE KEYS */;
INSERT INTO `log` VALUES (1,'Pengguna melakukan login.','2025-12-03 16:09:36',1),(2,'Pengguna membuat user baru dengan NUPTK: \'9990942\'.','2025-12-03 16:09:44',1),(3,'Pengguna memperbarui data (status) pengguna NUPTK: \'9990942\'.','2025-12-03 16:09:48',1),(4,'Pengguna \'AryaSeptiaputra\' menambahkan surat masuk nomor: \'IN-160948\'.','2025-12-03 16:09:50',1),(5,'Pengguna \'AryaSeptiaputra\' mengupdate data (subject) pada surat masuk nomor: \'IN-160948\'.','2025-12-03 16:09:54',1),(6,'Pengguna \'AryaSeptiaputra\' menambahkan surat keluar nomor: \'OUT-160954\'.','2025-12-03 16:09:57',1),(7,'Pengguna \'AryaSeptiaputra\' mengupdate (subject) surat keluar nomor: \'OUT-160954\'.','2025-12-03 16:10:01',1),(8,'Pengguna \'AryaSeptiaputra\' menambahkan ijazah No: \'DN-161000\' atas nama \'Siswa SMK Test\'.','2025-12-03 16:10:03',1),(9,'Pengguna \'AryaSeptiaputra\' mengupdate (is_collected, student_name) pada ijazah No: \'DN-161000\'.','2025-12-03 16:10:07',1),(10,'Pengguna \'AryaSeptiaputra\' menghapus surat masuk nomor: \'IN-160948\'.','2025-12-03 16:10:17',1),(11,'Pengguna \'AryaSeptiaputra\' menghapus surat keluar nomor: \'OUT-160954\'.','2025-12-03 16:10:19',1),(12,'Pengguna \'AryaSeptiaputra\' menghapus ijazah No: \'DN-161000\' milik \'Siswa SMK Test (Revisi)\'.','2025-12-03 16:10:22',1),(13,'Pengguna melakukan login.','2025-12-03 16:10:48',1),(14,'Pengguna melakukan login.','2025-12-03 16:15:00',1),(15,'Pengguna melakukan login.','2025-12-03 16:45:18',1),(16,'Pengguna melakukan login.','2025-12-03 16:54:06',1),(17,'Pengguna melakukan login.','2025-12-03 16:59:01',1),(18,'Pengguna melakukan login.','2025-12-03 17:15:34',1),(19,'Pengguna melakukan login.','2025-12-03 17:41:19',1),(20,'Pengguna melakukan login.','2025-12-03 17:57:55',1),(21,'Pengguna melakukan login.','2025-12-03 18:12:31',1),(22,'Pengguna melakukan login.','2025-12-03 18:13:52',1),(23,'Pengguna melakukan login.','2025-12-03 18:52:33',1),(24,'Pengguna melakukan login.','2025-12-03 20:04:24',1),(25,'Pengguna melakukan login.','2025-12-03 20:28:18',1),(26,'Pengguna melakukan login.','2025-12-03 20:44:40',1),(27,'Pengguna melakukan login.','2025-12-03 21:08:26',1),(28,'Pengguna melakukan login.','2025-12-03 21:10:48',1),(29,'Pengguna melakukan login.','2025-12-03 21:29:33',1),(30,'Pengguna melakukan login.','2025-12-03 22:01:49',1),(31,'Pengguna melakukan login.','2025-12-03 22:02:14',1),(32,'Pengguna melakukan login.','2025-12-03 22:05:04',1),(33,'Pengguna melakukan login.','2025-12-03 22:05:59',1),(34,'Pengguna melakukan login.','2025-12-03 22:06:52',1),(35,'Pengguna melakukan login.','2025-12-03 22:07:55',1),(36,'Pengguna melakukan login.','2025-12-03 22:27:29',1),(37,'Pengguna melakukan login.','2025-12-03 22:40:03',1),(38,'Pengguna melakukan login.','2025-12-03 22:41:53',1),(39,'Pengguna melakukan login.','2025-12-03 22:45:30',1),(40,'Pengguna melakukan login.','2025-12-03 23:33:50',1),(41,'Pengguna melakukan login.','2025-12-04 15:37:10',1),(42,'Pengguna melakukan login.','2025-12-04 15:59:14',1),(43,'Pengguna AryaSeptiaputra melakukan login.','2025-12-04 16:34:19',1),(44,'Pengguna memperbarui data (username, role, status, password) pengguna NUPTK: \'152022190\'.','2025-12-04 16:35:01',1),(45,'Pengguna AryaSeptiaputra melakukan login.','2025-12-04 16:35:20',1),(46,'Pengguna memperbarui data (username, role, status) pengguna NUPTK: \'152022190\'.','2025-12-04 16:35:39',1),(47,'Pengguna Arya Septiaputra melakukan login.','2025-12-04 16:35:52',1),(48,'Pengguna Arya Septiaputra melakukan login.','2025-12-04 16:51:05',1),(49,'Pengguna Arya Septiaputra melakukan login.','2025-12-04 17:08:29',1),(50,'Pengguna Arya Septiaputra melakukan login.','2025-12-04 17:40:31',1),(51,'Pengguna Arya Septiaputra melakukan login.','2025-12-04 17:40:44',1),(52,'Pengguna Arya Septiaputra melakukan login.','2025-12-04 17:56:36',1),(53,'Pengguna Arya Septiaputra melakukan login.','2025-12-04 18:49:18',1),(54,'Pengguna Arya Septiaputra melakukan login.','2025-12-04 20:19:58',1),(55,'Pengguna Arya Septiaputra melakukan login.','2025-12-04 22:47:50',1),(56,'Pengguna \'Arya Septiaputra\' menghapus surat masuk nomor: \'900/014/SMK/2025\'.','2025-12-04 22:52:12',1),(57,'Pengguna \'Arya Septiaputra\' menambahkan surat masuk nomor: \'900/014/SMK/2022\'.','2025-12-04 22:53:47',1),(58,'Pengguna memperbarui data (username, role, status) pengguna NUPTK: \'152022190\'.','2025-12-04 22:55:22',1),(59,'Pengguna Arya Eka Septiaputra melakukan login.','2025-12-04 22:55:42',1),(60,'Pengguna \'Arya Eka Septiaputra\' mengupdate data (number, sender, subject, letter_date, received_date, classification_id) pada surat masuk: \'900/014/SMK/2022\'.','2025-12-04 22:58:28',1),(61,'Pengguna \'Arya Eka Septiaputra\' menghapus surat masuk nomor: \'423/017/SMK/2025\'.','2025-12-04 23:06:51',1),(62,'Pengguna \'Arya Eka Septiaputra\' menambahkan surat masuk nomor: \'423/017/SMK/2025\'.','2025-12-04 23:07:10',1),(63,'Pengguna Arya Eka Septiaputra melakukan login.','2025-12-04 23:10:03',1),(64,'Pengguna \'Arya Eka Septiaputra\' mengupdate (number, destination, subject, letter_date, sent_date, classification_id) surat keluar nomor: \'090/KEU-HON/SMK/IX/2022\'.','2025-12-04 23:11:59',1),(65,'Pengguna Arya Eka Septiaputra melakukan login.','2025-12-04 23:44:01',1),(66,'Pengguna Arya Eka Septiaputra melakukan login.','2025-12-04 23:59:12',1),(67,'Pengguna \'Arya Eka Septiaputra\' menghapus ijazah No: \'DOC/IJZ/2024/001\' milik \'Andi Saputra\'.','2025-12-05 00:06:07',1),(68,'Pengguna \'Arya Eka Septiaputra\' menghapus ijazah No: \'DOC/IJZ/2024/002\' milik \'Budi Santoso\'.','2025-12-05 00:06:29',1),(69,'Pengguna \'Arya Eka Septiaputra\' menambahkan ijazah No: \'DOC/IJZ/2024/011\' atas nama \'Andi Saputra\'.','2025-12-05 00:06:50',1),(70,'Pengguna Arya Eka Septiaputra melakukan login.','2025-12-05 06:05:08',1),(71,'Pengguna Arya Eka Septiaputra melakukan login.','2025-12-05 07:16:31',1),(72,'Pengguna Arya Eka Septiaputra melakukan login.','2025-12-05 12:34:16',1),(73,'Pengguna Arya Eka Septiaputra melakukan login.','2025-12-05 12:48:21',1),(74,'Pengguna Arya Eka Septiaputra melakukan login.','2025-12-05 13:13:37',1),(75,'Pengguna Arya Eka Septiaputra melakukan login.','2025-12-05 13:45:47',1),(76,'Pengguna membuat user baru dengan NUPTK: \'152022174\'.','2025-12-05 13:47:46',1),(77,'Pengguna Arya Eka Septiaputra melakukan login.','2025-12-05 14:11:24',1),(78,'Pengguna Arya Eka Septiaputra melakukan login.','2025-12-05 14:42:59',1),(79,'Pengguna Arya Eka Septiaputra melakukan login.','2025-12-05 15:00:20',1),(80,'Pengguna Arya Eka Septiaputra melakukan login.','2025-12-05 15:51:21',1);
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
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `outgoing_letter`
--

LOCK TABLES `outgoing_letter` WRITE;
/*!40000 ALTER TABLE `outgoing_letter` DISABLE KEYS */;
INSERT INTO `outgoing_letter` VALUES (2,'001/PEG/SMK/I/2024','2024-01-05 08:00:00','2024-01-05 09:00:00','Dinas Pendidikan Kota','Laporan Data Kepegawaian Bulanan',0,'files/laporan_pegawai_jan.pdf',43,1,'2025-12-03 20:26:10','2025-12-03 20:26:10'),(3,'002/SK-PEG/SMK/I/2024','2024-01-10 09:00:00','2024-01-10 10:00:00','Bpk. Ahmad Fauzi, S.Kom','SK Pengangkatan Kepala Lab Komputer',1,'files/sk_lab_komputer.pdf',43,1,'2025-12-03 20:26:10','2025-12-03 20:26:10'),(4,'015/BOS/SMK/II/2024','2024-02-12 10:00:00','2024-02-12 13:00:00','Tim BOS Provinsi','Revisi RKAS Tahun Anggaran 2024',0,'files/rkas_revisi_v1.xlsx',40,1,'2025-12-03 20:26:10','2025-12-03 20:26:10'),(5,'022/KUR/SMK/III/2024','2024-03-01 07:00:00','2024-03-01 07:30:00','Seluruh Wali Murid Kelas XII','Pemberitahuan Jadwal Ujian Sekolah',0,NULL,16,1,'2025-12-03 20:26:10','2025-12-03 20:26:10'),(6,'030/HUBIN/SMK/IV/2024','2024-04-05 11:00:00','2024-04-06 08:00:00','PT. Telkom Indonesia','Permohonan Kunjungan Industri Siswa TKJ',0,'files/proposal_kunjungan.pdf',26,1,'2025-12-03 20:26:10','2025-12-03 20:26:10'),(7,'045/SARPRAS/SMK/V/2024','2024-05-15 14:00:00','2024-05-15 15:00:00','Toko Bangunan Sejahtera','Purchase Order (PO) Perbaikan Atap Aula',0,NULL,36,1,'2025-12-03 20:26:10','2025-12-03 20:26:10'),(8,'055/SIS/SMK/VI/2024','2024-06-10 08:30:00','2024-06-10 09:00:00','Ketua OSIS','Persetujuan Proposal Class Meeting',1,NULL,28,1,'2025-12-03 20:26:10','2025-12-03 20:26:10'),(9,'062/KEU/SMK/VII/2024','2024-07-02 09:00:00','2024-07-02 11:00:00','Bank Jabar Banten (BJB)','Permohonan Rekening Koran Sekolah',0,NULL,38,1,'2025-12-03 20:26:10','2025-12-03 20:26:10'),(10,'078/AKR/SMK/VIII/2024','2024-08-20 10:00:00','2024-08-20 10:30:00','Pengawas Pembina','Laporan Progres Persiapan Akreditasi',0,'files/progres_akreditasi.docx',25,1,'2025-12-03 20:26:10','2025-12-03 20:26:10'),(11,'090/KEU-HON/SMK/IX/2022','2024-09-25 00:00:00','2024-09-25 00:00:00','Bendahara Sekolah','Rekapitulasi Jam Mengajar Guru Honorer',0,'files/rekap_jam_sept.xlsx',42,1,'2025-12-03 20:26:10','2025-12-04 23:11:59');
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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'152022190','Arya Eka Septiaputra','$argon2id$v=19$m=65536,t=3,p=4$1HpPiTFGSMmZ894753zPOQ$7BOi0dnmOKeLaHP7fBEwSnsVM7ciEKvBrhnppCVsxg0','admin','active','2025-12-03 16:09:21','2025-12-04 22:55:22'),(3,'112022190','AryaSeptiaputra','$argon2id$v=19$m=65536,t=3,p=4$7n3v/T8nxDhHaA1BCKGU8g$HZSxC12HsTwUPHTKJC33hAhdOwLQwRPlI2zK6vx4e04','admin','active','2025-12-05 12:47:57','2025-12-05 12:47:57'),(4,'152022174','Alif Fathurrohman','$argon2id$v=19$m=65536,t=3,p=4$VCqlVOqdc24txdg7x7i31g$y1TDidb8wbmSMX5pKZbrZmeS768vaug/niFTcSCUWGo','headmaster','active','2025-12-05 13:47:46','2025-12-05 13:47:46');
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

-- Dump completed on 2025-12-06  5:41:19
