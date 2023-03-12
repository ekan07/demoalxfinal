import os
import re

from studentrecord import app

from flask import redirect, render_template, request, session
from functools import wraps
from datetime import datetime


def allowed_image(filename):
    """ checking and validating file extension 'upload an image' """

    # We only want files with a dot in the filename
    if not "." in filename:
        return False
    # Split the extension from the image filename
    img_exsn = filename.rsplit(".", 1)[1]
    # Check if the extension is in ALLOWED_IMAGE_EXTENSIONS
    if img_exsn.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


def allowed_image_filesize(filesize):
    """ Validate the image filesize """

    if  int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
        return True
    else:
        return False


def email_address_valid(email):
    """Validate the email address using a regex."""

    if not re.match("^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$", email):
        return False
    return True


def signup_password_valid(password):
    """
    https://www.geeksforgeeks.org/password-validation-in-python/
    """

    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
    # compiling regex
    pat = re.compile(reg)
    # searching regex
    mat = re.search(pat, password)
    # validating conditions
    if mat:
        return True
    else:
        return False


def reg_pool(reg_codes):
    """
    Generate registration numbers

    https://stackoverflow.com/questions/60316144/assign-a-unique-4-digit-number-to-a-list-of-ids-using-python
    """
    try:
        pools = []
        for i in range(100, 1000):
            pools.append(i)

        year = datetime.now().strftime("%Y")
        year_code = year[2] + year[3]

        SCH_CODE = "714"

        reg_sets = set()
        if len(reg_codes) != 0:
            for reg_c in reg_codes:
                reg_sets.add(reg_c["reg_code"])

        # Asign registration number
        poolsets = set(pools)
        reg_code = 0
        for poolset in poolsets:
            if poolset not in reg_sets:
                reg_sets.add(poolset)
                reg_code += poolset
                break
        reg_num = year_code + SCH_CODE + str(reg_code)

        return {
            "year_code" : year_code,
            "sch_code" : SCH_CODE,
            "reg_code" : reg_code,
            "reg_num" : reg_num,
            "pools" : pools
        }
    except (KeyError, TypeError, ValueError):
        return None


def school_session():
    """ Asign school session """

    now = datetime.now()
    if now.month >= 9:
        return str(now.year) +'/'+ str(now.year + 1)
    else:
        return str(now.year - 1) +'/'+ str(now.year)


def asign_classcode(classname):
    if classname == "Basic 1":
        return "1"
    elif classname == "Basic 2":
        return "2"
    elif classname == "Basic 3":
        return "3"
    elif classname == "Basic 4":
        return "4"
    elif classname == "Basic 5":
        return "5"


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def e_message(message, code=400):
    """Render message as an error to user."""

    return render_template("errmessage.html", message=message, code=code), code