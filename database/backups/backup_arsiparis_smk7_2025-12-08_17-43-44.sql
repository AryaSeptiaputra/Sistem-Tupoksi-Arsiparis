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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `backup`
--

LOCK TABLES `backup` WRITE;
/*!40000 ALTER TABLE `backup` DISABLE KEYS */;
INSERT INTO `backup` VALUES (1,'backup_arsiparis_smk7_2025-12-08_07-21-23.sql','SUCCESS','Database backup created successfully.','2025-12-08 07:21:24',1);
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
  `final_action` enum('destroy','permanent','assess') NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_classification_name` (`name`),
  UNIQUE KEY `ix_classification_code` (`code`),
  KEY `ix_classification_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classification`
--

LOCK TABLES `classification` WRITE;
/*!40000 ALTER TABLE `classification` DISABLE KEYS */;
INSERT INTO `classification` VALUES (1,'Administrasi Umum','01-ADM','Arsip administrasi umum sekolah: surat masuk/keluar, undangan, notulen rapat, SK kepala sekolah, dan dokumen tata usaha umum.',2,3,'assess','2025-12-07 22:15:20','2025-12-07 22:15:20'),(2,'Kesiswaan','02-SIS','Arsip kesiswaan: data biodata siswa, mutasi masuk/keluar, catatan pelanggaran, prestasi siswa, dan layanan konseling.',5,10,'permanent','2025-12-07 22:15:20','2025-12-07 22:15:20'),(3,'Kepegawaian','03-KEP','Arsip kepegawaian guru dan tenaga kependidikan: biodata, riwayat jabatan, SK pengangkatan, kenaikan pangkat, cuti, dan penilaian kinerja.',5,10,'assess','2025-12-07 22:15:20','2025-12-07 22:15:20'),(4,'Keuangan','04-KEU','Arsip keuangan sekolah: RKAS/RAPBS, pembukuan kas, laporan BOS, bukti pengeluaran, dan pertanggungjawaban dana.',5,5,'assess','2025-12-07 22:15:20','2025-12-07 22:15:20'),(5,'Kurikulum','05-KUR','Arsip kurikulum dan pembelajaran: dokumen kurikulum, program tahunan/semester, perangkat pembelajaran, bank soal, dan evaluasi pembelajaran.',5,10,'permanent','2025-12-07 22:15:20','2025-12-07 22:15:20'),(6,'Sarana dan Prasarana','06-SAR','Arsip pengelolaan sarana prasarana: daftar inventaris, berita acara serah terima barang, pemeliharaan, perbaikan, dan penghapusan aset.',4,6,'assess','2025-12-07 22:15:20','2025-12-07 22:15:20'),(7,'Hubungan Masyarakat dan Kemitraan','07-HUM','Arsip hubungan sekolah dengan masyarakat dan institusi lain: kerja sama (MoU), undangan eksternal, publikasi kegiatan, dokumentasi hubungan kemitraan.',3,3,'assess','2025-12-07 22:15:20','2025-12-07 22:15:20'),(8,'Perpustakaan','08-PER','Arsip pengelolaan perpustakaan: katalog koleksi, pengadaan buku, kartu anggota, daftar peminjaman/pengembalian, dan laporan layanan perpustakaan.',2,3,'destroy','2025-12-07 22:15:20','2025-12-07 22:15:20'),(9,'Ekstrakurikuler','09-EKS','Arsip kegiatan ekstrakurikuler: program kerja, jadwal latihan, daftar hadir, surat tugas lomba, dan dokumentasi kegiatan.',3,4,'assess','2025-12-07 22:15:20','2025-12-07 22:15:20'),(10,'Arsip Khusus (Ijazah dan Alumni)','10-KHS','Arsip bernilai vital dan historis: blangko dan daftar ijazah, leger nilai akhir, arsip sertifikat, serta data alumni.',5,25,'permanent','2025-12-07 22:15:20','2025-12-07 22:15:20');
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
  `storage_location_id` int DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_diploma_number` (`number`),
  KEY `user_id` (`user_id`),
  KEY `storage_location_id` (`storage_location_id`),
  KEY `ix_diploma_academic_year` (`academic_year`),
  KEY `ix_diploma_id` (`id`),
  KEY `ix_diploma_student_name` (`student_name`),
  KEY `ix_diploma_major` (`major`),
  CONSTRAINT `diploma_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `diploma_ibfk_2` FOREIGN KEY (`storage_location_id`) REFERENCES `storage_location` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `diploma`
--

LOCK TABLES `diploma` WRITE;
/*!40000 ALTER TABLE `diploma` DISABLE KEYS */;
INSERT INTO `diploma` VALUES (1,'DOC/IJZ/2024/003','Andi Saputra','Kimia Industri','2023/2024',0,NULL,'storage\\documents\\diplomas\\4._Metode_Penjadwalan_Proyek.pdf',1,10,'2025-12-07 23:24:27','2025-12-07 23:24:27');
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
  `document_type` enum('sk_cpns','sk_pangkat','sk_berkala','ijazah','sertifikat','ktp_kk','lainnya') NOT NULL,
  `document_year` int DEFAULT NULL,
  `description` text,
  `attachment_path` varchar(255) DEFAULT NULL,
  `employee_id` int NOT NULL,
  `storage_location_id` int DEFAULT NULL,
  `created_by` int NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `storage_location_id` (`storage_location_id`),
  KEY `created_by` (`created_by`),
  KEY `ix_employee_archive_employee_id` (`employee_id`),
  KEY `ix_employee_archive_id` (`id`),
  CONSTRAINT `employee_archive_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `user` (`id`),
  CONSTRAINT `employee_archive_ibfk_2` FOREIGN KEY (`storage_location_id`) REFERENCES `storage_location` (`id`),
  CONSTRAINT `employee_archive_ibfk_3` FOREIGN KEY (`created_by`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employee_archive`
--

LOCK TABLES `employee_archive` WRITE;
/*!40000 ALTER TABLE `employee_archive` DISABLE KEYS */;
INSERT INTO `employee_archive` VALUES (1,'SK Kenaikan Jabatan','sk_cpns',2025,'SK kenaikan jabatan bapak Arya Eka Septiaputra','storage\\documents\\employee_archives\\5._Trello.pdf',2,4,1,'2025-12-08 07:29:38','2025-12-08 07:29:38');
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
  `category` enum('bos_reguler','bos_kinerja','komite','bop','lainnya') NOT NULL,
  `amount` bigint DEFAULT NULL,
  `description` text,
  `attachment_path` varchar(255) DEFAULT NULL,
  `classification_id` int NOT NULL,
  `storage_location_id` int DEFAULT NULL,
  `archive_status` enum('active','inactive','destroyed') NOT NULL,
  `user_id` int NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `classification_id` (`classification_id`),
  KEY `storage_location_id` (`storage_location_id`),
  KEY `user_id` (`user_id`),
  KEY `ix_finance_archive_id` (`id`),
  KEY `ix_finance_archive_fiscal_year` (`fiscal_year`),
  CONSTRAINT `finance_archive_ibfk_1` FOREIGN KEY (`classification_id`) REFERENCES `classification` (`id`),
  CONSTRAINT `finance_archive_ibfk_2` FOREIGN KEY (`storage_location_id`) REFERENCES `storage_location` (`id`),
  CONSTRAINT `finance_archive_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `finance_archive`
--

LOCK TABLES `finance_archive` WRITE;
/*!40000 ALTER TABLE `finance_archive` DISABLE KEYS */;
INSERT INTO `finance_archive` VALUES (1,'Laporan BPJS BOS',2025,NULL,'bos_reguler',200000,'Uang Kesahatan para guru','storage\\documents\\finance_archives\\Power_Point_Seminar_Proposal_-_Draft.pdf',4,4,'active',1,'2025-12-08 06:24:49','2025-12-08 06:25:14');
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
  `user_id` int NOT NULL,
  `storage_location_id` int DEFAULT NULL,
  `archive_status` enum('active','inactive','destroyed') NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_incoming_letter_number` (`number`),
  KEY `ix_incoming_letter_sender` (`sender`),
  KEY `ix_incoming_letter_user_id` (`user_id`),
  KEY `ix_incoming_letter_classification_id` (`classification_id`),
  KEY `ix_incoming_letter_storage_location_id` (`storage_location_id`),
  KEY `ix_incoming_letter_letter_date` (`letter_date`),
  KEY `ix_incoming_letter_received_date` (`received_date`),
  KEY `ix_incoming_letter_id` (`id`),
  CONSTRAINT `incoming_letter_ibfk_1` FOREIGN KEY (`classification_id`) REFERENCES `classification` (`id`),
  CONSTRAINT `incoming_letter_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `incoming_letter_ibfk_3` FOREIGN KEY (`storage_location_id`) REFERENCES `storage_location` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `incoming_letter`
--

LOCK TABLES `incoming_letter` WRITE;
/*!40000 ALTER TABLE `incoming_letter` DISABLE KEYS */;
INSERT INTO `incoming_letter` VALUES (1,'900/014/SMK/2022','2025-12-07 00:00:00','2025-12-07 00:00:00','Mahasiswa','Pengajuan Kegiatan Pengabdian Kepada Masyarakat','storage\\documents\\incoming_letters\\1._Penyusunan_Proposal_PKM-K.pdf',7,1,3,'active','2025-12-07 22:28:38','2025-12-07 22:28:38');
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
  KEY `ix_log_user_id` (`user_id`),
  KEY `ix_log_id` (`id`),
  KEY `ix_log_timestamp` (`timestamp`),
  CONSTRAINT `log_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `log`
--

LOCK TABLES `log` WRITE;
/*!40000 ALTER TABLE `log` DISABLE KEYS */;
INSERT INTO `log` VALUES (1,'Pengguna AryaSeptiaputra melakukan login.','2025-12-07 20:59:05',1),(2,'Pengguna membuat user baru dengan NUPTK: \'152022190\'.','2025-12-07 21:03:13',1),(3,'Pengguna Arya Eka Septiaputra melakukan login.','2025-12-07 21:03:41',2),(4,'Pengguna AryaSeptiaputra melakukan login.','2025-12-07 21:16:06',1),(5,'Pengguna AryaSeptiaputra melakukan login.','2025-12-07 21:43:07',1),(6,'Pengguna AryaSeptiaputra melakukan login.','2025-12-07 22:02:03',1),(7,'Pengguna AryaSeptiaputra melakukan login.','2025-12-07 22:17:52',1),(8,'Tambah surat masuk No: \'900/014/SMK/2022\'','2025-12-07 22:28:38',1),(9,'Pengguna AryaSeptiaputra melakukan login.','2025-12-07 22:33:38',1),(10,'Pengguna AryaSeptiaputra melakukan login.','2025-12-07 22:51:23',1),(11,'Pengguna Arya Eka Septiaputra melakukan login.','2025-12-07 22:56:49',2),(12,'Pengguna AryaSeptiaputra melakukan login.','2025-12-07 22:59:45',1),(13,'Menambahkan surat keluar No: \'900/014/SMK/2025\'','2025-12-07 23:01:03',1),(14,'Update surat keluar No: \'900/014/SMK/2025\'','2025-12-07 23:09:48',1),(15,'Update surat keluar No: \'900/014/SMK/2025\'','2025-12-07 23:10:07',1),(16,'Pengguna AryaSeptiaputra melakukan login.','2025-12-07 23:15:32',1),(17,'Tambah Ijazah: Andi Saputra','2025-12-07 23:24:27',1),(18,'Pengguna AryaSeptiaputra melakukan login.','2025-12-07 23:30:47',1),(19,'Pengguna AryaSeptiaputra melakukan login.','2025-12-08 05:55:02',1),(20,'Pengguna AryaSeptiaputra melakukan login.','2025-12-08 06:11:46',1),(21,'Menambahkan Arsip Keuangan: \'Laporan BPJS BOS\' (2025)','2025-12-08 06:24:49',1),(22,'Update Arsip Keuangan: \'Laporan BPJS BOS\'','2025-12-08 06:25:14',1),(23,'Pengguna AryaSeptiaputra melakukan login.','2025-12-08 06:27:03',1),(24,'Pengguna AryaSeptiaputra melakukan login.','2025-12-08 06:45:40',1),(25,'Pengguna AryaSeptiaputra melakukan login.','2025-12-08 07:04:22',1),(26,'Pengguna AryaSeptiaputra melakukan login.','2025-12-08 07:20:03',1),(27,'Upload Arsip Pegawai (Arya Eka Septiaputra): SK Kenaikan Jabatan','2025-12-08 07:29:38',1),(28,'Pengguna AryaSeptiaputra melakukan login.','2025-12-08 07:49:48',1),(29,'Pengguna AryaSeptiaputra melakukan login.','2025-12-08 11:43:11',1),(30,'Pengguna AryaSeptiaputra melakukan login.','2025-12-08 17:43:05',1);
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
  `storage_location_id` int DEFAULT NULL,
  `archive_status` enum('active','inactive','destroyed') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `user_id` int NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `storage_location_id` (`storage_location_id`),
  KEY `ix_outgoing_letter_letter_date` (`letter_date`),
  KEY `ix_outgoing_letter_user_id` (`user_id`),
  KEY `ix_outgoing_letter_classification_id` (`classification_id`),
  KEY `ix_outgoing_letter_sent_date` (`sent_date`),
  KEY `ix_outgoing_letter_id` (`id`),
  KEY `ix_outgoing_letter_number` (`number`),
  KEY `ix_outgoing_letter_destination` (`destination`),
  KEY `ix_outgoing_letter_is_decree` (`is_decree`),
  CONSTRAINT `outgoing_letter_ibfk_1` FOREIGN KEY (`classification_id`) REFERENCES `classification` (`id`),
  CONSTRAINT `outgoing_letter_ibfk_2` FOREIGN KEY (`storage_location_id`) REFERENCES `storage_location` (`id`),
  CONSTRAINT `outgoing_letter_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `outgoing_letter`
--

LOCK TABLES `outgoing_letter` WRITE;
/*!40000 ALTER TABLE `outgoing_letter` DISABLE KEYS */;
INSERT INTO `outgoing_letter` VALUES (1,'900/014/SMK/2025','2025-12-07 00:00:00','2025-12-07 00:00:00','Institut Teknologi Nasional','Perihal surat balasan kegiatan pengabdian kepada masyarakat blablablablblablablablablabla',0,'storage\\documents\\outgoing_letters\\3._Manajemen_Integrasi_Proyek.pdf',7,3,'active',1,'2025-12-07 23:01:03','2025-12-07 23:10:07');
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
INSERT INTO `storage_location` VALUES (1,'Ruang Arsip Utama','Lokasi penyimpanan berkas jangka panjang dengan sistem klasifikasi dan kontrol akses.','2025-12-07 22:26:28','2025-12-07 22:26:28'),(2,'Lemari Arsip Kesiswaan','Lemari khusus penyimpanan arsip siswa seperti mutasi, pelanggaran, prestasi, dan administrasi kelas.','2025-12-07 22:26:28','2025-12-07 22:26:28'),(3,'Ruang Tata Usaha','Tempat penyimpanan arsip aktif yang sering diakses untuk kebutuhan administrasi sekolah.','2025-12-07 22:26:28','2025-12-07 22:26:28'),(4,'Kabinet Keuangan','Penyimpanan laporan BOS, bukti transaksi, kwitansi, dan pembukuan keuangan lainnya.','2025-12-07 22:26:28','2025-12-07 22:26:28'),(5,'Ruang Kepala Sekolah','Lokasi arsip penting bersifat terbatas seperti nota dinas, MoU, dan dokumen strategis.','2025-12-07 22:26:28','2025-12-07 22:26:28'),(6,'Ruang Wakasek Kurikulum','Penyimpanan RPP, silabus, program semester, dan perangkat pembelajaran.','2025-12-07 22:26:28','2025-12-07 22:26:28'),(7,'Gudang Inventaris','Tempat arsip sarpras, BAST, pengadaan, pemeliharaan dan penghapusan aset.','2025-12-07 22:26:28','2025-12-07 22:26:28'),(8,'Perpustakaan Sekolah','Penyimpanan katalog buku, dokumentasi peminjaman, serta arsip pengelolaan koleksi.','2025-12-07 22:26:28','2025-12-07 22:26:28'),(9,'Ruang Ekstrakurikuler','Lokasi arsip kegiatan ekskul, jadwal latihan, dokumentasi lomba, dan surat tugas.','2025-12-07 22:26:28','2025-12-07 22:26:28'),(10,'Brankas Ijazah','Tempat penyimpanan fisik ijazah, leger nilai, dan arsip vital bernilai permanen.','2025-12-07 22:26:28','2025-12-07 22:26:28');
/*!40000 ALTER TABLE `storage_location` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'112022190','AryaSeptiaputra','$argon2id$v=19$m=65536,t=3,p=4$2psTQqh1LuV8L0VorVWKEQ$dUIcJpImlfe87JM7e9mF64d81Vvf+ebEiCXihchtNZU','admin','active','2025-12-07 20:58:46','2025-12-07 20:58:46'),(2,'152022190','Arya Eka Septiaputra','$argon2id$v=19$m=65536,t=3,p=4$pVTK+f9/T4kRIoSQEmLMOQ$y51vQ2phLD2N118kKjpqe0rlHrX9zQx0OS3/kQINYPc','headmaster','active','2025-12-07 21:03:13','2025-12-07 21:03:13');
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

-- Dump completed on 2025-12-08 17:43:44
