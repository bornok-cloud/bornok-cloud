CREATE DATABASE IF NOT EXISTS `ondajob` 
  CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

USE `ondajob`;

CREATE TABLE IF NOT EXISTS `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `first_name` VARCHAR(100) NOT NULL,
  `middle_name` VARCHAR(100),
  `last_name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(255) NOT NULL UNIQUE,
  `phone` VARCHAR(20),
  `password_hash` VARCHAR(255) NOT NULL,
  `role` ENUM('jobseeker','employer','admin') DEFAULT 'jobseeker',
  `avatar_initials` VARCHAR(5),
  `is_active` BOOLEAN DEFAULT TRUE,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX `idx_email` (`email`),
  INDEX `idx_role` (`role`)
) ENGINE=InnoDB;

-- Profiles (Job Seeker)
CREATE TABLE IF NOT EXISTS `profiles` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL UNIQUE,
  `title` VARCHAR(200),
  `summary` TEXT,
  `location` VARCHAR(200),
  `linkedin_url` VARCHAR(500),
  `portfolio_url` VARCHAR(500),
  `resume_score` INT DEFAULT 0,
  `skills` TEXT,
  `experience_years` INT DEFAULT 0,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Experiences
CREATE TABLE IF NOT EXISTS `experiences` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `profile_id` INT NOT NULL,
  `job_title` VARCHAR(200) NOT NULL,
  `company` VARCHAR(200) NOT NULL,
  `start_date` VARCHAR(50),
  `end_date` VARCHAR(50) DEFAULT 'Present',
  `description` TEXT,
  FOREIGN KEY (`profile_id`) REFERENCES `profiles`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Educations
CREATE TABLE IF NOT EXISTS `educations` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `profile_id` INT NOT NULL,
  `degree` VARCHAR(200) NOT NULL,
  `school` VARCHAR(200) NOT NULL,
  `start_year` VARCHAR(10),
  `end_year` VARCHAR(10),
  FOREIGN KEY (`profile_id`) REFERENCES `profiles`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Companies (Employer)
CREATE TABLE IF NOT EXISTS `companies` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL UNIQUE,
  `name` VARCHAR(200) NOT NULL,
  `description` TEXT,
  `industry` VARCHAR(100),
  `location` VARCHAR(200),
  `website` VARCHAR(500),
  `employee_count` VARCHAR(50),
  `logo_emoji` VARCHAR(10) DEFAULT '🏢',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Jobs
CREATE TABLE IF NOT EXISTS `jobs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `employer_id` INT NOT NULL,
  `company_id` INT,
  `title` VARCHAR(200) NOT NULL,
  `description` TEXT,
  `location` VARCHAR(200),
  `job_type` ENUM('full-time','part-time') DEFAULT 'full-time',
  `work_setup` ENUM('remote','on-site','hybrid') DEFAULT 'on-site',
  `experience_level` ENUM('entry','mid','senior','lead','manager','director') DEFAULT 'mid',
  `salary_min` INT,
  `salary_max` INT,
  `currency` VARCHAR(5) DEFAULT 'PHP',
  `skills_required` TEXT,
  `industry` VARCHAR(100),
  `is_featured` BOOLEAN DEFAULT FALSE,
  `is_urgent` BOOLEAN DEFAULT FALSE,
  `status` ENUM('active','paused','closed') DEFAULT 'active',
  `views_count` INT DEFAULT 0,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`employer_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`) ON DELETE SET NULL,
  INDEX `idx_status` (`status`),
  INDEX `idx_job_type` (`job_type`),
  INDEX `idx_work_setup` (`work_setup`)
) ENGINE=InnoDB;

-- Applications
CREATE TABLE IF NOT EXISTS `applications` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `job_id` INT NOT NULL,
  `status` ENUM('applied','reviewing','interview','offered','rejected') DEFAULT 'applied',
  `cover_letter` TEXT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`job_id`) REFERENCES `jobs`(`id`) ON DELETE CASCADE,
  UNIQUE KEY `unique_application` (`user_id`, `job_id`)
) ENGINE=InnoDB;

-- Saved Jobs
CREATE TABLE IF NOT EXISTS `saved_jobs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `job_id` INT NOT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`job_id`) REFERENCES `jobs`(`id`) ON DELETE CASCADE,
  UNIQUE KEY `unique_save` (`user_id`, `job_id`)
) ENGINE=InnoDB;

-- Messages
CREATE TABLE IF NOT EXISTS `messages` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `sender_id` INT NOT NULL,
  `receiver_id` INT NOT NULL,
  `content` TEXT NOT NULL,
  `is_read` BOOLEAN DEFAULT FALSE,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`sender_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`receiver_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_sender` (`sender_id`),
  INDEX `idx_receiver` (`receiver_id`)
) ENGINE=InnoDB;

-- Notifications
CREATE TABLE IF NOT EXISTS `notifications` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `title` VARCHAR(200),
  `message` TEXT,
  `is_read` BOOLEAN DEFAULT FALSE,
  `notification_type` VARCHAR(50),
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Reports
CREATE TABLE IF NOT EXISTS `reports` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `reporter_id` INT NOT NULL,
  `job_id` INT,
  `user_id` INT,
  `reason` ENUM('spam','misleading','scam','inappropriate','other') NOT NULL,
  `description` TEXT,
  `status` ENUM('pending','reviewed','resolved') DEFAULT 'pending',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`reporter_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`job_id`) REFERENCES `jobs`(`id`) ON DELETE SET NULL,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB;
