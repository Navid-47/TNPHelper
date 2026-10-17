-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 17, 2026 at 07:36 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `tnp_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `accounts_user`
--

CREATE TABLE `accounts_user` (
  `id` bigint(20) NOT NULL,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `role` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `accounts_user`
--

INSERT INTO `accounts_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`, `role`) VALUES
(1, 'pbkdf2_sha256$260000$g61cG7AhIOfXbzZOj97Z8A$dEkjJb5o0dvPDObkkiDLxRrIWIuUQl8+PLS6Z2PoXFk=', '2026-10-17 05:00:06.125558', 1, 'admin', 'Admin', 'User', 'admin@example.com', 1, 1, '2026-02-13 10:54:18.466247', 'admin'),
(2, 'pbkdf2_sha256$260000$AHI5A0cEW1V7SjZq7kMhYj$ZkBQyVtUjLxo4Ng2m3bxO77MSPkh7bovTXq4ijMLjao=', '2026-02-13 12:36:35.096419', 0, 'student1@example.com', 'John', 'Doe', 'student1@example.com', 0, 1, '2026-02-13 10:54:18.590854', 'student'),
(3, 'pbkdf2_sha256$260000$iNPBsovxQsJzZSnVys6SmB$F71tZMF6wa0SY13StgrndEbuYuQV0uw3+P6Vkywx+0w=', NULL, 0, 'student2@example.com', 'Jane', 'Smith', 'student2@example.com', 0, 1, '2026-02-13 10:54:18.714735', 'student'),
(4, 'pbkdf2_sha256$260000$SF2j3iCmEFMkDRUINisqFr$QPx/kccyWV/sesXaEy2+1WQr1qcpVlDTkvhIXRRi3vg=', '2026-03-14 14:42:03.111780', 0, 'student3@example.com', 'Mike', 'Johnson', 'student3@example.com', 0, 1, '2026-02-13 10:54:18.861683', 'student'),
(5, 'pbkdf2_sha256$260000$wHuxt1oLzbiydJMCcC9h8k$oIO6W/RlqAUpzDW6uLkjaxZpdGtXBgoI5/3W+IzsDAM=', NULL, 0, 'student4@example.com', 'Sarah', 'Wilson', 'student4@example.com', 0, 1, '2026-02-13 10:54:18.992032', 'student'),
(6, 'pbkdf2_sha256$260000$mlRAhTQi7dobuWm9qgLDIB$AMuh7AlzwguOM6I4el/BGUh5WS6uBxppKCUY9FrnogA=', NULL, 0, 'student5@example.com', 'David', 'Brown', 'student5@example.com', 0, 1, '2026-02-13 10:54:19.115785', 'student'),
(7, 'pbkdf2_sha256$260000$R30DJxeUt1Dq75fOnLzXHm$fFmT43j8bVHHCACWLeF9TW0oqBZCE72ck+lz+5+Khdo=', '2026-05-05 06:34:18.219123', 0, 'navid@gmail.com', 'Perampalli Navidul Hasan Liyaquat Ali', '', 'navid@gmail.com', 0, 1, '2026-03-06 15:45:10.141893', 'student'),
(8, 'pbkdf2_sha256$260000$R78VZaZq3x1C8fEZX227fu$XYXVCGeqlcE0YSpqHprIyB0qKLG+H/ZYQCJfjrl9udo=', '2026-03-07 17:36:04.950239', 0, 'misbahshaikh1425@gmail.com', 'Misbah Shaikh', '', 'misbahshaikh1425@gmail.com', 0, 1, '2026-03-07 17:35:37.051807', 'student'),
(9, 'pbkdf2_sha256$260000$Ck9l6C2PNzYbjr7hMGCiFi$7qvgzbetr+yOarr58mfANKuE9XWPrpSoedTBEgU34p0=', '2026-10-17 05:02:34.345907', 0, 'abcd@gmail.com', 'ABCD', '', 'abcd@gmail.com', 0, 1, '2026-04-01 15:27:00.050854', 'student');

-- --------------------------------------------------------

--
-- Table structure for table `accounts_user_groups`
--

CREATE TABLE `accounts_user_groups` (
  `id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `accounts_user_user_permissions`
--

CREATE TABLE `accounts_user_user_permissions` (
  `id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add content type', 4, 'add_contenttype'),
(14, 'Can change content type', 4, 'change_contenttype'),
(15, 'Can delete content type', 4, 'delete_contenttype'),
(16, 'Can view content type', 4, 'view_contenttype'),
(17, 'Can add session', 5, 'add_session'),
(18, 'Can change session', 5, 'change_session'),
(19, 'Can delete session', 5, 'delete_session'),
(20, 'Can view session', 5, 'view_session'),
(21, 'Can add user', 6, 'add_user'),
(22, 'Can change user', 6, 'change_user'),
(23, 'Can delete user', 6, 'delete_user'),
(24, 'Can view user', 6, 'view_user'),
(25, 'Can add Student', 7, 'add_student'),
(26, 'Can change Student', 7, 'change_student'),
(27, 'Can delete Student', 7, 'delete_student'),
(28, 'Can view Student', 7, 'view_student'),
(29, 'Can add Placement Drive', 8, 'add_drive'),
(30, 'Can change Placement Drive', 8, 'change_drive'),
(31, 'Can delete Placement Drive', 8, 'delete_drive'),
(32, 'Can view Placement Drive', 8, 'view_drive'),
(33, 'Can add Drive Application', 9, 'add_application'),
(34, 'Can change Drive Application', 9, 'change_application'),
(35, 'Can delete Drive Application', 9, 'delete_application'),
(36, 'Can view Drive Application', 9, 'view_application');

-- --------------------------------------------------------

--
-- Table structure for table `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(6, 'accounts', 'user'),
(1, 'admin', 'logentry'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(4, 'contenttypes', 'contenttype'),
(5, 'sessions', 'session'),
(7, 'students', 'student'),
(9, 'tpo', 'application'),
(8, 'tpo', 'drive');

-- --------------------------------------------------------

--
-- Table structure for table `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2026-02-13 10:54:08.789894'),
(2, 'contenttypes', '0002_remove_content_type_name', '2026-02-13 10:54:08.855882'),
(3, 'auth', '0001_initial', '2026-02-13 10:54:09.050506'),
(4, 'auth', '0002_alter_permission_name_max_length', '2026-02-13 10:54:09.104163'),
(5, 'auth', '0003_alter_user_email_max_length', '2026-02-13 10:54:09.112224'),
(6, 'auth', '0004_alter_user_username_opts', '2026-02-13 10:54:09.118872'),
(7, 'auth', '0005_alter_user_last_login_null', '2026-02-13 10:54:09.124496'),
(8, 'auth', '0006_require_contenttypes_0002', '2026-02-13 10:54:09.128345'),
(9, 'auth', '0007_alter_validators_add_error_messages', '2026-02-13 10:54:09.135449'),
(10, 'auth', '0008_alter_user_username_max_length', '2026-02-13 10:54:09.143136'),
(11, 'auth', '0009_alter_user_last_name_max_length', '2026-02-13 10:54:09.154266'),
(12, 'auth', '0010_alter_group_name_max_length', '2026-02-13 10:54:09.168773'),
(13, 'auth', '0011_update_proxy_permissions', '2026-02-13 10:54:09.176303'),
(14, 'auth', '0012_alter_user_first_name_max_length', '2026-02-13 10:54:09.185149'),
(15, 'accounts', '0001_initial', '2026-02-13 10:54:09.430303'),
(16, 'admin', '0001_initial', '2026-02-13 10:54:09.527796'),
(17, 'admin', '0002_logentry_remove_auto_add', '2026-02-13 10:54:09.536272'),
(18, 'admin', '0003_logentry_add_action_flag_choices', '2026-02-13 10:54:09.545283'),
(19, 'sessions', '0001_initial', '2026-02-13 10:54:09.572390'),
(20, 'students', '0001_initial', '2026-02-13 10:54:09.660272'),
(21, 'tpo', '0001_initial', '2026-02-13 10:54:09.842476');

-- --------------------------------------------------------

--
-- Table structure for table `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('60o2x2366rhz5huudgg8rh16culyraj5', '.eJxVjMEOwiAQRP-FsyFAFwGP3v0GsuyCVA1NSnsy_rtt0oMeZ96beYuI61Lj2vMcRxYX4cTpt0tIz9x2wA9s90nS1JZ5THJX5EG7vE2cX9fD_Tuo2Ou2tkYphsCFirJh8CFZ5YJNgZItsEUgMoTZ4QCcbOYzGw3agyLvjNbi8wXkAjeq:1w7xaT:7YLkweuV9TBRw7E_617PHunysDL6FWuAhf02rW8m9e8', '2026-04-15 15:34:33.121567'),
('87eankps2uvqw2gafn0zb6nqg5xnezxu', '.eJxVjDsOwjAQBe_iGlkOwlkvJT1nsNbefSSAEimfCnF3iJQC2jcz7-WyrEuX19mm3Ks7u8Ydfrci9WHDBvQuw230dRyWqS9-U_xOZ38d1Z6X3f076GTuvrUJEcA1gYKCQ4OTIWlq2GJhFiGWVgzlGJBiAigKWAnSVtYC9_4AGzU5vw:1w7xIq:RFsGCRMiNKZMzyfIAMltSGB9i9XH-Qgam6GRNnS8l_8', '2026-04-15 15:16:20.593641'),
('axev4jegqcy831sb05r8aon1ehzyoi0d', '.eJxVjDsOwjAQBe_iGlkOwlkvJT1nsNbefSSAEimfCnF3iJQC2jcz7-WyrEuX19mm3Ks7u8Ydfrci9WHDBvQuw230dRyWqS9-U_xOZ38d1Z6X3f076GTuvrUJEcA1gYKCQ4OTIWlq2GJhFiGWVgzlGJBiAigKWAnSVtYC9_4AGzU5vw:1wBoW6:zX8PgSbB-jrXwY0xSonuvFhw1zqETfze1SfqJx41dIA', '2026-04-26 06:41:58.720397'),
('bv9li2k5iku47yas4cjud4pif5jhcffk', '.eJxVjMsOwiAUBf-FtSFSELgu3fsNhPtQqgaS0q6M_26bdKHbMzPnrVJe5pKWLlMaWZ0VqMPvhpmeUjfAj1zvTVOr8zSi3hS9066vjeV12d2_g5J7Wetg6HjzSMEjoqU4kEUBx8QYDURHDADCp-gCDIbAZ2vcGqDYAIBOfb4EwDha:1xHwZ0:-AMZNu0HwtsnQZBj1VkwG86iS_XeiqbHNxumyaco1I4', '2026-10-31 05:02:34.349154'),
('k14mqpgjkd36k97mdysuqmllexnua279', '.eJxVjEEOwiAQRe_C2pDSqTC4dN8zkBkYpGrapLQr492VpAvd_vfef6lA-1bCXmUNU1IXher0uzHFh8wNpDvNt0XHZd7WiXVT9EGrHpckz-vh_h0UquVbixVwjMb4JENH6NJge3JC0XaAEQDQEjM2DXv0kJxlQ_7MOZNAVu8P4vg4HA:1vyvZM:XuG7a7IZMg3ZaF2TI-0sFS_e3IH9hdlq_ec-pcSd4Jo', '2026-03-21 17:36:04.955776'),
('mrno9119ymupbq8qzo4q49nacj5ejxbv', '.eJxVjMsOwiAUBf-FtSFSELgu3fsNhPtQqgaS0q6M_26bdKHbMzPnrVJe5pKWLlMaWZ0VqMPvhpmeUjfAj1zvTVOr8zSi3hS9066vjeV12d2_g5J7Wetg6HjzSMEjoqU4kEUBx8QYDURHDADCp-gCDIbAZ2vcGqDYAIBOfb4EwDha:1w7xVG:vBALn1iYpXCP8wZ7O84bZvu1hINo-pcjM62Q3uXnQ94', '2026-04-15 15:29:10.723705'),
('tgeou4bxfmc1a6q77g6q6p36w5z47jj1', '.eJxVjDsOwjAQBe_iGlkOwlkvJT1nsNbefSSAEimfCnF3iJQC2jcz7-WyrEuX19mm3Ks7u8Ydfrci9WHDBvQuw230dRyWqS9-U_xOZ38d1Z6X3f076GTuvrUJEcA1gYKCQ4OTIWlq2GJhFiGWVgzlGJBiAigKWAnSVtYC9_4AGzU5vw:1vrLP6:zaDcIHShQHWV1Cn-HvNrfl_kpjXoCnOpdcfb5GhhcqY', '2026-02-28 19:34:08.515135'),
('wwh4hmaivhgtq00iljvhu4zrisiv9pbw', '.eJxVjDkOAjEQBP_iGFm-D0LyfcNqPB7jBWRLe0SIvyNLG0DaVdVvNsOx1_nYaJ2XzK5MscvvlgCf1AbID2j3zrG3fV0SHwo_6cannul1O92_gwpbHbXNGKORZEgonQVaF6IIQRqyoZjotCWImEPxxnsXoACKJDQlqQAJ2ecL1ns4FA:1vqris:cbqoKHxH1RsKLwbMgtj8HFZFECc1HATamTSokJooOEY', '2026-02-27 11:52:34.312999');

-- --------------------------------------------------------

--
-- Table structure for table `students_student`
--

CREATE TABLE `students_student` (
  `id` bigint(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `roll_no` varchar(20) NOT NULL,
  `email` varchar(254) NOT NULL,
  `branch` varchar(10) NOT NULL,
  `cgpa` decimal(4,2) NOT NULL,
  `skills` longtext NOT NULL,
  `resume` varchar(100) DEFAULT NULL,
  `placement_status` varchar(15) NOT NULL,
  `company_name` varchar(100) DEFAULT NULL,
  `package` decimal(6,2) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `students_student`
--

INSERT INTO `students_student` (`id`, `name`, `roll_no`, `email`, `branch`, `cgpa`, `skills`, `resume`, `placement_status`, `company_name`, `package`, `created_at`, `updated_at`, `user_id`) VALUES
(1, 'John Doe', '2021001', 'student1@example.com', 'CSE', 8.50, 'Python, Java, Machine Learning, Web Development', 'resumes/2021001_resume.pdf', 'not_placed', 'Tech Corp', 12.50, '2026-02-13 10:54:18.709976', '2026-02-13 12:05:44.772030', 2),
(2, 'Jane Smith', '2021002', 'student2@example.com', 'ECE', 9.20, 'VLSI, Embedded Systems, C++, Python', '', 'placed', 'Electronics Inc', 15.00, '2026-02-13 10:54:18.860630', '2026-02-13 10:54:18.860630', 3),
(3, 'Mike Johnson', '2021003', 'student3@example.com', 'ME', 7.80, 'AutoCAD, SolidWorks, Manufacturing, CAD', 'resumes/2021003_resume.pdf', 'placed', 'wegdvdv', 23.00, '2026-02-13 10:54:18.988863', '2026-03-10 14:55:17.334623', 4),
(4, 'Sarah Wilson', '2021004', 'student4@example.com', 'CSE', 8.90, 'JavaScript, React, Node.js, MongoDB', '', 'not_placed', '', NULL, '2026-02-13 10:54:19.111929', '2026-02-13 10:54:19.111929', 5),
(5, 'David Brown', '2021005', 'student5@example.com', 'IT', 8.10, 'Data Science, SQL, Python, Tableau', '', 'placed', 'Data Analytics Ltd', 14.00, '2026-02-13 10:54:19.264765', '2026-02-13 10:54:19.264765', 6),
(6, 'Perampalli Navidul Hasan Liyaquat Ali', '226222014', 'navid@gmail.com', 'CSE', 6.70, 'Python , Java , Html , C , CSS , Javascript', 'resumes/226222014_resume.pdf', 'not_placed', NULL, NULL, '2026-03-06 15:45:10.300951', '2026-03-06 15:46:01.385098', 7),
(7, 'Misbah Shaikh', 'CSE20', 'misbahshaikh1425@gmail.com', 'CSE', 8.64, 'Python', '', 'not_placed', NULL, NULL, '2026-03-07 17:35:37.200017', '2026-03-07 17:35:37.200017', 8),
(8, 'ABCD', '4252', 'abcd@gmail.com', 'CSE', 7.00, 'Python , SOC , Ethical Hacking , Java , Web Dev', 'resumes/4252_resume.pdf', 'not_placed', NULL, NULL, '2026-04-01 15:27:00.232188', '2026-04-01 15:35:08.836751', 9);

-- --------------------------------------------------------

--
-- Table structure for table `tpo_application`
--

CREATE TABLE `tpo_application` (
  `id` bigint(20) NOT NULL,
  `applied_at` datetime(6) NOT NULL,
  `status` varchar(15) NOT NULL,
  `drive_id` bigint(20) NOT NULL,
  `student_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tpo_application`
--

INSERT INTO `tpo_application` (`id`, `applied_at`, `status`, `drive_id`, `student_id`) VALUES
(1, '2026-02-13 11:53:21.888456', 'shortlisted', 1, 1),
(2, '2026-03-06 15:46:16.604533', 'offered', 1, 6),
(3, '2026-03-10 14:55:42.784926', 'rejected', 1, 3),
(4, '2026-03-14 14:36:26.799426', 'offered', 2, 6),
(5, '2026-03-14 14:39:57.865667', 'rejected', 2, 3),
(6, '2026-04-01 15:35:32.061008', 'offered', 3, 8),
(7, '2026-04-01 15:40:54.387088', 'rejected', 2, 8),
(8, '2026-04-01 15:41:00.524181', 'shortlisted', 1, 8),
(9, '2026-05-05 06:34:45.441153', 'applied', 3, 6);

-- --------------------------------------------------------

--
-- Table structure for table `tpo_drive`
--

CREATE TABLE `tpo_drive` (
  `id` bigint(20) NOT NULL,
  `company_name` varchar(100) NOT NULL,
  `role` varchar(100) NOT NULL,
  `package` decimal(6,2) NOT NULL,
  `description` longtext DEFAULT NULL,
  `min_cgpa` decimal(4,2) NOT NULL,
  `allowed_branches` varchar(200) NOT NULL,
  `backlogs_criteria` varchar(20) NOT NULL,
  `deadline` date DEFAULT NULL,
  `status` varchar(15) NOT NULL,
  `created_at` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tpo_drive`
--

INSERT INTO `tpo_drive` (`id`, `company_name`, `role`, `package`, `description`, `min_cgpa`, `allowed_branches`, `backlogs_criteria`, `deadline`, `status`, `created_at`) VALUES
(1, 'Intellise', 'SWE , QA', 4.20, 'Nothing', 6.00, 'CSE, ECE, IT ,AI&DS', 'no_active', '2026-02-20', 'active', '2026-02-13 11:51:37.600109'),
(2, 'Two Elephants', 'SOC -1', 5.50, 'SOC analyst who is skilled in reading logs and vulnerability managment', 6.50, 'CSE , IT', 'no_history', '2026-03-15', 'active', '2026-03-14 14:35:09.153915'),
(3, 'LIC', 'SWE', 9.00, '', 0.00, '', 'any', '2026-04-03', 'active', '2026-04-01 15:05:03.968109');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `accounts_user`
--
ALTER TABLE `accounts_user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `accounts_user_groups`
--
ALTER TABLE `accounts_user_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `accounts_user_groups_user_id_group_id_59c0b32f_uniq` (`user_id`,`group_id`),
  ADD KEY `accounts_user_groups_group_id_bd11a704_fk_auth_group_id` (`group_id`);

--
-- Indexes for table `accounts_user_user_permissions`
--
ALTER TABLE `accounts_user_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `accounts_user_user_permi_user_id_permission_id_2ab516c2_uniq` (`user_id`,`permission_id`),
  ADD KEY `accounts_user_user_p_permission_id_113bb443_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Indexes for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_accounts_user_id` (`user_id`);

--
-- Indexes for table `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- Indexes for table `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- Indexes for table `students_student`
--
ALTER TABLE `students_student`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `roll_no` (`roll_no`),
  ADD UNIQUE KEY `user_id` (`user_id`);

--
-- Indexes for table `tpo_application`
--
ALTER TABLE `tpo_application`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `tpo_application_drive_id_student_id_7da63a09_uniq` (`drive_id`,`student_id`),
  ADD KEY `tpo_application_student_id_0a4f00a6_fk_students_student_id` (`student_id`);

--
-- Indexes for table `tpo_drive`
--
ALTER TABLE `tpo_drive`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `accounts_user`
--
ALTER TABLE `accounts_user`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `accounts_user_groups`
--
ALTER TABLE `accounts_user_groups`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `accounts_user_user_permissions`
--
ALTER TABLE `accounts_user_user_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;

--
-- AUTO_INCREMENT for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=22;

--
-- AUTO_INCREMENT for table `students_student`
--
ALTER TABLE `students_student`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `tpo_application`
--
ALTER TABLE `tpo_application`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `tpo_drive`
--
ALTER TABLE `tpo_drive`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `accounts_user_groups`
--
ALTER TABLE `accounts_user_groups`
  ADD CONSTRAINT `accounts_user_groups_group_id_bd11a704_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  ADD CONSTRAINT `accounts_user_groups_user_id_52b62117_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`);

--
-- Constraints for table `accounts_user_user_permissions`
--
ALTER TABLE `accounts_user_user_permissions`
  ADD CONSTRAINT `accounts_user_user_p_permission_id_113bb443_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `accounts_user_user_p_user_id_e4f0a161_fk_accounts_` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`);

--
-- Constraints for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Constraints for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Constraints for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`);

--
-- Constraints for table `students_student`
--
ALTER TABLE `students_student`
  ADD CONSTRAINT `students_student_user_id_56286dbb_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`);

--
-- Constraints for table `tpo_application`
--
ALTER TABLE `tpo_application`
  ADD CONSTRAINT `tpo_application_drive_id_f3ae7678_fk_tpo_drive_id` FOREIGN KEY (`drive_id`) REFERENCES `tpo_drive` (`id`),
  ADD CONSTRAINT `tpo_application_student_id_0a4f00a6_fk_students_student_id` FOREIGN KEY (`student_id`) REFERENCES `students_student` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
