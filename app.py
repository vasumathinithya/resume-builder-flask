
from flask import Flask, render_template, request, send_file, redirect, url_for
from backend.database import create_table, save_resume, get_resume
from backend.pdf_generator import generate_pdf
import os

app = Flask(__name__)

create_table()

OPTIONAL_FIELDS = [
    "summary",
    "education",
    "skills",
    "projects",
    "experience",
    "certifications",
    "achievements",
    "languages"
]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    # Mandatory fields
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()

    if not name or not email or not phone:
        return "Name, email and phone are required.", 400

    # Optional personal information
    data = {
        "name": name,
        "email": email,
        "phone": phone,
        "address": request.form.get("address", "").strip(),
        "linkedin": request.form.get("linkedin", "").strip(),
        "github": request.form.get("github", "").strip(),
    }

    # Store the content of all standard sections.
    # Only selected sections will appear in the PDF.
    for field in OPTIONAL_FIELDS:
        data[field] = request.form.get(field, "").strip()

    # Accept only recognized section names.
    selected = request.form.getlist("selected_sections")
    data["selected_sections"] = [
        section for section in selected
        if section in OPTIONAL_FIELDS
    ]

    # Read custom sections added by the user.
    titles = request.form.getlist("custom_title[]")
    contents = request.form.getlist("custom_content[]")

    custom_sections = []

    for title, content in zip(titles, contents):
        title = title.strip()
        content = content.strip()

        if title and content:
            custom_sections.append({
                "title": title,
                "content": content
            })

    data["custom_sections"] = custom_sections

    resume_id = save_resume(data)

    return redirect(url_for("preview", resume_id=resume_id))


@app.route("/preview/<int:resume_id>")
def preview(resume_id):
    resume = get_resume(resume_id)

    if resume is None:
        return "Resume not found.", 404

    return render_template("preview.html", resume=resume)


@app.route("/download/<int:resume_id>")
def download(resume_id):
    resume = get_resume(resume_id)

    if resume is None:
        return "Resume not found.", 404

    output_folder = os.path.join(app.root_path, "generated_pdfs")
    os.makedirs(output_folder, exist_ok=True)

    pdf_path = os.path.join(
        output_folder,
        f"resume_{resume_id}.pdf"
    )

    generate_pdf(resume, pdf_path)

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name="Professional_Resume.pdf"
    )


if __name__ == "__main__":
    app.run(debug=True)
