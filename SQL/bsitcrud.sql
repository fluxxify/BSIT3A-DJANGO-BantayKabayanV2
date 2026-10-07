-- =========================================================
-- COMBINED SQL FILE
-- BantayKabayan + BSITCRUD Backup
-- =========================================================

-- =========================================================
-- DATABASE 1: BANTAYKABAYAN
-- =========================================================

DROP DATABASE IF EXISTS bantaykabayan;

CREATE DATABASE bantaykabayan
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE bantaykabayan;

-- =========================================================
-- ACCOUNTS
-- =========================================================

CREATE TABLE accounts_user (
    id BIGINT NOT NULL AUTO_INCREMENT,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME(6) NULL,
    is_superuser TINYINT(1) NOT NULL DEFAULT 0,
    username VARCHAR(150) NOT NULL,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) NOT NULL,
    is_staff TINYINT(1) NOT NULL DEFAULT 0,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    date_joined DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY accounts_user_username_unique (username),
    UNIQUE KEY accounts_user_email_unique (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- OFW PROFILE
-- =========================================================

CREATE TABLE ofw_ofwprofile (
    id BIGINT NOT NULL AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    ofw_id VARCHAR(50) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100) NULL,
    last_name VARCHAR(100) NOT NULL,
    sex VARCHAR(20) NULL,
    birth_date DATE NULL,
    contact_number VARCHAR(30) NULL,
    email VARCHAR(254) NULL,
    address TEXT NULL,
    country VARCHAR(100) NOT NULL,
    employer VARCHAR(200) NULL,
    occupation VARCHAR(150) NULL,
    contract_start DATE NULL,
    contract_end DATE NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Active',
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY ofw_ofwprofile_ofw_id_unique (ofw_id),
    KEY ofw_ofwprofile_user_id_idx (user_id),
    CONSTRAINT ofw_ofwprofile_user_fk
        FOREIGN KEY (user_id)
        REFERENCES accounts_user(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- WELFARE CHECK-IN
-- =========================================================

CREATE TABLE monitoring_welfarecheckin (
    id BIGINT NOT NULL AUTO_INCREMENT,
    ofw_id BIGINT NOT NULL,
    checkin_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Safe',
    location VARCHAR(255) NULL,
    remarks TEXT NULL,
    created_at DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    KEY monitoring_welfarecheckin_ofw_id_idx (ofw_id),
    CONSTRAINT monitoring_welfarecheckin_ofw_fk
        FOREIGN KEY (ofw_id)
        REFERENCES ofw_ofwprofile(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- MONITORING RECORD
-- =========================================================

CREATE TABLE monitoring_monitoringrecord (
    id BIGINT NOT NULL AUTO_INCREMENT,
    ofw_id BIGINT NOT NULL,
    monitoring_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL,
    notes TEXT NULL,
    monitored_by BIGINT NULL,
    created_at DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    KEY monitoring_monitoringrecord_ofw_id_idx (ofw_id),
    KEY monitoring_monitoringrecord_monitored_by_idx (monitored_by),
    CONSTRAINT monitoring_monitoringrecord_ofw_fk
        FOREIGN KEY (ofw_id)
        REFERENCES ofw_ofwprofile(id)
        ON DELETE CASCADE,
    CONSTRAINT monitoring_monitoringrecord_user_fk
        FOREIGN KEY (monitored_by)
        REFERENCES accounts_user(id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- CONCERN CASE
-- =========================================================

CREATE TABLE cases_concerncase (
    id BIGINT NOT NULL AUTO_INCREMENT,
    ofw_id BIGINT NOT NULL,
    case_number VARCHAR(50) NOT NULL,
    concern_type VARCHAR(100) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(30) NOT NULL DEFAULT 'Normal',
    status VARCHAR(50) NOT NULL DEFAULT 'Open',
    date_reported DATE NOT NULL,
    assigned_to BIGINT NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY cases_concerncase_case_number_unique (case_number),
    KEY cases_concerncase_ofw_id_idx (ofw_id),
    KEY cases_concerncase_assigned_to_idx (assigned_to),
    CONSTRAINT cases_concerncase_ofw_fk
        FOREIGN KEY (ofw_id)
        REFERENCES ofw_ofwprofile(id)
        ON DELETE CASCADE,
    CONSTRAINT cases_concerncase_assigned_to_fk
        FOREIGN KEY (assigned_to)
        REFERENCES accounts_user(id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- CASE ACTION
-- =========================================================

CREATE TABLE cases_caseaction (
    id BIGINT NOT NULL AUTO_INCREMENT,
    case_id BIGINT NOT NULL,
    action_taken TEXT NOT NULL,
    action_date DATE NOT NULL,
    performed_by BIGINT NULL,
    remarks TEXT NULL,
    created_at DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    KEY cases_caseaction_case_id_idx (case_id),
    KEY cases_caseaction_performed_by_idx (performed_by),
    CONSTRAINT cases_caseaction_case_fk
        FOREIGN KEY (case_id)
        REFERENCES cases_concerncase(id)
        ON DELETE CASCADE,
    CONSTRAINT cases_caseaction_user_fk
        FOREIGN KEY (performed_by)
        REFERENCES accounts_user(id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- SUPPORT RECORD
-- =========================================================

CREATE TABLE support_supportrecord (
    id BIGINT NOT NULL AUTO_INCREMENT,
    ofw_id BIGINT NOT NULL,
    support_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    support_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    provided_by BIGINT NULL,
    created_at DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    KEY support_supportrecord_ofw_id_idx (ofw_id),
    KEY support_supportrecord_provided_by_idx (provided_by),
    CONSTRAINT support_supportrecord_ofw_fk
        FOREIGN KEY (ofw_id)
        REFERENCES ofw_ofwprofile(id)
        ON DELETE CASCADE,
    CONSTRAINT support_supportrecord_user_fk
        FOREIGN KEY (provided_by)
        REFERENCES accounts_user(id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- REFERRAL
-- =========================================================

CREATE TABLE support_referral (
    id BIGINT NOT NULL AUTO_INCREMENT,
    ofw_id BIGINT NOT NULL,
    referral_type VARCHAR(100) NOT NULL,
    referred_to VARCHAR(255) NOT NULL,
    reason TEXT NOT NULL,
    referral_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    remarks TEXT NULL,
    created_at DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    KEY support_referral_ofw_id_idx (ofw_id),
    CONSTRAINT support_referral_ofw_fk
        FOREIGN KEY (ofw_id)
        REFERENCES ofw_ofwprofile(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- FOLLOW-UP
-- =========================================================

CREATE TABLE support_followup (
    id BIGINT NOT NULL AUTO_INCREMENT,
    ofw_id BIGINT NOT NULL,
    support_id BIGINT NULL,
    followup_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    notes TEXT NULL,
    created_by BIGINT NULL,
    created_at DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    KEY support_followup_ofw_id_idx (ofw_id),
    KEY support_followup_support_id_idx (support_id),
    KEY support_followup_created_by_idx (created_by),
    CONSTRAINT support_followup_ofw_fk
        FOREIGN KEY (ofw_id)
        REFERENCES ofw_ofwprofile(id)
        ON DELETE CASCADE,
    CONSTRAINT support_followup_support_fk
        FOREIGN KEY (support_id)
        REFERENCES support_supportrecord(id)
        ON DELETE SET NULL,
    CONSTRAINT support_followup_user_fk
        FOREIGN KEY (created_by)
        REFERENCES accounts_user(id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- NOTIFICATION
-- =========================================================

CREATE TABLE notifications_notification (
    id BIGINT NOT NULL AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL DEFAULT 'Info',
    is_read TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    KEY notifications_notification_user_id_idx (user_id),
    CONSTRAINT notifications_notification_user_fk
        FOREIGN KEY (user_id)
        REFERENCES accounts_user(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- AUDIT LOG
-- =========================================================

CREATE TABLE audit_auditlog (
    id BIGINT NOT NULL AUTO_INCREMENT,
    user_id BIGINT NULL,
    action VARCHAR(100) NOT NULL,
    model_name VARCHAR(100) NULL,
    object_id VARCHAR(100) NULL,
    description TEXT NULL,
    ip_address VARCHAR(45) NULL,
    created_at DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    KEY audit_auditlog_user_id_idx (user_id),
    CONSTRAINT audit_auditlog_user_fk
        FOREIGN KEY (user_id)
        REFERENCES accounts_user(id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- DATABASE 2: OLD BSITCRUD BACKUP
-- Kept separate so it will not interfere with BantayKabayan
-- =========================================================

DROP DATABASE IF EXISTS bsitcrud_backup;

CREATE DATABASE bsitcrud_backup
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE bsitcrud_backup;

-- =========================================================
-- AUTH GROUP
-- =========================================================

CREATE TABLE auth_group (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(150) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY auth_group_name_unique (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- AUTH PERMISSION
-- =========================================================

CREATE TABLE auth_permission (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    content_type_id INT NOT NULL,
    codename VARCHAR(100) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY auth_permission_content_type_codename_unique
        (content_type_id, codename)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- AUTH GROUP PERMISSIONS
-- =========================================================

CREATE TABLE auth_group_permissions (
    id BIGINT NOT NULL AUTO_INCREMENT,
    group_id INT NOT NULL,
    permission_id INT NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY auth_group_permissions_unique
        (group_id, permission_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- AUTH USER
-- =========================================================

CREATE TABLE auth_user (
    id INT NOT NULL AUTO_INCREMENT,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME(6) NULL,
    is_superuser TINYINT(1) NOT NULL,
    username VARCHAR(150) NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff TINYINT(1) NOT NULL,
    is_active TINYINT(1) NOT NULL,
    date_joined DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY auth_user_username_unique (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- AUTH USER GROUPS
-- =========================================================

CREATE TABLE auth_user_groups (
    id BIGINT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    group_id INT NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY auth_user_groups_unique
        (user_id, group_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- AUTH USER PERMISSIONS
-- =========================================================

CREATE TABLE auth_user_user_permissions (
    id BIGINT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    permission_id INT NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY auth_user_user_permissions_unique
        (user_id, permission_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- DJANGO CONTENT TYPE
-- =========================================================

CREATE TABLE django_content_type (
    id INT NOT NULL AUTO_INCREMENT,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY django_content_type_app_model_unique
        (app_label, model)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- DJANGO ADMIN LOG
-- =========================================================

CREATE TABLE django_admin_log (
    id INT NOT NULL AUTO_INCREMENT,
    action_time DATETIME(6) NOT NULL,
    object_id LONGTEXT NULL,
    object_repr VARCHAR(200) NOT NULL,
    action_flag SMALLINT UNSIGNED NOT NULL,
    change_message LONGTEXT NOT NULL,
    content_type_id INT NULL,
    user_id INT NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- DJANGO MIGRATIONS
-- =========================================================

CREATE TABLE django_migrations (
    id BIGINT NOT NULL AUTO_INCREMENT,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied DATETIME(6) NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- DJANGO SESSION
-- =========================================================

CREATE TABLE django_session (
    session_key VARCHAR(40) NOT NULL,
    session_data LONGTEXT NOT NULL,
    expire_date DATETIME(6) NOT NULL,
    PRIMARY KEY (session_key),
    KEY django_session_expire_date_idx (expire_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- OLD TBLINFO TABLE
-- =========================================================

CREATE TABLE tblinfo (
    id INT NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- END OF COMBINED SQL
-- =========================================================