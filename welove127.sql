---GROUP 4 | CMSC 127 ST1 - 4L
---BANASIHAN, MARIA ANGELA REGULACION
---CABATINGAN, JOANNE MARYZ PILAYRE
---DOROJA, KRISTINA BRILLO
---MILESTONE 3


-- MEMBER (Student number, First name, Middle name, Last name, Degree program, Gender, Batch)
-- ORGANIZATION (Organization name, Number of members, Members with unpaid fees)
-- FEE (Receipt Number, Amount, Payment deadline, Date paid, Payment status, Student number, Organization name)
-- MEMBER_SERVES_ORGANIZATION (Student number, Organization name, Academic year, Semester, Role, Status, Committee)

DROP DATABASE IF EXISTS `welove127`;
CREATE DATABASE IF NOT EXISTS `welove127`;
GRANT ALL PRIVILEGES ON welove127.* TO 'admin'@'%';
USE `welove127`;

CREATE TABLE IF NOT EXISTS member(
    student_no VARCHAR(10) PRIMARY KEY, 
    first_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50), 
    last_name VARCHAR(50) NOT NULL, 
    degree_program VARCHAR(50),
    gender VARCHAR(10),
    batch INT
);

CREATE TABLE IF NOT EXISTS organization(
    org_id VARCHAR(10) PRIMARY KEY, 
    org_name VARCHAR(50) UNIQUE NOT NULL, 
    no_of_members INT
);

CREATE TABLE IF NOT EXISTS fee(
    receipt_no VARCHAR(50) PRIMARY KEY,
    amount DECIMAL(10,2) NOT NULL, 
    payment_deadline DATE NOT NULL, 
    date_paid DATE, 
    payment_status VARCHAR(10) DEFAULT "Unpaid",
    student_no VARCHAR(10), 
    org_name VARCHAR(50),
    FOREIGN KEY (student_no) REFERENCES member(student_no) ON DELETE CASCADE,
    FOREIGN KEY (org_name) REFERENCES organization (org_name) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS serves(
    student_no VARCHAR(10),
    org_name VARCHAR(50),
    academic_year VARCHAR(10),
    semester VARCHAR(10),
    role VARCHAR(50),
    status VARCHAR(10),
    committee VARCHAR(50), 
    PRIMARY KEY(student_no, org_name),
    UNIQUE(academic_year, semester, role, status, committee),
    FOREIGN KEY(student_no) REFERENCES member(student_no) ON DELETE CASCADE,
    FOREIGN KEY (org_name) REFERENCES organization (org_name) ON DELETE CASCADE
);


-- Initial Org Members
-- Initial Members
INSERT INTO member (student_no, first_name, middle_name, last_name, degree_program, gender, batch) VALUES
('2023-00001', 'Gumball', NULL, 'Watterson', 'BS Computer Science', 'M', 2023),
('2023-00002', 'Anais', NULL, 'Watterson', 'BS Applied Mathematics', 'F', 2023),
('2023-00003', 'Darwin', NULL, 'Watterson', 'BS Biology', 'M', 2023),
('2023-00004', 'Nicole', NULL, 'Watterson', 'BS Chemistry', 'F', 2023),
('2023-00005', 'Richard', NULL, 'Watterson', 'BA Communication Arts', 'M', 2023);

-- Initial Organizations
INSERT INTO organization (org_id, org_name, no_of_members) VALUES
('0001', 'ACSS', 0),
('0002', 'YSES', 0),
('0003', 'COSS', 0),
('0004', 'DSG', 0);

---1. View all members of the organization by role, status, gender, degree program, batch (year of
---     membership), and committee. (Note: we assume one committee membership only per
---     organization per semester)

    SELECT
    m.student_no,
    m.first_name,
    m.middle_name,
    m.last_name,
    m.degree_program,
    m.gender,
    m.batch,
    s.role,
    s.status,
    s.committee
FROM member m
JOIN serves s
    ON m.student_no = s.student_no
WHERE s.org_name = "replace with org name";

---2. View members for a given organization with unpaid membership fees or dues for a given
---     semester and academic year.

    SELECT DISTINCT 
        m.student_no, 
        m.first_name, 
        m.middle_name, 
        m.last_name, 
        s.org_name 
    FROM member m 
    JOIN fee f 
        ON m.student_no = f.student_no 
    JOIN serves s
        ON m.student_no = s.student_no AND s.org_name = f.org_name
    WHERE f.payment_status = "Unpaid" OR f.date_paid IS NULL
        AND s.org_name = "replace with org_name" 
        AND s.academic_year = "acad year"
        AND s.semester = "replace with semester";

---3. View a member’s unpaid membership fees or dues for all their organizations (Member’s POV).

    SELECT f.org_name, f.receipt_no, f.amount, f.payment_deadline FROM fee f
    WHERE f.student_no = "2025-10506" 
        AND (f.date_paid IS NULL OR f.payment_status = "Unpaid")
    ORDER BY f.payment_deadline DESC;
    
---4. View all executive committee members of a given organization for a given academic year.
    SELECT 
        m.student_no, 
        m.first_name, 
        m.middle_name, 
        m.last_name, 
        s.role,
        s.status,
        s.committee 
    FROM member m 
    JOIN serves s
            ON m.student_no = s.student_no
    WHERE s.org_name = "org_name" 
        AND s.academic_year = "acad year"
        AND s.committee = "Executive"; 

---5. View all Presidents (or any other role) of a given organization for every academic year in
---     reverse chronological order (current to past).
    SELECT
        f.receipt_no, 
        f.amount,
        f.payment_deadline,
        f.date_paid,
        f.student_no,
        f.payment_status
    FROM fee f
    JOIN serves s
        ON f.student_no = s.student_no AND f.org_name = s.org_name
    WHERE (f.payment_status = "Late" OR f.date_paid > f.payment_deadline) 
        AND s.org_name = "org_name"
        AND s.academic_year = "acad year"
        AND s.semester = "semester"
    ORDER BY f.date_paid DESC;

---6. View all late payments made by all members of a given organization for a given semester
---     and academic year.

    SELECT 
        f.receipt_no, 
        f.amount, 
        f.payment_deadline,
        f.date_paid,
        f.student_no,
        f.payment_status 
    from fee f
    JOIN serves s
        ON f.student_no = s.student_no AND f.org_name = s.org_name
    WHERE f.payment_status = "Late" OR f.date_paid > f.payment_deadline
        AND s.org_name = "org_name" 
        AND s.academic_year = "acad year"
        AND s.semester = "semester"
    ORDER BY f.date_paid DESC; 


---7. View the percentage of active vs inactive members of a given organization for the last n
---     semesters. (Note: n is a positive integer)

    SELECT
        s.status,
        COUNT(s.student_no) / o.no_of_members AS member_percentage
    FROM serves s
    JOIN organization o
        ON s.org_name = o.org_name
    WHERE s.org_name = "org_name"
        AND s.academic_year = "academic_year"
        AND s.semester = "semester"
    GROUP BY s.status
    ORDER BY
        s.academic_year,
        CASE s.semester     
            WHEN 'Second' THEN 1
            WHEN 'First' THEN 2
            ELSE 3
        END,                 
        s.semester DESC;
        


---8. View all alumni members of a given organization as of a given date.

    SELECT 
        m.student_no, 
        m.first_name, 
        m.middle_name, 
        m.last_name, 
        m.batch, 
        s.org_name,
        s.role,
        s.committee,
        s.academic_year,
        s.status 
    FROM member m
    JOIN serves s
        ON m.student_no = s.student_no
    WHERE s.org_name = "org_name"
        AND s.academic_year < "given date"
    ORDER BY s.academic_year; 

---9. View the total amount of unpaid and paid fees or dues of a given organization as of a given date.

    SELECT COALESCE(SUM(CASE WHEN f.payment_status = 0 OR f.date_paid IS NULL THEN f.amount ELSE 0 END), 0) as "Unpaid",
            COALESCE(SUM(CASE WHEN f.payment_status = 1 OR f.date_paid IS NOT NULL THEN f.amount ELSE 0 END), 0) as "Paid"
    FROM fee f
    WHERE f.org_name = "org_name" AND (f.date_paid <= '2date paid' OR f.date_paid IS NULL);

---10. View the member/s with the highest debt of a given organization for a given semester.
    SELECT
        s.student_no,
        s.org_name,
        SUM(f.amount) AS total_debt
    FROM FEE f
    JOIN SERVES s
        ON f.student_no = s.student_no AND f.org_name = s.org_name
    WHERE s.org_name = "org_name"
        AND s.academic_year = "academic_year"
        AND s.semester = "semester"
        AND (f.payment_status = "Unpaid" OR f.date_paid IS NULL) 
    GROUP BY s.student_no, s.org_name 
    ORDER BY total_debt DESC
    LIMIT 1;
