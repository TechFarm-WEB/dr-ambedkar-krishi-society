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

import os
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
# =========================================================
# ABHISHEK CHANGE
# Purpose:
# Enable Flask session management
# =========================================================

app.secret_key = "abhishek_auth_v1"

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
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db()

        user = conn.execute(
            """
            SELECT * FROM users
            WHERE email = ?
            AND password = ?
            """,
            (email, password)
        ).fetchone()

        conn.close()

        if user:

            session["logged_in"] = True
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_role"] = user["role"]

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
                password,
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
# UPLOAD DOCUMENT  (Upload New Document panel)
# =========================================================

@app.route("/upload", methods=["POST"])
def upload():

    category = request.form.get("category")
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

@app.route("/api/stats")
def api_stats():

    conn = get_db()

    total_documents = conn.execute(
        "SELECT COUNT(*) AS c FROM documents"
    ).fetchone()["c"]

    week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()

    new_uploads = conn.execute(
        "SELECT COUNT(*) AS c FROM documents WHERE uploaded_at >= ?",
        (week_ago,)
    ).fetchone()["c"]

    conn.close()

    return jsonify(
        total_documents=total_documents,
        categories=len(CATEGORIES),
        new_uploads=new_uploads,
        years_archive="50+"
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