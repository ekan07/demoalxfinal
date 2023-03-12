-- List of class(es) Asign to a teacher
SELECT * FROM classes WHERE id IN (
    SELECT class_id FROM students WHERE class_id IN (
        SELECT class_id FROM teachers WHERE userid = :userid))
AND id IN (
    SELECT currentclass_id FROM class_details)
ORDER BY class_name

-- Query students in a specified class
SELECT reg_num as admission_number, surname, othername, gender FROM people
JOIN students ON people.id = students.person_id
JOIN classes ON students.class_id = classes.id
JOIN teachers ON classes.id = teachers.class_id
WHERE teachers.userid = :userid AND classes.id = :id

-- Query for student's details
SELECT * FROM people
JOIN students ON people.id = students.person_id
JOIN classes ON students.class_id = classes.id
JOIN teachers ON classes.id = teachers.class_id
JOIN class_details ON class_details.currentclass_id = classes.id
GROUP BY students.reg_num, class_details.currentclass_id
HAVING students.reg_num = :reg_num

-- Get class(es) asigned to teacher
SELECT class_name FROM classes
JOIN teachers ON classes.id = teachers.class_id
JOIN class_details ON class_details.currentclass_id = classes.id
WHERE teachers.userid = :userid
GROUP BY class_details.currentclass_id

-- Query for asigned subject to a specified class
SELECT * FROM b_subjects
WHERE subject_name = :subject_name AND class_id = :class_id
LIMIT 1

-- Query for asigned subject to a specified class
SELECT b_subjects.id, subject_name, subject_code, b_subjects.class_id, class_name FROM b_subjects
JOIN classes ON b_subjects.class_id = classes.id
JOIN teachers ON b_subjects.teacher_id = teachers.userid
GROUP BY subject_name, userid, class_name
HAVING userid = :userid
ORDER BY class_name

-- Query for alread registered students
SELECT * FROM subject_offering
WHERE subject_id = :subject_id AND subjectcode_name = :subjectcode_name
ORDER BY student_id

-- db.execute("BEGIN TRANSACTION")
-- rows = db.execute("SELECT likes FROM posts WHERE id = ?", id);
-- likes = rows[0]["likes"]
-- db.execute("UPDATE posts SET likes = ? WHERE id = ?", likes + 1, id);
-- db.execute("COMMIT")

CREATE TABLE users (
     id INTEGER, username TEXT NOT NULL, password_hash TEXT NOT NULL, PRIMARY KEY(id));

CREATE TABLE teachers (
     person_id INTEGER, class_id INTEGER NOT NULL, userid INTEGER NOT NULL, FOREIGN KEY(person_id) REFERENCES people(id),
     FOREIGN KEY(class_id) REFERENCES classes(id), FOREIGN KEY(userid) REFERENCES users(id));

CREATE TABLE classes (
     id INTEGER, class_name TEXT NOT NULL, PRIMARY KEY(id));

CREATE TABLE people (
    id INTEGER, surname TEXT NOT NULL, othername TEXT NOT NULL, gender TEXT NOT NULL,
    lga,states TEXT NOT NULL, nationality TEXT NOT NULL, religion TEXT NOT NULL,
    date_of_birth TEXT NOT NULL, affiliation TEXT NOT NULL, PRIMARY KEY(id));

CREATE TABLE students (
    reg_num INTEGER UNIQUE, person_id INTEGER, class_id INTEGER NOT NULL, st_email TEXT NOT NULL,
    FOREIGN KEY(person_id) REFERENCES people(id), FOREIGN KEY(class_id) REFERENCES classes(id));

CREATE TABLE unique_ids (
    id INTEGER, year_code TEXT NOT NULL, sch_code TEXT NOT NULL, reg_code INTEGER NOT NULL,
    regnum_id INTEGER NOT NULL, FOREIGN KEY(regnum_id) REFERENCES students(reg_num), PRIMARY KEY(id));

CREATE TABLE images (
    regnum_id INTEGER NOT NULL, image TEXT NOT NULL, mimetype TEXT NOT NULL , FOREIGN KEY(regnum_id) REFERENCES students(reg_num));

CREATE TABLE guardians (
    regnum_id INTEGER NOT NULL, g_name TEXT NOT NULL, g_address TEXT NOT NULL, g_email TEXT NOT NULL, g_phone TEXT NOT NULL,
    FOREIGN KEY(regnum_id) REFERENCES students(reg_num));

CREATE TABLE class_details (
    id INTEGER, entryclass_id INTEGER NOT NULL, currentclass_id INTEGER NOT NULL, admsn_date TEXT NOT NULL,
    cl_session TEXT NOT NULL, class_status TEXT DEFAULT 'Active', trans_grad_date TEXT DEFAULT 'Not applicable',
    FOREIGN KEY(currentclass_id) REFERENCES classes(id), PRIMARY KEY(id));

CREATE TABLE b_subjects (
    id INTEGER NOT NULL, subject_name TEXT NOT NULL, subject_code TEXT NOT NULL, teacher_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL, FOREIGN KEY(teacher_id) REFERENCES users(id), FOREIGN KEY(class_id) REFERENCES classes(id),
    PRIMARY KEY(id));

CREATE TABLE subject_offering (
    id INTEGER NOT NULL, subjectcode_name TEXT NOT NULL, sch_session TEXT NOT NULL, subject_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL, FOREIGN KEY(subject_id) REFERENCES b_subjects(id),
    FOREIGN KEY(student_id) REFERENCES students(reg_num), PRIMARY KEY(id));


CREATE UNIQUE INDEX userid ON users (userid);
CREATE INDEX index ON TABLE column;