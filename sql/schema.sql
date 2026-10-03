CREATE DATABASE IF NOT EXISTS pathnotes;
USE pathnotes;

CREATE TABLE IF NOT EXISTS profile_analyses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(120) NOT NULL,
    primary_role VARCHAR(120) NOT NULL,
    readiness DECIMAL(5,2) NOT NULL,
    cluster_label VARCHAR(80),
    anomaly BOOLEAN DEFAULT FALSE,
    created_at DATETIME NOT NULL
);
