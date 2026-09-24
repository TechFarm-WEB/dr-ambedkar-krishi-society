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
    flash,

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
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime, timedelta
app = Flask(__name__)
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

# UPLOAD_FOLDER = "uploads"
# DATABASE = "documents.db"
UPLOAD_FOLDER = "uploads"

DATABASE_URL = os.getenv("DATABASE_URL")

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

# def get_db():
#     conn = sqlite3.connect(DATABASE)
#     conn.row_factory = sqlite3.Row
#     return conn

class PostgresConnection:

    def __init__(self):

        if not DATABASE_URL:
            raise RuntimeError(
                "DATABASE_URL environment variable is not set"
            )

        self.conn = psycopg2.connect(
            DATABASE_URL
        )

    def execute(self, sql, params=None):

        # SQLite placeholders -> PostgreSQL placeholders
        sql = sql.replace("?", "%s")

        cursor = self.conn.cursor(
            cursor_factory=DictCursor
        )

        cursor.execute(
            sql,
            params or ()
        )

        return cursor

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()


def get_db():
    return PostgresConnection()


# def init_db():
#     conn = get_db()

#     conn.execute("""
#         CREATE TABLE IF NOT EXISTS documents (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             filename TEXT NOT NULL,
#             category TEXT NOT NULL,
#             source TEXT NOT NULL DEFAULT 'upload',
#             filepath TEXT NOT NULL,
#             filesize INTEGER DEFAULT 0,
#             uploaded_by TEXT,
#             document_date TEXT,
#             uploaded_at TEXT NOT NULL
#         )
#     """)

#     try:
#         conn.execute(
#             "ALTER TABLE documents ADD COLUMN uploaded_by TEXT"
#         )
#     except:
#         pass

#     try:
#         conn.execute(
#             "ALTER TABLE documents ADD COLUMN document_date TEXT"
#         )
#     except:
#         pass

#     conn.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             mobile TEXT UNIQUE,
#             email TEXT UNIQUE NOT NULL,
#             address TEXT,
#             fav_place TEXT,
#             password TEXT NOT NULL,
#             role TEXT DEFAULT 'user',
#             last_login TEXT
#         )
#     """)

#     conn.commit()
#     conn.close()

def init_db():

    conn = get_db()

    # =====================================================
    # DOCUMENTS TABLE
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
            filename TEXT NOT NULL,
            category TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT 'upload',
            filepath TEXT NOT NULL,
            filesize INTEGER DEFAULT 0,
            uploaded_by TEXT,
            document_date TEXT,
            uploaded_at TEXT NOT NULL
        )
    """)


    # =====================================================
    # USERS TABLE
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
            name TEXT NOT NULL,
            mobile TEXT UNIQUE,
            email TEXT UNIQUE NOT NULL,
            address TEXT,
            fav_place TEXT,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            last_login TEXT
        )
    """)


    # =====================================================
    # CATEGORIES TABLE
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
            category_name TEXT UNIQUE NOT NULL,
            icon TEXT DEFAULT 'fa-folder',
            is_default INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


# try:
#     conn.execute(
#         """
#         ALTER TABLE users
#         ADD COLUMN last_login TEXT
#         """
#     )
# except:
#     pass
    



    # =====================================================
# ABHISHEK CHANGE
# Purpose:
# Store user's last successful login timestamp
# =====================================================


  


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
    uploaded_by=None,
    document_date=None
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
                document_date,
                uploaded_at
            )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            filename,
            category,
            source,
            filepath,
            filesize,
            uploaded_by,
            document_date,
            ist_timestamp
        )
    )

    conn.commit()
    conn.close()

# init_db()


# conn = get_db()

# conn.execute("""
# CREATE TABLE IF NOT EXISTS categories (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     category_name TEXT UNIQUE NOT NULL,
#     icon TEXT DEFAULT 'fa-folder',
#     is_default INTEGER DEFAULT 0
# )
# """)

# default_categories = [
#     "Audit",
#     "Revenue",
#     "Court Matter",
#     "Membership Details",
#     "Police Department",
#     "Dispute",
#     "Committee Proceedings",
#     "Samiti Records",
#     "Others",
#     "Official Letters"
# ]

# for category in default_categories:

#     conn.execute(
#         """
#         INSERT OR IGNORE INTO categories
#         (
#             category_name,
#             is_default
#         )
#         VALUES
#         (?, 1)
#         """,
#         (category,)
#     )

#     conn.execute("""
# UPDATE categories
# SET is_default = 1
# WHERE category_name IN (
#     'Audit',
#     'Revenue',
#     'Court Matter',
#     'Membership Details',
#     'Police Department',
#     'Dispute',
#     'Committee Proceedings',
#     'Samiti Records',
#     'Others',
#     'Official Letters'
# )
# """)

# conn.commit()
# conn.close()


init_db()


# =====================================================
# DEFAULT CATEGORIES
# PostgreSQL
# =====================================================

conn = get_db()

default_categories = [
    "Audit",
    "Revenue",
    "Court Matter",
    "Membership Details",
    "Police Department",
    "Dispute",
    "Committee Proceedings",
    "Samiti Records",
    "Others",
    "Official Letters"
]


for category in default_categories:

    conn.execute(
        """
        INSERT INTO categories
        (
            category_name,
            is_default
        )
        VALUES
        (?, 1)

        ON CONFLICT (category_name)
        DO NOTHING
        """,
        (category,)
    )


conn.execute(
    """
    UPDATE categories
    SET is_default = 1
    WHERE category_name IN (
        'Audit',
        'Revenue',
        'Court Matter',
        'Membership Details',
        'Police Department',
        'Dispute',
        'Committee Proceedings',
        'Samiti Records',
        'Others',
        'Official Letters'
    )
    """
)


conn.commit()
conn.close()
# =====================================================
# ABHISHEK CHANGE
# Purpose:
# Create default admin user if not exists
# =====================================================

# conn = get_db()

# conn.execute("""
# INSERT OR IGNORE INTO users
# (name, email, password, role)
# VALUES
# ('Admin', 'admin@neudocl.com', 'admin123', 'admin')
# """)

# conn.commit()
# conn.close()

# conn = get_db()

# admin_password = generate_password_hash("Sunil@123")

# conn.execute(
#     """
#     INSERT OR IGNORE INTO users
#     (name, email, password, role)
#     VALUES (?, ?, ?, ?)
#     """,
#     (
#         "Sunil Choudhary",
#         "sunil@neudocl.com",
#         admin_password,
#         "admin"
#     )
# )

# conn.commit()
# conn.close()

conn = get_db()

admin_password = generate_password_hash("Sunil@123")

conn.execute(
    """
    INSERT INTO users
    (
        name,
        email,
        password,
        role
    )
    VALUES
    (
        ?, ?, ?, ?
    )

    ON CONFLICT (email)
    DO NOTHING
    """,
    (
        "Sunil Choudhary",
        "sunil@neudocl.com",
        admin_password,
        "admin"
    )
)

conn.commit()
conn.close()




# conn.execute("""
# UPDATE users
# SET
# name = 'Sunil Choudhary',
# email = 'choudharysuneel@gmail.com',
# password = 'Sunil@123'
# WHERE role = 'admin'
# """)

# conn.commit()
# conn.close()





# =========================================================
# HOME / DASHBOARD
# =========================================================


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

    conn = get_db()

    rows = conn.execute(
        """
        SELECT category_name
        FROM categories
        ORDER BY category_name
        """
    ).fetchall()

    conn.close()

    categories = {}

    for row in rows:

        categories[
            row["category_name"]
        ] = row["category_name"]

    return render_template(
        "index.html",
        categories=categories,
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
    files = request.files.getlist("file")
    document_date = request.form.get(
    "document_date"
)

    if not category:
        return jsonify(
            success=False,
            message="Please select a category."
        ), 400

    conn = get_db()

    valid_category = conn.execute(
        """
        SELECT *
        FROM categories
        WHERE category_name = ?
        """,
        (category,)
    ).fetchone()

    conn.close()

    if not valid_category:
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
    secure_filename(category)
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

        filesize = os.path.getsize(destination)

        record_document(
    filename=filename,
    category=category,
    source="upload",
    filepath=destination,
    filesize=filesize,
    uploaded_by=session.get("user_name"),
    document_date=document_date
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

    filesize = os.path.getsize(destination)

    record_document(
        filename=filename,
        category=category,
        source="scanner",
        filepath=destination,
        filesize=filesize
    )

    return jsonify(
        success=True,
        message=f"Scanned document saved to {category}.",
        category=category,
        filename=filename
    )


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


# =========================================================
# API — DASHBOARD STATISTICS
# =========================================================

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
    total_categories = conn.execute(
    "SELECT COUNT(*) AS c FROM categories"
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
        # categories=len(CATEGORIES),
        categories=total_categories,
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

    # if date:
    #     sql += " AND substr(uploaded_at, 1, 10) = ?"
    #     params.append(date)
    if date:
        sql += " AND LEFT(uploaded_at, 10) = ?"
        params.append(date)

    sql += " ORDER BY uploaded_at DESC LIMIT ?"
    params.append(limit)

    conn = get_db()
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    documents = [dict(row) for row in rows]

    return jsonify(documents)


# @app.route("/api/archive")
# def api_archive():

#     query = request.args.get(
#         "q",
#         ""
#     ).strip()
#     archive_type = request.args.get(
#     "type",
#     "historical"
#     )

#     conn = get_db()

#     sql = """
#     SELECT
#         id,
#         filename,
#         category,
#         document_date,
#         uploaded_at
#     FROM documents
#     WHERE document_date IS NOT NULL
#     AND document_date != ''
#     AND document_date <= '2000-12-31'
#     """

#     params = []

#     if query:

#         sql += """
#         WHERE filename LIKE ?
#         """

#         params.append(
#             f"%{query}%"
#         )
    
#     sql += """
#   ORDER BY
#     COALESCE(
#         document_date,
#         substr(uploaded_at,1,10)
#     ) ASC
#     """

#     rows = conn.execute(
#         sql,
#         params
#     ).fetchall()

#     conn.close()

#     return jsonify([
#         dict(row)
#         for row in rows
#     ])


@app.route("/api/archive")
def api_archive():

    query = request.args.get(
        "q",
        ""
    ).strip()

    archive_type = request.args.get(
        "type",
        "historical"
    )

    conn = get_db()

    sql = """
        SELECT
            id,
            filename,
            category,
            document_date,
            uploaded_at
        FROM documents
        WHERE document_date IS NOT NULL
        AND document_date != ''
        AND document_date <= '2000-12-31'
    """

    params = []

    if query:

        sql += """
            AND filename LIKE ?
        """

        params.append(
            f"%{query}%"
        )

    sql += """
        ORDER BY
            COALESCE(
                document_date,
                LEFT(uploaded_at, 10)
            ) ASC
    """

    rows = conn.execute(
        sql,
        params
    ).fetchall()

    conn.close()

    return jsonify([
        dict(row)
        for row in rows
    ])
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

@app.route("/test-categories")
def test_categories():

    conn = get_db()

    rows = conn.execute(
        """
        SELECT *
        FROM categories
        ORDER BY category_name
        """
    ).fetchall()

    conn.close()

    return jsonify([
        dict(row)
        for row in rows
    ])

@app.route("/api/category/create", methods=["POST"])
def create_category():

    data = request.get_json()

    category_name = (
        data.get("category", "")
        .strip()
    )

    if not category_name:

        return jsonify({
            "success": False,
            "message": "Category name required"
        })

    conn = get_db()

    existing = conn.execute(
        """
        SELECT *
        FROM categories
        WHERE category_name = ?
        """,
        (category_name,)
    ).fetchone()

    if existing:

        conn.close()

        return jsonify({
            "success": False,
            "message": "Category already exists"
        })

    conn.execute(
        """
        INSERT INTO categories
        (
            category_name
        )
        VALUES
        (?)
        """,
        (category_name,)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Category created successfully"
    })

@app.route("/api/category/delete", methods=["POST"])
def delete_category():

    data = request.get_json()

    category_name = data.get(
        "category",
        ""
    ).strip()

    if not category_name:

        return jsonify({
            "success": False,
            "message": "Category name required"
        })

    conn = get_db()

    category = conn.execute(
        """
        SELECT *
        FROM categories
        WHERE category_name = ?
        """,
        (category_name,)
    ).fetchone()

    if not category:

        conn.close()

        return jsonify({
            "success": False,
            "message": "Category not found"
        })

    if category["is_default"] == 1:

        conn.close()

        return jsonify({
            "success": False,
            "message": "Default categories cannot be deleted"
        })

   # Delete all document records

    conn.execute(
        """
        DELETE FROM documents
        WHERE category = ?
        """,
        (category_name,)
    )

    category_folder = os.path.join(
        app.config["UPLOAD_FOLDER"],
        secure_filename(category_name)
    )

    if os.path.exists(category_folder):

        import shutil

        shutil.rmtree(category_folder)

    conn.execute(
        """
        DELETE FROM categories
        WHERE category_name = ?
        """,
        (category_name,)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Category deleted successfully"
    })

# =========================================================
# START FLASK
# =========================================================

@app.route("/create-user", methods=["POST"])
def create_user():

    name = request.form["name"]
    email = request.form["email"]
    mobile = request.form["mobile"]
    password = request.form["password"]
    role = request.form["role"]

    password_hash = generate_password_hash(
        password
    )

    conn = get_db()

    existing = conn.execute(
        """
        SELECT *
        FROM users
        WHERE email = ?
        OR mobile = ?
        """,
        (
            email,
            mobile
        )
    ).fetchone()

    if existing:

        conn.close()

        flash(
            "User with this email or mobile already exists",
            "error"
        )

        return redirect("/users")

    conn.execute(
        """
        INSERT INTO users
        (
            name,
            email,
            mobile,
            password,
            role
        )
        VALUES
        (
            ?, ?, ?, ?, ?
        )
        """,
        (
            name,
            email,
            mobile,
            password_hash,
            role
        )
    )

    conn.commit()
    conn.close()

    flash(
        "User created successfully",
        "success"
    )

    return redirect("/users")


@app.route("/test-documents")
def test_documents():

    conn = get_db()

    rows = conn.execute(
        """
        SELECT
            filename,
            category,
            document_date,
            uploaded_at
        FROM documents
        ORDER BY id DESC
        LIMIT 20
        """
    ).fetchall()

    conn.close()

    return jsonify([
        dict(row)
        for row in rows
    ])

if __name__ == "__main__":

    app.run(
        debug=True
    )