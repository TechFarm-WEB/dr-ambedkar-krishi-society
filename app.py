# <!---------------------------------------------------------------------
#  Author           : Abhishek
#  Creation Date    : 09/08/2026
#  Transaction      : NA
#  Application Area : BACKEND ENGINE
#  Object ID        : Neudocl
#  BRF Application  : NA
#  BRF DT           : NA
#  ISSUE NO         : GIT HUB ISSUE NO
#  Description      : FILE UPLOADING SYSTEM
# ------------------------------------------------------------------->
# <!---------------------------------------------------------------------
#  Author Modify    : Sakshi
#  Creation Date    : 12/08/2026
#  Transaction      : NA
#  Application Area : BACKEND ENGINE
#  Object ID        : Neudocl
#  BRF Application  : NA
#  BRF DT           : NA
#  ISSUE NO         : GIT HUB ISSUE NO
#  Description      : FILE UPLOADING SYSTEM
# ------------------------------------------------------------------->
#ABHISHEK CHANGE
# Purpose:
# Flask session is used to remember whether
# a user is logged in between requests.



# =====================================================
# ABHISHEK CHANGE
# Purpose:
# Delete physical files from storage
# =====================================================

import os
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    session,

    # =====================================================
    # ABHISHEK CHANGE
    # Purpose:
    # Enable document downloads
    # =====================================================
    send_file
)


from werkzeug.utils import secure_filename

# =====================================================
# ABHISHEK CHANGE
# Purpose:
# Import secure password hashing functions
# =====================================================
from werkzeug.security import generate_password_hash, check_password_hash

import os
import sqlite3
# =====================================================
# ABHISHEK CHANGE
# Purpose:
# Enable OCR text extraction from images
# =====================================================
import pytesseract
from PIL import Image
from datetime import datetime, timedelta
# =====================================================
# ABHISHEK CHANGE
# Purpose:
# Enable TXT to PDF conversion
# =====================================================
from reportlab.pdfgen import canvas
app = Flask(__name__)
# =====================================================
# ABHISHEK CHANGE
# Purpose:
# Configure Tesseract OCR executable
# =====================================================
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe\tesseract.exe"
)




app.secret_key = "abhishek_auth_v1"
# =====================================================
# ABHISHEK CHANGE
# Purpose:
# Convert image files to PDF
# =====================================================
from PIL import Image
# =========================================================
# ABHISHEK CHANGE
# Purpose:
# Enable Flask session management
# =========================================================

app.secret_key = "abhishek_auth_v1"
# =====================================================
# ABHISHEK CHANGE
# Purpose:
# Remember Me session duration
# =====================================================
app.permanent_session_lifetime = timedelta(days=30)

UPLOAD_FOLDER = "uploads"
DATABASE = "documents.db"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# =========================================================
# CATEGORIES (single source of truth — used by every route)
# =========================================================

CATEGORIES = {

    "Audit": "Audit",

    "Revenue": "Revenue",

    "Court Matter": "Court_Matter",

    "Membership Details": "Membership_Details",

    "Police Department": "Police_Department",

    "Dispute": "Dispute",

    "Committee Proceedings":
        "Committee_Proceedings",

    "Samiti Records":
        "Samiti_Records",

    "Others": "Others",

    "Official Letters":
        "Official_Letters"
}

CATEGORY_ICONS = {
    "Audit": "fa-clipboard-check",
    "Revenue": "fa-sack-dollar",
    "Court Matter": "fa-scale-balanced",
    "Membership Details": "fa-users",
    "Police Department": "fa-shield-halved",
    "Dispute": "fa-gavel",
    "Committee Proceedings": "fa-building-columns",
    "Samiti Records": "fa-box-archive",
    "Others": "fa-thumbtack",
    "Official Letters": "fa-envelope-open-text"
}


# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         filename TEXT NOT NULL,
         category TEXT NOT NULL,
         source TEXT NOT NULL DEFAULT 'upload',
         filepath TEXT NOT NULL,
         filesize INTEGER DEFAULT 0,
         uploaded_by TEXT,
         uploaded_at TEXT NOT NULL
    )
""")
    try:
        conn.execute(
        "ALTER TABLE documents ADD COLUMN uploaded_by TEXT"
    )
    except:
       pass

    # =====================================================
    # ABHISHEK CHANGE
    # Purpose:
    # Store login users for authentication
    # =====================================================
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        mobile TEXT UNIQUE,
        email TEXT UNIQUE NOT NULL,
        address TEXT,
        fav_place TEXT,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user'
    )
""")
    try:
        conn.execute("ALTER TABLE users ADD COLUMN mobile TEXT")
    except:
        pass

    try:
        conn.execute("ALTER TABLE users ADD COLUMN address TEXT")
    except:
        pass

    try:
        conn.execute("ALTER TABLE users ADD COLUMN fav_place TEXT")
    except:
        pass



    # =====================================================
# ABHISHEK CHANGE
# Purpose:
# Store user's last successful login timestamp
# =====================================================


    try:
        conn.execute("ALTER TABLE users ADD COLUMN last_login TEXT")
    except:
        pass

    conn.commit()
    conn.close()


# def record_document(filename, category, source, filepath, filesize):

#     conn = get_db()

#     conn.execute(
#         """
#         INSERT INTO documents
#             (filename, category, source, filepath, filesize, uploaded_at)
#         VALUES (?, ?, ?, ?, ?, ?)
#         """,
#         (
#             filename,
#             category,
#             source,
#             filepath,
#             filesize,
#             datetime.utcnow().isoformat()
#         )
#     )

#     conn.commit()
#     conn.close()
# =========================================================
# SAVE DOCUMENT RECORD WITH IST TIMESTAMP
# =========================================================

from zoneinfo import ZoneInfo


def record_document(
    filename,
    category,
    source,
    filepath,
    filesize,
    uploaded_by=None
):

    # UTC + 5:30 = IST
    ist_timestamp = (
        datetime.utcnow() + timedelta(hours=5, minutes=30)
    ).isoformat()

    conn = get_db()

    conn.execute(
        """
        INSERT INTO documents
            (
                filename,
                category,
                source,
                filepath,
                filesize,
                uploaded_by,
                uploaded_at
            )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            filename,
            category,
            source,
            filepath,
            filesize,
            uploaded_by,
            ist_timestamp
        )
    )

    conn.commit()
    conn.close()

init_db()


init_db()

# =====================================================
# ABHISHEK CHANGE
# Purpose:
# Create default admin user if not exists
# =====================================================

conn = get_db()

conn.execute("""
INSERT OR IGNORE INTO users
(name, email, password, role)
VALUES
('Abhishek', 'admin@neudocl.com', 'admin123', 'admin')
""")

conn.commit()
conn.close()



# =====================================================
# ABHISHEK CHANGE
# Purpose:
# Convert TXT file to PDF
# =====================================================

def txt_to_pdf(txt_path, pdf_path):

    pdf = canvas.Canvas(pdf_path)

    y = 800

    with open(
        txt_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:

        for line in file:

            pdf.drawString(
                40,
                y,
                line.strip()
            )

            y -= 20

            if y < 40:

                pdf.showPage()
                y = 800

    pdf.save()

# =====================================================
# ABHISHEK CHANGE
# Purpose:
# Convert image file to PDF
# =====================================================


def image_to_pdf(image_path, pdf_path):

    image = Image.open(image_path)

    if image.mode != "RGB":
        image = image.convert("RGB")

    image.save(
        pdf_path,
        "PDF"
    )


# =====================================================
# ABHISHEK CHANGE
# Purpose:
# Extract text from image using OCR
# =====================================================

def image_to_text(image_path):

    image = Image.open(image_path)

    extracted_text = pytesseract.image_to_string(
        image
    )

    return extracted_text


# =========================================================
# HOME / DASHBOARD
# =========================================================
from flask import render_template, request, redirect

@app.route("/")
def home():
    return render_template("login.html")




# =========================================================
# LOGIN PAGE
# =========================================================


        # =====================================================
# ABHISHEK CHANGE
# Purpose:
# Verify hashed password
# =====================================================
# =====================================================
# ABHISHEK CHANGE
# Purpose:
# Support both hashed passwords and legacy plain-text
# passwords during migration
# =====================================================

       # =====================================================
# ABHISHEK CHANGE
# Purpose:
# Support both hashed passwords and legacy plain-text
# passwords during migration
# =====================================================

# =========================================================
# LOGIN PAGE
# =========================================================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")
        # =====================================================
# ABHISHEK CHANGE
# Purpose:
# Read Remember Me checkbox
# =====================================================
        remember_me = request.form.get("remember_me")

        conn = get_db()

        # =====================================================
        # ABHISHEK CHANGE
        # Purpose:
        # Find user by email only
        # Password will be verified using hash
        # =====================================================
        # =====================================================
# ABHISHEK CHANGE
# Purpose:
# Allow login using email OR mobile number
# =====================================================
        user = conn.execute(
    """
    SELECT *
    FROM users
    WHERE email = ?
    OR mobile = ?
    """,
    (email, email)
).fetchone()

        conn.close()

        if user:

            password_valid = False

            try:

                password_valid = check_password_hash(
                    user["password"],
                    password
                )

            except:

                password_valid = False

            # =====================================================
            # ABHISHEK CHANGE
            # Purpose:
            # Auto-migrate legacy plain-text passwords
            # to secure hashed passwords
            # =====================================================
            if not password_valid and user["password"] == password:

                conn = get_db()

                conn.execute(
                    """
                    UPDATE users
                    SET password = ?
                    WHERE id = ?
                    """,
                    (
                        generate_password_hash(password),
                        user["id"]
                    )
                )

                conn.commit()
                conn.close()

                password_valid = True

            if password_valid:

                session["logged_in"] = True
                session["user_name"] = user["name"]
                session["user_role"] = user["role"]

                # =====================================================
                # ABHISHEK CHANGE
                # Purpose:
                # Store logged-in user ID in session
                # =====================================================
                session["user_id"] = user["id"]
                # =====================================================
    # ABHISHEK CHANGE
    # Purpose:
    # Keep user logged in longer
    # =====================================================
                if remember_me:
                    session.permanent = True

# =====================================================
    # ABHISHEK CHANGE
    # Purpose:
    # Update last successful login time
    # =====================================================


                conn = get_db()

                conn.execute(
                    """
                    UPDATE users
                    SET last_login = ?
                    WHERE id = ?
                    """,
                    (
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        user["id"]
                    )
                )

                conn.commit()
                conn.close()

                return redirect("/dashboard")
        return render_template(
            "login.html",
            error="Invalid Email or Password"
        )

    return render_template(
        "login.html",
        error=None
    )


# =========================================================
# REGISTER
# =========================================================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        mobile = request.form.get("mobile")
        email = request.form.get("email")
        address = request.form.get("address")
        fav_place = request.form.get("fav_place")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

                # Password validation
        if password != confirm_password:
            return render_template(
                "register.html",
                error="Passwords do not match"
            )

        # =====================================================
        # ABHISHEK CHANGE
        # Purpose:
        # Convert plain password into secure hash
        # before storing in database
        # =====================================================
        hashed_password = generate_password_hash(password)

        conn = get_db()
        

              # Check if email already exists
        existing_user = conn.execute(
            """
            SELECT * FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        if existing_user:

            conn.close()

            return render_template(
                "register.html",
                error="Email already registered"
            )

        # =====================================================
        # ABHISHEK CHANGE
        # Purpose:
        # Check if mobile number already exists
        # =====================================================

        existing_mobile = conn.execute(
            """
            SELECT *
            FROM users
            WHERE mobile = ?
            """,
            (mobile,)
        ).fetchone()

        if existing_mobile:

            conn.close()

            return render_template(
                "register.html",
                error="Mobile number already registered"
            )



    

        # Save new user
        conn.execute(
            """
            INSERT INTO users
            (
                name,
                mobile,
                email,
                address,
                fav_place,
                password,
                role
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                mobile,
                email,
                address,
                fav_place,
                hashed_password,
                "user"
            )
        )
        

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template(
        "register.html",
        error=None
    )

# =========================================================
# ABHISHEK CHANGE
# Purpose:
# Recover forgotten password using favourite place
# =========================================================

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form.get("email")
        fav_place = request.form.get("fav_place")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # =====================================================
        # ABHISHEK CHANGE
        # Purpose:
        # Validate password confirmation
        # =====================================================

        if password != confirm_password:

            return render_template(
                "forgot_password.html",
                error="Passwords do not match"
            )

        conn = get_db()

        # =====================================================
        # ABHISHEK CHANGE
        # Purpose:
        # Verify user using email and favourite place
        # =====================================================

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            AND fav_place = ?
            """,
            (email, fav_place)
        ).fetchone()

        if not user:

            conn.close()

            return render_template(
                "forgot_password.html",
                error="Invalid Email or Favourite Place"
            )

        # =====================================================
        # ABHISHEK CHANGE
        # Purpose:
        # Update password
        # =====================================================

        conn.execute(
            """
            UPDATE users
            SET password = ?
            WHERE id = ?
            """,
            (password, user["id"])
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template(
        "forgot_password.html",
        error=None
    )








# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if not session.get("logged_in"):
        return redirect("/login")

    return render_template(
        "index.html",
        categories=CATEGORIES,
        category_icons=CATEGORY_ICONS
    )


# =========================================================
# ABHISHEK CHANGE
# Purpose:
# Admin user management page
# =========================================================

@app.route("/users")
def users():

    # =====================================================
    # ABHISHEK CHANGE
    # Purpose:
    # Allow only logged-in users
    # =====================================================

    if not session.get("logged_in"):
        return redirect("/login")

    # =====================================================
    # ABHISHEK CHANGE
    # Purpose:
    # Allow only admin users
    # =====================================================

    if session.get("user_role") != "admin":
        return "Access Denied", 403

    conn = get_db()

    users = conn.execute(
        """
        SELECT *
        FROM users
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "users.html",
        users=users
    )




# =========================================================
# ABHISHEK CHANGE
# Purpose:
# Allow admin to delete users
# =========================================================

@app.route("/delete-user/<int:user_id>")
def delete_user(user_id):

    # =====================================================
    # ABHISHEK CHANGE
    # Purpose:
    # Allow only admin users
    # =====================================================

    if not session.get("logged_in"):
        return redirect("/login")

    if session.get("user_role") != "admin":
        return "Access Denied", 403

    conn = get_db()

    # =====================================================
    # ABHISHEK CHANGE
    # Purpose:
    # Prevent admin deleting own account
    # =====================================================

    current_user_id = session.get("user_id")

    if user_id == current_user_id:
        conn.close()
        return "You cannot delete your own account"

    conn.execute(
        "DELETE FROM users WHERE id = ?",
        (user_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/users")


# =========================================================
# ABHISHEK CHANGE
# Purpose:
# Allow admin to change user roles
# =========================================================

@app.route("/change-role/<int:user_id>")
def change_role(user_id):

    # =====================================================
    # ABHISHEK CHANGE
    # Purpose:
    # Allow only logged-in admins
    # =====================================================

    if not session.get("logged_in"):
        return redirect("/login")

    if session.get("user_role") != "admin":
        return "Access Denied", 403

    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    if not user:
        conn.close()
        return "User not found", 404

    # =====================================================
    # ABHISHEK CHANGE
    # Purpose:
    # Prevent changing your own role
    # =====================================================

    if user_id == session.get("user_id"):
        conn.close()
        return "You cannot change your own role"

    # =====================================================
    # ABHISHEK CHANGE
    # Purpose:
    # Toggle user/admin role
    # =====================================================

    new_role = "admin" if user["role"] == "user" else "user"

    conn.execute(
        "UPDATE users SET role = ? WHERE id = ?",
        (new_role, user_id)
    )

    conn.commit()
    conn.close()

    return redirect("/users")





 
# =========================================================
# UPLOAD DOCUMENT  (Upload New Document panel)
# =========================================================

@app.route("/upload", methods=["POST"])
def upload():

    category = request.form.get("category")
    # =====================================================
# ABHISHEK CHANGE
# Purpose:
# Read selected save format
# =====================================================
    save_format = request.form.get("save_format")
    files = request.files.getlist("file")

    if not category:
        return jsonify(
            success=False,
            message="Please select a category."
        ), 400

    if category not in CATEGORIES:
        return jsonify(
            success=False,
            message="Invalid category selected."
        ), 400

    valid_files = [f for f in files if f and f.filename]

    if not valid_files:
        return jsonify(
            success=False,
            message="Please choose at least one file to upload."
        ), 400

    category_folder = os.path.join(
        app.config["UPLOAD_FOLDER"],
        CATEGORIES[category]
    )

    os.makedirs(
        category_folder,
        exist_ok=True
    )

    saved_files = []

    for file in valid_files:

        filename = secure_filename(file.filename)

        if not filename:
            continue

        destination = os.path.join(
            category_folder,
            filename
        )
        file.save(destination)

        # =====================================================
        # ABHISHEK CHANGE
        # Purpose:
        # Convert TXT file to PDF when requested
        # =====================================================

        if (
            save_format == "pdf"
            and filename.lower().endswith(".txt")
        ):

            pdf_filename = (
                os.path.splitext(filename)[0]
                + ".pdf"
            )

            pdf_destination = os.path.join(
                category_folder,
                pdf_filename
            )

            txt_to_pdf(
                destination,
                pdf_destination
            )

            os.remove(destination)

            filename = pdf_filename
            destination = pdf_destination

        # =====================================================
        # ABHISHEK CHANGE
        # Purpose:
        # Convert JPG / PNG to PDF
        # =====================================================

        elif (
            save_format == "pdf"
            and filename.lower().endswith(
                (".jpg", ".jpeg", ".png")
            )
        ):

            pdf_filename = (
                os.path.splitext(filename)[0]
                + ".pdf"
            )

            pdf_destination = os.path.join(
                category_folder,
                pdf_filename
            )

            image_to_pdf(
                destination,
                pdf_destination
            )

            os.remove(destination)

            filename = pdf_filename
            destination = pdf_destination

        filesize = os.path.getsize(destination)

        record_document(
            filename=filename,
            category=category,
            source="upload",
            filepath=destination,
            filesize=filesize,
            uploaded_by=session.get("user_name")
        )

        saved_files.append(filename)

    if not saved_files:
        return jsonify(
            success=False,
            message="No valid files were uploaded."
        ), 400

    return jsonify(
        success=True,
        message=f"{len(saved_files)} file(s) uploaded successfully to {category}.",
        category=category,
        files=saved_files
    )


# =========================================================
# SCAN & SAVE  (Document Scanner panel)
# =========================================================

@app.route("/scan", methods=["POST"])
def scan_save():

    category = request.form.get("category")
    file = request.files.get("file") 
# =====================================================
# ABHISHEK CHANGE
# Purpose:
# Read selected scanner output format
# =====================================================

    output_format = request.form.get("output_format")

    if not category or category not in CATEGORIES:
        return jsonify(
            success=False,
            message="Please select a valid category before saving."
        ), 400

    if not file or not file.filename:
        return jsonify(
            success=False,
            message="No scanned image was provided."
        ), 400

    category_folder = os.path.join(
        app.config["UPLOAD_FOLDER"],
        CATEGORIES[category]
    )

    os.makedirs(
        category_folder,
        exist_ok=True
    )

    filename = secure_filename(file.filename)

    destination = os.path.join(
        category_folder,
        filename
    )

    file.save(destination)
    
 # =====================================================
# ABHISHEK CHANGE
# Purpose:
# Convert scanned image to TXT using OCR
# =====================================================
    if output_format =="txt":
        extracted_text = image_to_text(destination)
        print("OCR RESULT:")
        print(extracted_text)
        text_filename = (
            os.path.splitext(filename)[0]
            + ".txt"
        )
        text_destination = os.path.join(
            category_folder,
            text_filename
        )
        with open(text_destination, "w") as f:
            f.write(extracted_text)
        os.remove(destination)
        filename = text_filename
        destination = text_destination
           # =====================================================
        # ABHISHEK CHANGE
        # Purpose:
        # Convert scanned text to PDF
        # =====================================================
    if output_format == "txt":
        extracted_text = image_to_text(destination)
        print("OCR RESULT:")
        print(repr(extracted_text))
            #====================================================
# ABHISHEK CHANGE
# Purpose:
# Convert scanned image to PDF
# =====================================================
    elif output_format == "pdf":
        pass
    filesize = os.path.getsize(destination)

    record_document(
        filename=filename,
        category=category,
        source="scanner",
        filepath=destination,
        filesize=filesize
    )

    response = {
        "success": True,
        "message": f"Scanned document saved to {category}.",
        "category": category,
        "filename": filename
    }
    print(response)
    return jsonify(response)




# =========================================================
# OPEN CATEGORY  (unchanged — filesystem-backed listing)
# =========================================================

@app.route("/category/<path:category>")
def show_category(category):

    if category not in CATEGORIES:

        return "Category not found.", 404

    folder = os.path.join(
        app.config["UPLOAD_FOLDER"],
        CATEGORIES[category]
    )

    os.makedirs(
        folder,
        exist_ok=True
    )

    files = []

    for filename in os.listdir(folder):

        filepath = os.path.join(
            folder,
            filename
        )

        if os.path.isfile(filepath):

            files.append(filename)

    return render_template(

        "index.html",

        categories=CATEGORIES,

        category_icons=CATEGORY_ICONS,

        selected_category=category,

        category_files=files
    )

# =====================================================
# ABHISHEK CHANGE
# Purpose:
# Preview file from category page
# =====================================================

@app.route("/preview/<category>/<filename>")
def preview_file(category, filename):

    if category not in CATEGORIES:
        return "Category not found", 404

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        CATEGORIES[category],
        filename
    )

    if not os.path.exists(filepath):
        return "File not found", 404

    return send_file(
        filepath,
        as_attachment=False
    )

# =========================================================
# API — DASHBOARD STATISTICS
# =========================================================

@app.route("/api/stats")
def api_stats():

    conn = get_db()

    # =====================================================
    # ABHISHEK CHANGE
    # Purpose:
    # Count total documents in archive
    # =====================================================

    total_documents = conn.execute(
        "SELECT COUNT(*) AS c FROM documents"
    ).fetchone()["c"]

    # =====================================================
    # ABHISHEK CHANGE
    # Purpose:
    # Count total registered users
    # =====================================================

    total_users = conn.execute(
        "SELECT COUNT(*) AS c FROM users"
    ).fetchone()["c"]

    # =====================================================
    # ABHISHEK CHANGE
    # Purpose:
    # Count documents uploaded through Scanner module
    # =====================================================

    scanned_documents = conn.execute(
        "SELECT COUNT(*) AS c FROM documents WHERE source = ?",
        ("scanner",)
    ).fetchone()["c"]

    # =====================================================
    # ABHISHEK CHANGE
    # Purpose:
    # Count documents uploaded manually
    # =====================================================

    uploaded_documents = conn.execute(
        "SELECT COUNT(*) AS c FROM documents WHERE source = ?",
        ("upload",)
    ).fetchone()["c"]

    # =====================================================
    # ABHISHEK CHANGE
    # Purpose:
    # Count uploads made in the last 7 days
    # =====================================================

    week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()

    new_uploads = conn.execute(
        "SELECT COUNT(*) AS c FROM documents WHERE uploaded_at >= ?",
        (week_ago,)
    ).fetchone()["c"]

    conn.close()

    # =====================================================
    # ABHISHEK CHANGE
    # Purpose:
    # Return dashboard and reports statistics
    # =====================================================

    return jsonify(
        total_documents=total_documents,
        categories=len(CATEGORIES),
        new_uploads=new_uploads,
        years_archive="50+",
        total_users=total_users,
        scanned_documents=scanned_documents,
        uploaded_documents=uploaded_documents
    )


# =========================================================
# API — CATEGORY BREAKDOWN (for the Categories popup)
# =========================================================

@app.route("/api/categories")
def api_categories():

    conn = get_db()

    rows = conn.execute(
        "SELECT category, COUNT(*) AS c FROM documents GROUP BY category"
    ).fetchall()

    conn.close()

    counts = {row["category"]: row["c"] for row in rows}

    data = [
        {"name": name, "count": counts.get(name, 0)}
        for name in CATEGORIES.keys()
    ]

    return jsonify(data)



# =========================================================
# ABHISHEK CHANGE
# Purpose:
# Preview documents in browser
# =========================================================


@app.route("/preview/<int:doc_id>")
def preview_document(doc_id):

    if not session.get("logged_in"):
        return redirect("/login")

    conn = get_db()

    doc = conn.execute(
        """
        SELECT *
        FROM documents
        WHERE id = ?
        """,
        (doc_id,)
    ).fetchone()

    conn.close()

    if not doc:
        return "Document not found"

    return send_file(
        doc["filepath"],
        as_attachment=False
    )

# =========================================================
# ABHISHEK CHANGE
# Purpose:
# Allow logged-in users to download uploaded documents
# =========================================================

@app.route("/download/<int:doc_id>")
def download_document(doc_id):
    

    # =====================================================
    # ABHISHEK CHANGE
    # Purpose:
    # Block downloads without login
    # =====================================================

    if not session.get("logged_in"):
        return redirect("/login")

    conn = get_db()

    # =====================================================
    # ABHISHEK CHANGE
    # Purpose:
    # Get document details from database
    # =====================================================

    doc = conn.execute(
        "SELECT * FROM documents WHERE id = ?",
        (doc_id,)
    ).fetchone()

    conn.close()

    # =====================================================
    # ABHISHEK CHANGE
    # Purpose:
    # Handle invalid document IDs
    # =====================================================

    if not doc:
        return "Document not found", 404

    # =====================================================
    # ABHISHEK CHANGE
    # Purpose:
    # Download the actual uploaded file
    # =====================================================

    return send_file(
        doc["filepath"],
        as_attachment=True,
        download_name=doc["filename"]
    )










# =========================================================
# ABHISHEK CHANGE
# Purpose:
# Allow admin users to delete documents
# =========================================================

@app.route("/delete/<int:doc_id>")
def delete_document(doc_id):

    # =====================================================
    # ABHISHEK CHANGE
    # Purpose:
    # Block access without login
    # =====================================================

    if not session.get("logged_in"):
        return redirect("/login")

    # =====================================================
    # ABHISHEK CHANGE
    # Purpose:
    # Allow only admin users
    # =====================================================

    if session.get("user_role") != "admin":
        return "Access Denied", 403

    conn = get_db()

    doc = conn.execute(
        "SELECT * FROM documents WHERE id = ?",
        (doc_id,)
    ).fetchone()

    if not doc:
        conn.close()
        return "Document not found", 404


    
    
    if not doc:
        conn.close()
        return "Document not found", 404

    # =====================================================
    # ABHISHEK CHANGE
    # Purpose:
    # Delete physical file from storage
    # =====================================================

    try:
        if os.path.exists(doc["filepath"]):
            os.remove(doc["filepath"])
    except Exception as e:
        print("File delete error:", e)

    # =====================================================
    # ABHISHEK CHANGE
    # Purpose:
    # Delete document record from database
    # =====================================================

    conn.execute(
        "DELETE FROM documents WHERE id = ?",
        (doc_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# =========================================================
# API — DOCUMENT LIST / SEARCH
# =========================================================

@app.route("/api/documents")
def api_documents():

    query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    date = request.args.get("date", "").strip()
    limit = request.args.get("limit", type=int) or 200

    sql = "SELECT * FROM documents WHERE 1=1"
    params = []

    if query:
        sql += " AND filename LIKE ?"
        params.append(f"%{query}%")

    if category and category != "All Categories":
        sql += " AND category = ?"
        params.append(category)

    if date:
        sql += " AND substr(uploaded_at, 1, 10) = ?"
        params.append(date)

    sql += " ORDER BY uploaded_at DESC LIMIT ?"
    params.append(limit)

    conn = get_db()
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    documents = [dict(row) for row in rows]

    return jsonify(documents)


# =========================================================
# API — RECENT ACTIVITY
# =========================================================

@app.route("/api/activity")
def api_activity():

    limit = request.args.get("limit", type=int) or 8

    conn = get_db()

    rows = conn.execute(
        "SELECT * FROM documents ORDER BY uploaded_at DESC LIMIT ?",
        (limit,)
    ).fetchall()

    conn.close()

    activity = []

    for row in rows:

        verb = "Scanned" if row["source"] == "scanner" else "Uploaded"

        activity.append({
    "user": row["uploaded_by"] or "Admin",
    "action": f"{verb} {row['filename']}",
    "category": row["category"],
    "date": row["uploaded_at"],
    "source": row["source"]
})

    return jsonify(activity)


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

# =========================================================
# START FLASK
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )