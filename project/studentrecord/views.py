import os
import re
import csv
from pathlib import Path

from flask.wrappers import Request
from studentrecord import app

from cs50 import SQL
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session, Response, url_for, send_from_directory
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from studentrecord.helpers import login_required, allowed_image_filesize, allowed_image, reg_pool, email_address_valid, e_message, asign_classcode, school_session
from werkzeug.utils import secure_filename


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///studentreg.db")

# Generate a secret random key for the session
app.secret_key = os.urandom(24)

CLASSNAMES = [
    "Basic 1",
    "Basic 2",
    "Basic 3",
    "Basic 4",
    "Basic 5"
]

SUBJECTS = {
    "AGRS": "Agricultural Science",
    "ENGL": "English Language",
    "BAST": "Basic Science and Technology",
    "CIVIC": "Civic Education",
    "COMS": "Computer Science",
    "CCA": "Cultural and Creative Art",
    "HEC": "Home Economics",
    "MATH": "Mathematics",
    "PHE": "P.H.E.",
    "SEC": "Security Education",
    "SOS": "Social Studies",
}

# Create views:


@app.route("/")
@login_required
def index():
    """ List of class(es) Asign to a teacher """

    # Query class(es) asigned to teacher
    classes = db.execute("SELECT * FROM classes WHERE id IN (SELECT class_id FROM students WHERE class_id IN (SELECT class_id FROM teachers WHERE userid = :userid)) AND id IN (SELECT currentclass_id FROM class_details) ORDER BY class_name",
                         userid=session["user_id"])
    return render_template("/index.html", classes=classes)


@app.route("/download_csv/<int:class_id>", methods=["GET", "POST"])
@login_required
def download_csv(class_id):
    """ download csv files of list of students in a specified class """

    # Query students in a specified class
    students = db.execute("SELECT reg_num as admission_number, surname, othername, gender FROM people JOIN students ON people.id = students.person_id JOIN classes ON students.class_id = classes.id JOIN teachers ON classes.id = teachers.class_id WHERE teachers.userid = :userid AND classes.id = :id",
                          userid=session['user_id'], id=class_id)
    if len(students) == 0:
        return e_message("Not authorized", 404)

    classRow = db.execute(
        "SELECT class_name FROM classes WHERE id = :id", id=class_id)[0]
    # field names
    fields = ['admission_number', 'surname', 'othername', 'gender']
    # name for csv file to be created
    filename = classRow["class_name"] + ".csv"
    # writing to csv file
    csv_path = Path("studentrecord", "static", "client", "csv")
    with open(Path(csv_path, filename), 'w', encoding="utf-8") as csvfile:
        # creating a csv dict writer object
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        # writing headers (field names)
        writer.writeheader()
        # writing data rows
        writer.writerows(students)
    # Download the csv file
    return send_from_directory(app.config["CLIENT_CSV"], Path(csv_path, filename), as_attachment=True)


@app.route("/<int:class_id>", methods=["GET", "POST"])
@login_required
def classStudents(class_id):
    """ List of students in a class """

    # Query students in a specified class
    students = db.execute("SELECT reg_num, surname, othername, gender FROM people JOIN students ON people.id = students.person_id JOIN classes ON students.class_id = classes.id JOIN teachers ON classes.id = teachers.class_id WHERE teachers.userid = :userid AND classes.id = :id",
                          userid=session['user_id'], id=class_id)
    if len(students) == 0:
        return e_message("Not authorized", 404)
    return render_template("/classstudents.html", students=students)


@app.route("/studentprofile/<int:student_regnum>")
@login_required
def studentprofile(student_regnum):
    """ Display student details on page """

    # Query for student's details
    studentDocument = db.execute("SELECT * FROM people JOIN students ON people.id = students.person_id JOIN classes ON students.class_id = classes.id JOIN teachers ON classes.id = teachers.class_id JOIN class_details ON class_details.currentclass_id = classes.id GROUP BY students.reg_num, class_details.currentclass_id HAVING students.reg_num = :reg_num",
                                 reg_num=student_regnum)
    if len(studentDocument) == 0:
        return e_message("Invalid url link", 404)
    image = db.execute(
        "SELECT * FROM images WHERE regnum_id = :regnum_id", regnum_id=student_regnum)
    # Use default image if no uploaded picture
    if len(image) == 0:
        if studentDocument[0]['gender'].lower() == 'female':
            # Image storage path
            imgFilePath = "img/default/female.png"
        elif(studentDocument[0]['gender'].lower()) == 'male':
            # Image storage path
            imgFilePath = "img/default/male.jpg"
    else:
        # Split the extension from the filename
        img_exsn = image[0]["mimetype"].rsplit("/", 1)[1]
        # Image storage path
        imgFilePath = "img/uploads/basic/" + \
            str(image[0]["regnum_id"]) + "." + img_exsn
        # Write image to storage path
        with open("studentrecord/static/" + imgFilePath, "wb") as file:
            file.write(image[0]["image"])

    entryClass = db.execute("SELECT class_name FROM classes WHERE id = :id",
                            id=studentDocument[0]["entryclass_id"])[0]
    currentClass = db.execute("SELECT class_name FROM classes WHERE id = :id",
                              id=studentDocument[0]["currentclass_id"])[0]
    guardian = db.execute(
        "SELECT * FROM guardians WHERE regnum_id = :regnum_id", regnum_id=student_regnum)[0]
    return render_template("/studentprofile.html", imgfile=imgFilePath, studentdocument=studentDocument[0], entryclass=entryClass,
                           currentclass=currentClass, guardian=guardian)


@app.route("/asign_classteacher", methods=["GET", "POST"])
@login_required
def asign_classteacher():
    """ Asign class to teacher """

    if request.method == "POST":
        className = request.form.get("classname")
        missing = list()
        # Ensure field(s) was submitted (key : value):
        # -------------------------------------------
        for k, v in request.form.items():
            if not v:
                missing.append(k)
        if missing:
            flash(f"Missing fields for {', '.join(missing)}", "danger")
            return redirect("/asign_classteacher")

        if className == None:
            flash("Please select class name", "danger")
            return redirect("/asign_classteacher")
        # Ensure that class name exist
        if className not in CLASSNAMES:
            return e_message("Invalid Class Name", 404)

        classID = int(asign_classcode(className))
        # Ensure class exist and teacher is not asign to a particular class more than once:
        classRow = db.execute(
            "SELECT * FROM classes WHERE class_name = :class_name", class_name=className)
        if len(classRow) != 0:
            teacherRows = db.execute("SELECT * FROM teachers WHERE class_id = :class_id AND userid = :userid",
                                     class_id=classRow[0]["id"], userid=session['user_id'])
            if len(teacherRows) != 0:
                flash(f"{classRow[0]['class_name']} already asigned", "danger")
                return redirect("/asign_classteacher")
            else:
                # Asign class to teacher
                db.execute("INSERT INTO teachers (class_id, userid) VALUES(:class_id, :userid)",
                           class_id=classRow[0]["id"], userid=session["user_id"])
                flash(f"{classRow[0]['class_name']} asigned", "success")
                return redirect("/")
        else:
            # Asign class
            db.execute("INSERT INTO classes (id, class_name) VALUES(:id, :class_name)",
                       id=classID, class_name=className)
            # Asign class to teacher
            db.execute("INSERT INTO teachers (class_id, userid) VALUES(:class_id, :userid)",
                       class_id=classID, userid=session["user_id"])
            flash(f"{className} asigned", "success")
            return redirect("/")

    classnames = CLASSNAMES
    # asign_classcode(classname)
    return render_template("/classteacher.html", classnames=classnames)


@app.route("/bsubjects")
@login_required
def bsubjects():
    """ Get class(es) asigned to teacher """

    # Get class(es) asigned to teacher
    classRows = db.execute("SELECT class_name FROM classes JOIN teachers ON classes.id = teachers.class_id JOIN class_details ON class_details.currentclass_id = classes.id WHERE teachers.userid = :userid GROUP BY class_details.currentclass_id",
                           userid=session["user_id"])
    ASIGNEDCLASSES = []
    for classRow in classRows:
        for classname in CLASSNAMES:
            if classRow["class_name"] == classname:
                ASIGNEDCLASSES.append(classname)
    return render_template("/bsubjects.html", asignedclasses=ASIGNEDCLASSES, subjects=SUBJECTS)


@app.route("/bsubject", methods=["GET", "POST"])
@login_required
def bsubject():
    """ Asign subject to a class """

    if request.method == "POST":
        # Get class(es) asigned to teacher
        classRows = db.execute("SELECT classes.id, class_name FROM classes JOIN teachers ON classes.id = teachers.class_id JOIN class_details ON class_details.currentclass_id = classes.id WHERE teachers.userid = :userid GROUP BY class_details.currentclass_id",
                               userid=session["user_id"])
        ASIGNEDCLASSES = []
        for classRow in classRows:
            if classRow["class_name"] in CLASSNAMES:
                ASIGNEDCLASSES.append(classRow["class_name"])

        subjectCode = request.form.get("subjectcode")
        className = request.form.get("classname")
        # Ensure subject and class name is selected
        if subjectCode == None:
            flash(f"Please select subject", "danger")
            return redirect("/bsubjects")
        if className == None:
            flash(f"Please select class name", "danger")
            return redirect("/bsubjects")
        # Ensure selected subject and class name exist in the server
        if subjectCode not in SUBJECTS:
            return e_message("Invalid Subject", 404)
        if className not in ASIGNEDCLASSES:
            return e_message("Invalid Class Name", 404)

        # Insert data into b_subject table
        for classRow in classRows:
            if classRow["class_name"] == className:
                # Check if subject has been asigned to a class
                subjectRow = db.execute("SELECT * FROM b_subjects WHERE subject_name = :subject_name AND class_id = :class_id LIMIT 1",
                                        subject_name=SUBJECTS[subjectCode], class_id=classRow["id"])
                if len(subjectRow) == 1:
                    flash(
                        f"{SUBJECTS[subjectCode]} subject already asigned to {className}", "danger")
                    return redirect("/bsubjects")
                # Else asign subject to a class
                db.execute("INSERT INTO b_subjects (subject_name, subject_code, teacher_id, class_id) VALUES(:subject_name, :subject_code, :teacher_id, :class_id)",
                           subject_name=SUBJECTS[subjectCode], subject_code=subjectCode, teacher_id=session["user_id"], class_id=classRow["id"])
                flash(
                    f"{SUBJECTS[subjectCode]} subject asigned to {className}", "success")
                return redirect("/bsubjects")


@app.route("/offer_bsubjects", methods=["GET", "POST"])
@login_required
def offer_bsubjects():
    """ List of students for subject registration """

    if request.method == "POST":
        classid_subjtname = request.form.get("classid_subjtname")
        # Ensure subject is selected
        if classid_subjtname == None:
            flash("Please select subject", "danger")
            return redirect("/offer_bsubjects")
        # Split input data
        classID = request.form.get("classid_subjtname").rsplit(",", 1)[0]
        subjectName = request.form.get("classid_subjtname").rsplit(",", 1)[1]
        # Query students in a specified class
        students = db.execute("SELECT students.reg_num, surname, othername FROM people JOIN students ON people.id = students.person_id JOIN classes ON students.class_id = classes.id JOIN teachers ON classes.id = teachers.class_id JOIN class_details ON class_details.currentclass_id = classes.id WHERE teachers.userid = :userid AND currentclass_id = :currentclass_id GROUP BY reg_num",
                              userid=session['user_id'], currentclass_id=classID)
        classRows = db.execute("SELECT * FROM classes")
        asignedClassSubjectRows = db.execute("SELECT b_subjects.id, subject_name, subject_code, b_subjects.class_id, class_name FROM b_subjects JOIN classes ON b_subjects.class_id = classes.id JOIN teachers ON b_subjects.teacher_id = teachers.userid GROUP BY subject_name, userid, class_name HAVING userid = :userid ORDER BY class_name",
                                             userid=session["user_id"])

        # Get classCode, bsubjectId, subject_code from a specified classID
        classCode = ""
        bsubjectId = 0
        subject_code = ""
        for asignedClassSubjectRow in asignedClassSubjectRows:
            if asignedClassSubjectRow["subject_name"] == subjectName and asignedClassSubjectRow["class_id"] == int(classID):
                classCode = asign_classcode(
                    asignedClassSubjectRow["class_name"])
                bsubjectId += asignedClassSubjectRow["id"]
                subject_code += asignedClassSubjectRow["subject_code"]
                break
        # Check if students already registered subject
        REGISTERED_STUDENT_IDS = []
        if len(asignedClassSubjectRows) != 0:
            # Asign subject code name
            subjectCodeName = subject_code + classCode
            studentIds = db.execute("SELECT * FROM subject_offering WHERE subject_id = :subject_id AND subjectcode_name = :subjectcode_name ORDER BY student_id",
                                    subject_id=bsubjectId, subjectcode_name=subjectCodeName)
            if len(studentIds) != 0:
                for studentId in studentIds:
                    REGISTERED_STUDENT_IDS.append(studentId["student_id"])
        # List of subjects asigned to specified class(es)
        ASIGNED_CLASS_SUBJECT_ROWS = []
        for asignedClassSubjectRow in asignedClassSubjectRows:
            ASIGNED_CLASS_SUBJECT_ROWS.append(asignedClassSubjectRow)
        # To dynamically change URL of action attribute on form
        url = "register_bsubjects"
        return render_template("/registerbsubjects.html", students=students, registeredstudentids=REGISTERED_STUDENT_IDS, asigned_class_subjects=ASIGNED_CLASS_SUBJECT_ROWS, subject_name=subjectName, class_id=classID, url=url)
    # If request.method is GET:
    # -------------------------
    asignedClassSubjectRows = db.execute("SELECT subject_name, b_subjects.class_id, class_name FROM b_subjects JOIN classes ON b_subjects.class_id = classes.id JOIN teachers ON b_subjects.teacher_id = teachers.userid GROUP BY subject_name, userid, class_name HAVING userid = :userid ORDER BY class_name",
                                         userid=session["user_id"])
    # List of subjects asigned to specified class(es)
    ASIGNED_CLASS_SUBJECT_ROWS = []
    for asignedClassSubjectRow in asignedClassSubjectRows:
        ASIGNED_CLASS_SUBJECT_ROWS.append(asignedClassSubjectRow)
    # To dynamically change URL of action attribute on form
    url = "offer_bsubjects"
    # To temporary hide student registering form in HTML
    # temp_hide_form = "tdisplay"
    return render_template("/registerbsubjects.html", url=url, asigned_class_subjects=ASIGNED_CLASS_SUBJECT_ROWS)


@app.route("/register_bsubjects", methods=["GET", "POST"])
@login_required
def register_bsubjects():
    """ Register students for a class subject """

    if request.method == "POST":
        classID = request.form.get("class_id")
        subject_name = request.form.get("subject_name")
        checkedStudentIDs = request.form.getlist("reg_num")
        # Ensure checkbox(es) is/are checked
        if len(checkedStudentIDs) == 0:
            flash("Ensure checkboxe(s) is/are checked", "danger")
            return redirect("/offer_bsubjects")
        # Asign scool session
        schoolSession = school_session()

        bsubjectRow = db.execute("SELECT b_subjects.id, subject_name, subject_code FROM b_subjects JOIN classes ON b_subjects.class_id = classes.id JOIN teachers ON classes.id = teachers.class_id JOIN class_details ON classes.id = class_details.currentclass_id WHERE teachers.userid = :userid AND subject_name = :subject_name AND class_details.currentclass_id = :currentclass_id GROUP BY subject_name, class_details.currentclass_id",
                                 userid=session["user_id"], subject_name=subject_name, currentclass_id=classID)[0]
        # Query class asigned to teacher
        classRow = db.execute("SELECT * FROM classes WHERE id = (SELECT class_id FROM teachers WHERE userid = :userid AND class_id = :class_id)",
                              userid=session["user_id"], class_id=classID)[0]

        # Asign subject code name
        classCode = asign_classcode(classRow["class_name"])
        subjectCodeName = bsubjectRow["subject_code"] + classCode
        # Register each students for the subject
        for checkedStudentID in checkedStudentIDs:
            db.execute("INSERT INTO subject_offering (subjectcode_name, sch_session, subject_id, student_id) VALUES(:subjectcode_name, :sch_session, :subject_id, :student_id)",
                       subjectcode_name=subjectCodeName, sch_session=schoolSession, subject_id=bsubjectRow["id"], student_id=checkedStudentID)

        flash(
            f"All checked {classRow['class_name']} student(s) have been registered for {bsubjectRow['subject_name']} subject", "success")
        return redirect("/offer_bsubjects")


@app.route("/uploadimg/<int:reg_num>", methods=["GET", "POST"])
@login_required
def uploadimg(reg_num):
    """ Upload an image """

    if request.method == "POST":
        # To access a file being posted by a form, use request.files provided by the request object.
        if request.files:
            image = request.files["image"]
            # if file is empty, use default image
            if image.filename == "":
                flash("default image will be use", "success")
                return render_template("/guardians.html", regnum_id=reg_num)
            # Validate the image filesize:
            if not allowed_image_filesize(request.cookies["filesize"]):
                flash("Filesize exceeded expectation", "danger")
                return render_template("/uploadimg.html", reg_num=reg_num)
            # Validating image file extension:
            if allowed_image(image.filename):
                # Ensuring the filename itself isn't dangerous
                filename = secure_filename(image.filename)
                # Ensure student exist
                student = db.execute(
                    "SELECT * FROM students WHERE reg_num = :reg_num", reg_num=reg_num)
                if len(student) == 0:
                    flash("Registration number no match", "danger")
                    return redirect("/studentdetails")
                # Add fields to images table
                db.execute("INSERT INTO images (regnum_id, image, mimetype) VALUES(:regnum_id, :image, :mimetype)",
                           regnum_id=reg_num, image=image.read(), mimetype=image.mimetype)
                flash("Image saved", "success")
                return render_template("/guardians.html", regnum_id=reg_num)
            else:
                flash("Only JPEG, JPG, PNG, GIF image extension is allowed", "danger")
                return render_template("uploadimg.html", reg_num=reg_num)
                # return redirect(request.url)
    return render_template("/uploadimg.html")


@app.route("/studentdetails", methods=["GET", "POST"])
@login_required
def studentdetails():

    if request.method == "POST":
        missing = list()
        # Ensure field(s) was submitted (key : value):
        for k, v in request.form.items():
            if not v:
                missing.append(k)
        if missing:
            flash(f"Missing fields for {', '.join(missing)}", "danger")
            return render_template("studentdetails.html")

        className = request.form.get("classname")
        schoolSession = request.form.get("sch_session")
        admsnDate = datetime.strptime(
            request.form.get("admsn_date"), "%Y-%m-%d")
        st_email = request.form.get("st_email").strip()
        # In format yyyy-mm-dd
        date_of_birth = datetime.strptime(
            request.form.get("date_of_birth"), "%Y-%m-%d")
        gender = request.form.get("gender").capitalize().strip()
        religion = request.form.get("religion").capitalize().strip()
        affiliation = "student"
        surname = request.form.get("surname").capitalize().strip()

        othername = ""
        lga = ""
        state = ""
        nationality = ""
        s_othername = request.form.get("othername").rsplit()
        for i in s_othername:
            othername += f"{i.capitalize()} "
        s_lga = request.form.get("lga").rsplit()
        for i in s_lga:
            lga += f"{i.capitalize()} "
        s_state = request.form.get("state").rsplit()
        for i in s_state:
            state += f"{i.capitalize()} "
        s_nationality = request.form.get("nationality").rsplit()
        for i in s_nationality:
            nationality += f"{i.capitalize()} "

        if className == None:
            flash("Please select class name", "danger")
            return render_template("classdetails.html", classnames=CLASSNAMES, reg_num=reg_num)
        if schoolSession == None:
            flash("Please select session", "danger")
            return render_template("classdetails.html", classnames=CLASSNAMES, reg_num=reg_num)
        # Ensure that class name exist
        if className not in CLASSNAMES:
            return e_message("Invalid Class Name", 404)
        if schoolSession != school_session():
            return e_message("Invalid School Session", 404)

        # Validate the email address and raise an error if it is invalid
        if not email_address_valid(st_email):
            flash("Please enter a valid email address", "danger")
            return render_template("studentdetails.html")

        # Asign registration number
        reg_rows = db.execute("SELECT reg_code FROM unique_ids")
        reg_codes = reg_pool(reg_rows)
        # Ensure registration number is asigned
        if reg_codes == None:
            flash("Couldn't asign registration number", "danger")
            return render_template("studentdetails.html")

        classRow = db.execute(
            "SELECT * FROM classes WHERE class_name = :class_name", class_name=className)[0]
        # Check that student is registered and asigned to class not more than ones
        detailsRow = db.execute("SELECT surname, othername FROM people JOIN students ON  people.id = students.person_id JOIN classes ON students.class_id = classes.id JOIN teachers ON classes.id = teachers.class_id JOIN class_details ON class_details.currentclass_id = classes.id WHERE teachers.userid = :userid AND classes.id = :id AND currentclass_id = :currentclass_id AND people.surname = :surname AND people.othername = :othername AND cl_session = :cl_session",
                                userid=session['user_id'], id=classRow['id'], currentclass_id=classRow['id'], surname=surname, othername=othername, cl_session=schoolSession)
        if len(detailsRow) != 0:
            flash({detailsRow[0]['surname']} + " " + detailsRow[0]
                  ['othername'] + " registered already ", "danger")
            return render_template("studentdetails.html")

        # Register and asign class to student
        peoplePK = db.execute("INSERT INTO people (surname, othername, gender, lga, states, nationality, religion, date_of_birth, affiliation) VALUES (:surname, :othername, :gender, :lga, :states, :nationality, :religion, :date_of_birth, :affiliation)",
                              surname=surname, othername=othername.strip(), gender=gender, lga=lga.strip(), states=state.strip(), nationality=nationality.strip(), religion=religion, date_of_birth=date_of_birth, affiliation=affiliation)
        studentPK = db.execute("INSERT INTO students (reg_num, person_id, class_id, st_email) VALUES(:reg_num, :person_id, :class_id, :st_email)",
                               reg_num=int(reg_codes["reg_num"]), person_id=peoplePK, class_id=classRow["id"], st_email=st_email)
        db.execute("INSERT INTO unique_ids (year_code, sch_code, reg_code, regnum_id) VALUES(:year_code, :sch_code, :reg_code, :regnum_id)",
                   year_code=reg_codes["year_code"], sch_code=reg_codes["sch_code"], reg_code=reg_codes["reg_code"], regnum_id=int(reg_codes["reg_num"]))
        db.execute("INSERT INTO class_details (entryclass_id, currentclass_id, admsn_date, cl_session) VALUES(:entryclass_id, :currentclass_id, :admsn_date, :cl_session)",
                   entryclass_id=classRow["id"], currentclass_id=classRow["id"], admsn_date=admsnDate, cl_session=schoolSession)

        reg_num = int(reg_codes["reg_num"])

        flash("Details saved", "success")
        return render_template("/uploadimg.html", reg_num=reg_num)

    # if request.method is GET
    schoolSession = school_session()
    classNames = db.execute("SELECT class_name FROM classes WHERE id IN (SELECT class_id FROM teachers WHERE userid = :userid) ORDER BY class_name",
                            userid=session["user_id"])
    return render_template("/studentdetails.html", classnames=classNames, schoolsession=schoolSession)


@app.route("/guardians/<int:regnum_id>", methods=["GET", "POST"])
@login_required
def guardians(regnum_id):

    if request.method == "POST":
        missing = list()
        # Ensure field(s) was submitted (key : value):
        # -------------------------------------------
        for k, v in request.form.items():
            if not v:
                missing.append(k)
        if missing:
            flash(f"Missing fields for {', '.join(missing)}", "danger")
            return render_template("guardians.html")

        email = request.form.get("g_email").strip()
        phone = request.form.get("g_phone")

        g_address = ""
        address = request.form.get("g_address").rsplit()
        for item in address:
            g_address += f"{item.capitalize()} "
        g_name = ""
        names = request.form.get("g_name").rsplit()
        for name in names:
            g_name += f"{name.capitalize()} "
        db.execute("INSERT INTO guardians (regnum_id, g_name, g_address, g_email, g_phone) VALUES(:regnum_id, :g_name, :g_address, :g_email, :g_phone)",
                   regnum_id=regnum_id, g_name=g_name.strip(), g_address=g_address.strip(), g_email=email, g_phone=phone)
        flash("Guardians details saved", "success")
        return redirect("/")

    return render_template("/guardians.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        missing = list()
        # Ensure username and password are filled in
        for k, v in request.form.items():
            if not v:
                missing.append(k)
        if missing:
            feedback = f"Missing fields for {', '.join(missing)}"
            flash(feedback, "danger")
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))
        # Ensure username exists:
        if len(rows) != 1:
            # missing.append("username and/or password not correct")
            feedback = f"username and/or password not correct"
            flash(feedback, "danger")
            return render_template("login.html")
        # Ensure username exists and password is correct
        if rows[0]["username"] and not check_password_hash(rows[0]["password_hash"], request.form.get("password")):
            # missing.append("username and/or password not correct")
            feedback = f"username and/or password not correct"
            flash(feedback, "danger")
            return render_template("login.html")
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """sign up teacher"""

    # TODO: Register Teacher
    if request.method == "GET":
        return render_template("/signup.html")
    else:
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        # Ensure username and password was submitted (key : value):
        missing = list()
        for k, v in request.form.items():
            if not v:
                missing.append(k)
        if missing:
            feedback = f"Missing fields for {', '.join(missing)}"
            flash(feedback, "danger")
            return render_template("signup.html")
        # Ensure no space in field(s) was submitted:
        for k, v in request.form.items():
            count = 0
            for i in v:
                if i.isspace():
                    count += 1
            if count > 0:
                missing.append(k)
        if missing:
            feedback = f"field(s) can't have space: {', '.join(missing)}"
            flash(feedback, "danger")
            return render_template("signup.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        # Check if username not equal to None then username exists
        if len(rows) == 1:
            missing.append(rows[0]['username'])
            feedback = f"username {''.join(missing)} exist already!"
            flash(feedback, "danger")
            return render_template("signup.html")
        # Check if passwords matches
        if password != request.form.get("confirmation"):
            # missing.append("passwords didn't matched")
            feedback = f"passwords didn't matched"
            flash(feedback, "danger")
            return render_template("signup.html")
        # Hash the password and insert the new user into users database table
        hash = generate_password_hash(password)
        primary_key = db.execute(
            "INSERT INTO users (username, password_hash) VALUES(?, ?)", username, hash)
        # Login the newly registered user and remember which user has logged in
        session["user_id"] = primary_key
        flash("signed up!", "success")
        return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return e_message(e.name, e.code)
# render_template("ermessage.html", message), e.code
# apology("low shares", 400)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
