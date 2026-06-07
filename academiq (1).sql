-- phpMyAdmin SQL Dump
-- version 5.1.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:8889
-- Generation Time: Apr 28, 2026 (updated)
-- Server version: 5.7.24
-- PHP Version: 8.3.1
--
-- This dump matches the original schema PLUS the advisor / chat
-- tables added during the AcademiQ project (advisors, advisors_login,
-- advisor_assignments, advisor_messages).

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `academiq`
--

-- --------------------------------------------------------

--
-- Table structure for table `courses`
--

CREATE TABLE `courses` (
  `code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `course_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `hours` int(11) NOT NULL DEFAULT '3'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `courses`
--

INSERT INTO `courses` (`code`, `course_name`, `hours`) VALUES
('AINT115', 'Introduction to AI', 2),
('CECS484', 'Machine Learning', 3),
('CENG123', 'Digital Logic', 4),
('CRCL115', 'University Life Skills', 3),
('CSCE102', 'Computer Programming', 4),
('CSCE121', 'Discrete Structures', 3),
('CSCE351', 'Databases Systems', 4),
('CSCE352', 'Operating Systems', 4),
('CSCE353', 'Computer Networks', 4),
('CSCE354', 'Compiler Design', 3),
('CSCE361', 'Artificial Intelligence', 3),
('CSCE362', 'Web Development', 4),
('CSCE363', 'Fundamental of Security', 3),
('CSCE364', 'Computer Graphics', 3),
('CSCE480', 'Graduation Project', 4),
('CSCE482', 'Cloud Computing', 3),
('CSCE487', 'High Performance Computing', 3),
('CSCE490', 'Special Topic', 3),
('MATH103', 'Calculus', 4),
('MGT212', 'Legal Environment', 3);

-- --------------------------------------------------------

--
-- Table structure for table `registration`
--

CREATE TABLE `registration` (
  `student_id` int(11) NOT NULL,
  `crn` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `registration`
--

INSERT INTO `registration` (`student_id`, `crn`) VALUES
(20243341, 1265),
(20248596, 1265),
(20241190, 1317),
(20247854, 1317),
(20240018, 1562),
(20249012, 1562),
(20241190, 2651),
(20247854, 2651),
(20241155, 3085),
(20247734, 3085),
(20241155, 3465),
(20241190, 3465),
(20247734, 3465),
(20247854, 3465),
(20249012, 3465),
(20243647, 3476),
(20245562, 3476),
(20243647, 4218),
(20245562, 4218),
(20243341, 4510),
(20248596, 4510),
(20241155, 4916),
(20247734, 4916),
(20240018, 7201),
(20240018, 7311),
(20249012, 7311),
(20243647, 8124),
(20245562, 8124),
(20241190, 8642),
(20247854, 8642),
(20249012, 6743),
(20240018, 9471),
(20243341, 9471),
(20243647, 9471),
(20245562, 9471),
(20248596, 9471),
(20243341, 9520),
(20248596, 9520);

-- --------------------------------------------------------

--
-- Table structure for table `sections`
--

CREATE TABLE `sections` (
  `ref_number` int(11) NOT NULL,
  `code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `instructor` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `total_students` int(11) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `sections`
--

INSERT INTO `sections` (`ref_number`, `code`, `instructor`, `type`, `total_students`) VALUES
(1265, 'CSCE364', 'Hind', 'LEC', 15),
(1317, 'CSCE362', 'Rawan', 'LEC', 15),
(1474, 'MATH103', 'Abrar', 'LEC', 15),
(1507, 'CSCE487', 'Alhanouf', 'LEC', 20),
(1562, 'CSCE480', 'Sara alfhiz', 'LEC', 30),
(1798, 'CSCE121', 'Salma', 'LEC', 25),
(2078, 'AINT115', 'Reem', 'LEC', 40),
(2378, 'AINT115', 'Rawan', 'LEC', 35),
(2468, 'CSCE480', 'Reem', 'LEC', 33),
(2651, 'MGT212', 'Afaf', 'LEC', 30),
(3026, 'MATH103', 'Abrar', 'LEC', 20),
(3085, 'MGT212', 'Afaf', 'LEC', 35),
(3465, 'CSCE102', 'Hadeel', 'LEC', 25),
(3476, 'CSCE364', 'Abeer', 'LEC', 20),
(3804, 'CRCL115', 'Moudi', 'LEC', 25),
(4140, 'CSCE352', 'Amal', 'LEC', 40),
(4207, 'CENG123', 'Noha', 'LEC', 30),
(4218, 'CSCE361', 'Afrah', 'LEC', 25),
(4510, 'CSCE487', 'Alhanouf', 'LAB', 35),
(4565, 'CSCE362', 'Albandari Meshal', 'LEC', 28),
(4675, 'CRCL115', 'Moudi', 'LEC', 40),
(4916, 'CECS484', 'Albandari Meshal', 'LEC', 25),
(5012, 'CSCE353', 'Afrah', 'LEC', 35),
(5427, 'CRCL115', 'Sara alfhiz', 'LEC', 30),
(5654, 'CSCE480', 'Sara alfhiz', 'LEC', 18),
(5803, 'CSCE361', 'Hadeel', 'LEC', 28),
(6194, 'CSCE361', 'Hadeel', 'LEC', 33),
(6301, 'CSCE121', 'Manal', 'LEC', 40),
(6520, 'CSCE121', 'Manal', 'LEC', 25),
(6743, 'MGT212', 'Hind', 'LEC', 19),
(7139, 'AINT115', 'Afaf', 'LEC', 30),
(7201, 'CSCE353', 'Afrah', 'LEC', 30),
(7311, 'CECS484', 'Noha', 'LEC', 30),
(7430, 'CENG123', 'Noha', 'LEC', 20),
(8012, 'CSCE102', 'Noha', 'LEC', 35),
(8109, 'MATH103', 'Abrar', 'LEC', 30),
(8124, 'CECS484', 'Abrar', 'LEC', 40),
(8260, 'CSCE353', 'Afaf', 'LEC', 20),
(8264, 'CSCE364', 'Hind', 'LEC', 23),
(8510, 'CSCE352', 'Amal', 'LEC', 25),
(8642, 'CSCE362', 'Moudi', 'LAB', 40),
(9103, 'CSCE352', 'Amal', 'LEC', 25),
(9227, 'CENG123', 'Rawan', 'LEC', 35),
(9471, 'CSCE102', 'Noha', 'LEC', 34),
(9520, 'CSCE487', 'Alhanouf', 'LEC', 30);

-- --------------------------------------------------------

--
-- Table structure for table `students`
--

CREATE TABLE `students` (
  `id` int(11) NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `specialistion` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `level` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `students`
--

INSERT INTO `students` (`id`, `name`, `specialistion`, `level`) VALUES
(20240018, 'Maryam Ahmed', 'Computer Science', '2'),
(20241155, 'Abrar Khaled', 'Computer Science', '2'),
(20241190, 'Fatimah Omar', 'Computer Science', '2'),
(20243341, 'Mona Saeed', 'Computer Science', '2'),
(20243647, 'Lama Salah', 'Computer Science', '2'),
(20245562, 'Reem Khalid', 'Computer Science', '2'),
(20247734, 'Noura Salem', 'Computer Science', '2'),
(20247854, 'Rima Mohammed', 'Computer Science', '2'),
(20248596, 'Amal Hamed', 'Computer Science', '2'),
(20249012, 'Samia Ali', 'Computer Science', '2');

-- --------------------------------------------------------

--
-- Table structure for table `students_login`
--

CREATE TABLE `students_login` (
  `username` int(11) NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `students_login`
--

INSERT INTO `students_login` (`username`, `password`) VALUES
(20240018, 'Ma9876am'),
(20241155, 'Ab6548kh'),
(20241190, 'Fa3512om'),
(20243341, 'Mo0943sa'),
(20243647, 'La1598sa'),
(20245562, 'Re9536kh'),
(20247734, 'No2584sa'),
(20247854, 'Ri3574mo'),
(20248596, 'Am2465hm'),
(20249012, 'Sa9012al');

-- --------------------------------------------------------

--
-- Table structure for table `time_slots`
--

CREATE TABLE `time_slots` (
  `id` int(11) NOT NULL,
  `ref_number` int(11) NOT NULL,
  `days` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  `location` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `max_capacity` int(11) NOT NULL DEFAULT '30'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `time_slots`
--

INSERT INTO `time_slots` (`id`, `ref_number`, `days`, `start_time`, `end_time`, `location`, `max_capacity`) VALUES
(1, 1562, 'S', '08:00:00', '09:50:00', '11A|201', 30),
(2, 2468, 'M', '10:00:00', '11:50:00', '11A|202', 35),
(3, 5654, 'T', '12:00:00', '13:50:00', '11A|203', 20),
(4, 7311, 'W', '08:00:00', '09:50:00', '11B|101', 30),
(5, 8124, 'R', '10:00:00', '11:50:00', '11B|102', 40),
(6, 4916, 'S', '12:00:00', '13:50:00', '11B|103', 25),
(7, 3085, 'M', '08:00:00', '09:50:00', '11B|201', 35),
(8, 6743, 'T', '10:00:00', '11:50:00', '11B|202', 20),
(9, 2651, 'W', '12:00:00', '13:50:00', '11B|203', 30),
(10, 8642, 'R', '08:00:00', '09:50:00', 'CL1|101', 40),
(11, 4565, 'S', '10:00:00', '11:50:00', '11C|101', 30),
(12, 1317, 'M', '12:00:00', '13:50:00', '11C|102', 15),
(13, 4218, 'T', '08:00:00', '09:50:00', '11C|201', 25),
(14, 6194, 'W', '10:00:00', '11:50:00', '11C|202', 35),
(15, 5803, 'R', '12:00:00', '13:50:00', '11C|203', 30),
(16, 3476, 'S', '08:00:00', '09:50:00', '11C|301', 20),
(17, 1265, 'M', '10:00:00', '11:50:00', '11C|302', 15),
(18, 8264, 'T', '12:00:00', '13:50:00', '11C|303', 25),
(19, 4510, 'W', '08:00:00', '09:50:00', 'CL1|201', 35),
(20, 9520, 'R', '10:00:00', '11:50:00', '11D|101', 30),
(21, 1507, 'S', '12:00:00', '13:50:00', '11D|102', 20),
(22, 7139, 'M', '08:00:00', '09:50:00', '11D|201', 30),
(23, 2378, 'T', '10:00:00', '11:50:00', '11D|202', 35),
(24, 2078, 'W', '12:00:00', '13:50:00', '11D|203', 40),
(25, 3026, 'R', '08:00:00', '09:50:00', '17A|101', 20),
(26, 8109, 'S', '10:00:00', '11:50:00', '17A|102', 30),
(27, 1474, 'M', '12:00:00', '13:50:00', '17A|103', 15),
(28, 3804, 'T', '08:00:00', '09:50:00', '11D|104', 25),
(29, 4675, 'W', '10:00:00', '11:50:00', '11D|104', 40),
(30, 5427, 'T', '11:00:00', '11:50:00', '11D|105', 30),
(31, 8012, 'R', '09:00:00', '10:50:00', '11D|104', 40),
(32, 9471, 'S', '13:00:00', '13:50:00', '11D|103', 35),
(33, 3465, 'M', '10:00:00', '11:50:00', '11D|102', 25),
(34, 6520, 'S', '08:00:00', '09:50:00', 'CL2|303', 30),
(35, 6301, 'W', '12:00:00', '13:50:00', 'CL2|302', 45),
(36, 1798, 'R', '14:00:00', '14:50:00', 'CL2|309', 30),
(37, 4207, 'T', '11:00:00', '12:50:00', '17D|103', 35),
(38, 9227, 'S', '09:00:00', '10:50:00', '17D|104', 40),
(39, 7430, 'M', '13:00:00', '13:50:00', '17D|302', 25),
(40, 8510, 'S', '10:00:00', '11:50:00', '17D|308', 30),
(41, 4140, 'W', '08:00:00', '09:50:00', '17D|305', 45),
(42, 9103, 'R', '10:00:00', '11:50:00', '17C|205', 30),
(43, 8260, 'T', '12:00:00', '12:50:00', '17C|209', 25),
(44, 7201, 'M', '13:00:00', '13:50:00', '17C|306', 35),
(45, 5012, 'S', '08:00:00', '09:50:00', '17C|301', 40);

-- --------------------------------------------------------

--
-- Table structure for table `advisors`
-- (NEW — academic advisors who can log in and chat with assigned students)
--

CREATE TABLE `advisors` (
  `id` int(11) NOT NULL,
  `name` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `department` varchar(80) COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `advisors`
--

INSERT INTO `advisors` (`id`, `name`, `department`) VALUES
(1001, 'Dr. Sara Al-Otaibi', 'Computer Science'),
(1002, 'Dr. Nora Al-Ghamdi', 'Information Technology');

-- --------------------------------------------------------

--
-- Table structure for table `advisors_login`
-- (NEW — credentials for advisor login)
--

CREATE TABLE `advisors_login` (
  `advisor_id` int(11) NOT NULL,
  `password` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `advisors_login`
--

INSERT INTO `advisors_login` (`advisor_id`, `password`) VALUES
(1001, 'Sara@1001'),
(1002, 'Nora@1002');

-- --------------------------------------------------------

--
-- Table structure for table `advisor_assignments`
-- (NEW — many-to-many mapping between advisors and the students they advise)
--

CREATE TABLE `advisor_assignments` (
  `advisor_id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `advisor_assignments`
--

INSERT INTO `advisor_assignments` (`advisor_id`, `student_id`) VALUES
(1001, 20240018),
(1001, 20241155),
(1001, 20247854),
(1002, 20243647),
(1002, 20247734),
(1002, 20249012);

-- --------------------------------------------------------

--
-- Table structure for table `advisor_messages`
-- (NEW — chat messages between students and advisors;
--  optional action_type/action_crn for embedded course requests)
--

CREATE TABLE `advisor_messages` (
  `id` int(11) NOT NULL,
  `advisor_id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `sender_role` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sender_name` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `body` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_type` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `action_crn` int(11) DEFAULT NULL,
  `handled` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `chk_msg_sender_role`
    CHECK (`sender_role` IN ('advisor','student')),
  CONSTRAINT `chk_msg_action_type`
    CHECK (`action_type` IS NULL OR `action_type` IN ('add','drop'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `advisor_messages`
--

INSERT INTO `advisor_messages` (`id`, `advisor_id`, `student_id`, `sender_role`, `sender_name`, `body`, `action_type`, `action_crn`, `handled`, `created_at`) VALUES
(1, 1001, 20240018, 'student', 'Maryam Ahmed',       'هلا',                    NULL, NULL, 0, '2026-04-28 01:07:24'),
(2, 1001, 20241155, 'advisor', 'Dr. Sara Al-Otaibi', 'هلا',                    NULL, NULL, 0, '2026-04-28 01:09:36'),
(3, 1001, 20240018, 'student', 'Maryam Ahmed',       'FAB test message hello', NULL, NULL, 0, '2026-04-28 01:49:25');

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
-- (NEW — notifications for students and advisors on course actions)
--

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `recipient_type` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `recipient_id` int(11) NOT NULL,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `body` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `notif_type` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'info',
  `is_read` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `chk_notif_recipient`
    CHECK (`recipient_type` IN ('student','advisor'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `courses`
--
ALTER TABLE `courses`
  ADD PRIMARY KEY (`code`);

--
-- Indexes for table `registration`
--
ALTER TABLE `registration`
  ADD PRIMARY KEY (`student_id`,`crn`),
  ADD KEY `fk_reg_section` (`crn`);

--
-- Indexes for table `sections`
--
ALTER TABLE `sections`
  ADD PRIMARY KEY (`ref_number`),
  ADD KEY `fk_section_course` (`code`);

--
-- Indexes for table `students`
--
ALTER TABLE `students`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `students_login`
--
ALTER TABLE `students_login`
  ADD PRIMARY KEY (`username`);

--
-- Indexes for table `time_slots`
--
ALTER TABLE `time_slots`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_timeslot_section` (`ref_number`);

--
-- Indexes for table `advisors` (NEW)
--
ALTER TABLE `advisors`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `advisors_login` (NEW)
--
ALTER TABLE `advisors_login`
  ADD PRIMARY KEY (`advisor_id`);

--
-- Indexes for table `advisor_assignments` (NEW)
--
ALTER TABLE `advisor_assignments`
  ADD PRIMARY KEY (`advisor_id`,`student_id`),
  ADD KEY `fk_assign_student` (`student_id`);

--
-- Indexes for table `advisor_messages` (NEW)
--
ALTER TABLE `advisor_messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_msg_advisor` (`advisor_id`),
  ADD KEY `fk_msg_student` (`student_id`),
  ADD KEY `idx_msg_pair_time` (`advisor_id`,`student_id`,`created_at`);

--
-- Indexes for table `notifications` (NEW)
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_notif_recipient` (`recipient_type`,`recipient_id`,`is_read`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `sections`
--
ALTER TABLE `sections`
  MODIFY `ref_number` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9521;

--
-- AUTO_INCREMENT for table `time_slots`
--
ALTER TABLE `time_slots`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=46;

--
-- AUTO_INCREMENT for table `advisor_messages` (NEW)
--
ALTER TABLE `advisor_messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `notifications` (NEW)
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `registration`
--
ALTER TABLE `registration`
  ADD CONSTRAINT `fk_reg_section` FOREIGN KEY (`crn`) REFERENCES `sections` (`ref_number`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_reg_student` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `sections`
--
ALTER TABLE `sections`
  ADD CONSTRAINT `fk_section_course` FOREIGN KEY (`code`) REFERENCES `courses` (`code`) ON UPDATE CASCADE;

--
-- Constraints for table `students_login`
--
ALTER TABLE `students_login`
  ADD CONSTRAINT `fk_login_student` FOREIGN KEY (`username`) REFERENCES `students` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `time_slots`
--
ALTER TABLE `time_slots`
  ADD CONSTRAINT `fk_timeslot_section` FOREIGN KEY (`ref_number`) REFERENCES `sections` (`ref_number`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `advisors_login` (NEW)
--
ALTER TABLE `advisors_login`
  ADD CONSTRAINT `fk_advlogin_advisor` FOREIGN KEY (`advisor_id`) REFERENCES `advisors` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `advisor_assignments` (NEW)
--
ALTER TABLE `advisor_assignments`
  ADD CONSTRAINT `fk_assign_advisor` FOREIGN KEY (`advisor_id`) REFERENCES `advisors` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_assign_student` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `advisor_messages` (NEW)
--
ALTER TABLE `advisor_messages`
  ADD CONSTRAINT `fk_msg_advisor` FOREIGN KEY (`advisor_id`) REFERENCES `advisors` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_msg_student` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
