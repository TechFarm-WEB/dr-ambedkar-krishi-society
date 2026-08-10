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

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for
)

import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# =========================================================
# HOME / DASHBOARD
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# UPLOAD DOCUMENT
# =========================================================

@app.route("/upload", methods=["POST"])
def upload():

    # Get selected category
    category = request.form.get("category")

    # Get uploaded files
    files = request.files.getlist("file")


    # Available categories
    categories = {

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


    # Check category
    if not category:

        return """
        <script>
            alert("Please select a category.");
            window.history.back();
        </script>
        """


    # Check valid category
    if category not in categories:

        return "Invalid category selected.", 400


    # Create selected category folder
    category_folder = os.path.join(

        app.config["UPLOAD_FOLDER"],

        categories[category]
    )

    os.makedirs(
        category_folder,
        exist_ok=True
    )


    # Save files
    for file in files:

        if file and file.filename:

            file.save(

                os.path.join(

                    category_folder,

                    file.filename
                )
            )


    # Go back to dashboard
    return f"""
    <script>

        alert(
            "Files uploaded successfully to {category} category!"
        );

        window.location.href = "/";

    </script>
    """


# =========================================================
# OPEN CATEGORY
# =========================================================

@app.route("/category/<path:category>")
def show_category(category):

    categories = {

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


    # Check category
    if category not in categories:

        return "Category not found.", 404


    # Get category folder
    folder = os.path.join(

        app.config["UPLOAD_FOLDER"],

        categories[category]
    )


    # Make folder if it doesn't exist
    os.makedirs(
        folder,
        exist_ok=True
    )


    # Get files
    files = []

    for filename in os.listdir(folder):

        filepath = os.path.join(
            folder,
            filename
        )

        if os.path.isfile(filepath):

            files.append(filename)


    # Use SAME index.html
    return render_template(

        "index.html",

        selected_category=category,

        category_files=files
    )


# =========================================================
# START FLASK
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )