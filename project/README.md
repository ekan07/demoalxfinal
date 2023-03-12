# STUDENT AND SUBJECT REGISTRATION

#### Video Demo:  <https://youtu.be/yk1ZL8lAwQ8>

### Description:

#### Menu
1. Sign Up
2. Log In
3. View Class
4. Asign Class-Teacher
5. Register Student
6. Asign Subject
7. Register Subject

This application registers newly admitted primary school students, from a class of Basic 1 to 5, and subjects offered by each registered student.

The user(teacher) sign up and log in to the application.
Then in the Asign Class-Teacher menu, the user asign class(es) that the user will handle for the registration of students.
Newly admitted students are register to the already asigned class with Register Student menu.
Asign subject(s) the user will be teaching the students in that class(es).
Register students that offer the asigned subject(s).
The View Class menu displays all the asigned class(es), list of admitted students which can be downloaded as CSV file, and each student's profile can be view.

#### Features & Functionality

##### __init__.py
This file pulls all the parts of the application together into a package, thereby treats it as a package.

##### helpers.py
The helper file contains functions/methods that are used in the views file.

##### views.py

1. **asign_classteacher**
A view function that asign a class and then asign a user(teacher) to that asigned class.

Database Tables:
- classes
- teachers

2. **studentdetails**
A view function representing registration of class and student details. Student registration/admission number is generated and
asigned to the newly registered student.

Database Tables:
- people
- students
- unique_ids
- class_details

3. **uploadimg**
A view function that upload student's picture.

Database Tables:
- images

4. **guardians**
A view function representing the guardian's details for a particular student.

Database Tables:
- guardians

5. **bsubjects**
A view function that get class(es) asigned to teacher.

Database Tables:
- classes
- teachers
- class_details

6. **bsubject**
A view function that asign subject to a class.

Database Tables:
- b_subjects

7. **offer_bsubjects**
A view function that get list of students for subject registration, list of subjects asigned to specified class(es),
check if students already registered a subject.

Database Tables:
- people
- students
- classes
- teachers
- class_details
- b_subjects

8. **students for a class subject**
A view function representing registration of students for a class subject.

Database Tables:
- subject_offering

9. **index**
A view function that list the class(es) the teacher is asigned to teach.

Database Table
- classes

10. **classStudents**
This view function that display list of students in a class.

Database Tables:
- people
- students
- classes
- teachers

11. **studentprofile**
A view function that display required student details on page.

Database Tables:
- people
- students
- classes
- teachers
- class_details
- images
- guardians

