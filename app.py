from collections import Counter
from werkzeug.utils import secure_filename

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    flash,
    session,
    send_file,
    jsonify
)

from config import Config
from models import db, Booking, Admin, Review, Gallery

from sqlalchemy import or_, text

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from dotenv import load_dotenv
from email.message import EmailMessage
from datetime import datetime

import smtplib
import ssl
import os
from reportlab.pdfgen import canvas
import io
import razorpay


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")


client = razorpay.Client(
    auth=(
        RAZORPAY_KEY_ID,
        RAZORPAY_KEY_SECRET
    )
)


print("========== RAZORPAY CHECK ==========")
print("KEY:", RAZORPAY_KEY_ID)
print(
    "SECRET FOUND:",
    bool(RAZORPAY_KEY_SECRET)
)
print(
    "SECRET LENGTH:",
    len(RAZORPAY_KEY_SECRET)
    if RAZORPAY_KEY_SECRET
    else 0
)
print("====================================")


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

app.config.from_object(Config)

app.config["SECRET_KEY"] = Config.SECRET_KEY

db.init_app(app)


# =========================================================
# UPLOAD FOLDER
# =========================================================

UPLOAD_FOLDER = "static/images"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# =========================================================
# DATABASE
# =========================================================

with app.app_context():

    db.create_all()

    # -----------------------------------------------------
    # Existing bookings.db me payment columns add karna
    # -----------------------------------------------------

    try:

        existing_columns = {
            row[1]
            for row in db.session.execute(
                text("PRAGMA table_info(bookings)")
            ).fetchall()
        }

        new_columns = {

            "payment_status":
                "VARCHAR(20) DEFAULT 'Pending'",

            "payment_id":
                "VARCHAR(100)",

            "order_id":
                "VARCHAR(100)",

            "payment_amount":
                "INTEGER DEFAULT 500"
        }

        for column_name, column_definition in new_columns.items():

            if column_name not in existing_columns:

                db.session.execute(
                    text(
                        f"ALTER TABLE bookings ADD COLUMN "
                        f"{column_name} {column_definition}"
                    )
                )

        db.session.commit()

        print("Payment database columns checked successfully.")

    except Exception as e:

        db.session.rollback()

        print(
            "Database migration error:",
            e
        )


# =========================================================
# DEMO GALLERY / REVIEWS
# =========================================================

with app.app_context():

    if Gallery.query.count() == 0:

        db.session.add(
            Gallery(
                image="gallery1.jpg",
                category="Bridal"
            )
        )

        db.session.add(
            Gallery(
                image="gallery2.jpg",
                category="HD"
            )
        )

        db.session.add(
            Gallery(
                image="gallery3.jpg",
                category="Party"
            )
        )

        db.session.commit()


    if Review.query.count() == 0:

        db.session.add(
            Review(
                client_name="Priya Sharma",
                rating=5,
                review="Amazing bridal makeup. Highly recommended!"
            )
        )

        db.session.add(
            Review(
                client_name="Neha Verma",
                rating=5,
                review="Very professional and beautiful work."
            )
        )

        db.session.add(
            Review(
                client_name="Anjali Singh",
                rating=4,
                review="Excellent service and friendly nature."
            )
        )

        db.session.commit()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    reviews = Review.query.all()

    gallery = Gallery.query.all()

    return render_template(
        "index.html",
        reviews=reviews,
        gallery=gallery
    )


# =========================================================
# BOOKING
# =========================================================

@app.route("/contact", methods=["POST"])
def contact():

    booking = Booking(

        name=request.form["name"],

        email=request.form["email"],

        phone=request.form["phone"],

        service=request.form["service"],

        booking_date=request.form["date"],

        message=request.form["message"]

    )

    db.session.add(booking)

    db.session.commit()


    # -----------------------------------------------------
    # Email settings
    # -----------------------------------------------------

    email = os.getenv("EMAIL")

    password = os.getenv("PASSWORD")

    context = ssl.create_default_context()


    print("EMAIL:", email)

    print(
        "PASSWORD FOUND:",
        password is not None
    )

    print(
        "CUSTOMER EMAIL:",
        booking.email
    )


    try:

        # =================================================
        # ADMIN EMAIL
        # =================================================

        msg = EmailMessage()

        msg["Subject"] = "New Makeup Booking"

        msg["From"] = email

        msg["To"] = email

        msg.set_content(
            f"""
New Booking Received

Customer Name : {booking.name}

Phone : {booking.phone}

Email : {booking.email}

Service : {booking.service}

Appointment Date : {booking.booking_date}

Message :

{booking.message}
"""
        )


        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465,
            context=context
        ) as smtp:

            smtp.login(
                email,
                password
            )

            smtp.send_message(msg)


        # =================================================
        # CUSTOMER EMAIL
        # =================================================

        customer = EmailMessage()

        customer["Subject"] = "Booking Confirmation"

        customer["From"] = email

        customer["To"] = booking.email

        customer.set_content(
            f"""
Hello {booking.name},

Thank you for booking with
Radhika Malviya Makeup Studio.

Your booking request has been received.

Service:
{booking.service}

Appointment Date:
{booking.booking_date}

We will contact you shortly.

Thank You ❤️

Radhika Malviya Makeup Studio
"""
        )


        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465,
            context=context
        ) as smtp:

            smtp.login(
                email,
                password
            )

            smtp.send_message(customer)


    except Exception as e:

        print(
            "Email Error:",
            e
        )


    flash(
        "Booking Submitted Successfully",
        "success"
    )

    return redirect("/")


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]


        admin = Admin.query.filter_by(
            username=username
        ).first()


        if admin and check_password_hash(
            admin.password,
            password
        ):

            session["admin"] = admin.username

            return redirect("/dashboard")


        flash(
            "Invalid Login",
            "danger"
        )


    return render_template(
        "login.html"
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "admin" not in session:

        return redirect("/login")


    search = request.args.get(
        "search",
        ""
    )


    if search:

        bookings = Booking.query.filter(

            or_(

                Booking.name.ilike(
                    f"%{search}%"
                ),

                Booking.phone.ilike(
                    f"%{search}%"
                ),

                Booking.service.ilike(
                    f"%{search}%"
                )

            )

        ).order_by(
            Booking.created_at.desc()
        ).all()


    else:

        bookings = Booking.query.order_by(
            Booking.created_at.desc()
        ).all()


    total = Booking.query.count()

    pending = Booking.query.filter_by(
        status="Pending"
    ).count()

    confirmed = Booking.query.filter_by(
        status="Confirmed"
    ).count()

    completed = Booking.query.filter_by(
        status="Completed"
    ).count()

    cancelled = Booking.query.filter_by(
        status="Cancelled"
    ).count()


    # =====================================================
    # CALENDAR
    # =====================================================

    calendar_events = []


    for booking in bookings:

        calendar_events.append(

            {
                "title": booking.service,

                "start": str(
                    booking.booking_date
                )
            }

        )


    # =====================================================
    # MONTHLY CHART
    # =====================================================

    month_counter = Counter()


    for booking in Booking.query.all():

        try:

            month = datetime.strptime(
                str(booking.booking_date),
                "%Y-%m-%d"
            ).strftime("%b")


            month_counter[month] += 1


        except:

            pass


    months = [

        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec"

    ]


    monthly_data = [

        month_counter.get(
            month,
            0
        )

        for month in months

    ]


    return render_template(

        "dashboard.html",

        bookings=bookings,

        total=total,

        pending=pending,

        confirmed=confirmed,

        completed=completed,

        cancelled=cancelled,

        search=search,

        calendar_events=calendar_events,

        monthly_data=monthly_data

    )


# =========================================================
# UPDATE BOOKING STATUS
# =========================================================

@app.route(
    "/status/<int:id>",
    methods=["POST"]
)
def update_status(id):

    if "admin" not in session:

        return redirect("/login")


    booking = Booking.query.get_or_404(id)


    booking.status = request.form["status"]


    db.session.commit()


    # =====================================================
    # STATUS EMAIL
    # =====================================================

    email = os.getenv("EMAIL")

    password = os.getenv("PASSWORD")

    context = ssl.create_default_context()


    try:

        customer = EmailMessage()

        customer["Subject"] = (
            f"Booking {booking.status}"
        )

        customer["From"] = email

        customer["To"] = booking.email


        customer.set_content(

            f"""
Hello {booking.name},

Your booking status has been updated.

Service:
{booking.service}

Appointment Date:
{booking.booking_date}

Current Status:
{booking.status}

Thank you for choosing
Radhika Malviya Makeup Studio.

Regards,
Radhika Malviya Makeup Studio
"""

        )


        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465,
            context=context
        ) as smtp:

            smtp.login(
                email,
                password
            )

            smtp.send_message(
                customer
            )


        print(
            "Status email sent successfully."
        )


    except Exception as e:

        print(
            "Status Email Error:",
            e
        )


    flash(
        "Booking Status Updated Successfully",
        "success"
    )


    return redirect(
        "/dashboard"
    )


# =========================================================
# DELETE BOOKING
# =========================================================

@app.route(
    "/delete/<int:id>"
)
def delete_booking(id):

    if "admin" not in session:

        return redirect("/login")


    booking = Booking.query.get_or_404(id)


    db.session.delete(
        booking
    )

    db.session.commit()


    flash(
        "Booking Deleted Successfully",
        "success"
    )


    return redirect(
        "/dashboard"
    )


# =========================================================
# PDF RECEIPT
# =========================================================

@app.route(
    "/receipt/<int:id>"
)
def receipt(id):

    if "admin" not in session:

        return redirect("/login")


    booking = Booking.query.get_or_404(id)


    pdf = io.BytesIO()


    c = canvas.Canvas(
        pdf
    )


    # =====================================================
    # HEADER
    # =====================================================

    c.setFont(
        "Helvetica-Bold",
        18
    )


    c.drawString(
        150,
        800,
        "Radhika Makeup Studio"
    )


    c.setFont(
        "Helvetica",
        12
    )


    # =====================================================
    # BOOKING DETAILS
    # =====================================================

    c.drawString(
        100,
        750,
        f"Name : {booking.name}"
    )


    c.drawString(
        100,
        720,
        f"Service : {booking.service}"
    )


    c.drawString(
        100,
        690,
        f"Date : {booking.booking_date}"
    )


    c.drawString(
        100,
        660,
        f"Phone : {booking.phone}"
    )


    c.drawString(
        100,
        630,
        f"Booking Status : {booking.status}"
    )


    # =====================================================
    # PAYMENT DETAILS
    # =====================================================

    payment_status = (
        booking.payment_status
        if booking.payment_status
        else "Pending"
    )


    payment_amount = (
        booking.payment_amount
        if booking.payment_amount
        else 500
    )


    c.drawString(
        100,
        590,
        f"Payment Status : {payment_status}"
    )


    c.drawString(
        100,
        560,
        f"Amount : Rs. {payment_amount}"
    )


    c.drawString(
        100,
        530,
        f"Payment ID : "
        f"{booking.payment_id or 'Not Available'}"
    )


    c.drawString(
        100,
        500,
        f"Order ID : "
        f"{booking.order_id or 'Not Available'}"
    )


    # =====================================================
    # FOOTER
    # =====================================================

    c.setFont(
        "Helvetica",
        10
    )


    c.drawString(
        100,
        450,
        "Thank you for choosing Radhika Makeup Studio."
    )


    c.save()


    pdf.seek(0)


    return send_file(

        pdf,

        download_name="booking_receipt.pdf",

        as_attachment=True

    )


# =========================================================
# RAZORPAY CLIENT PAYMENT
# =========================================================

@app.route(
    "/pay/<int:id>"
)
def pay(id):

    # IMPORTANT:
    # Yahan admin login required nahi hai.
    # Client bhi is link ko open kar sakta hai.

    booking = Booking.query.get_or_404(id)


    # -----------------------------------------------------
    # Agar payment already ho chuki hai
    # -----------------------------------------------------

    if booking.payment_status == "Paid":

        return render_template(
            "payment.html",
            booking=booking,
            already_paid=True,
            order=None,
            razorpay_key=RAZORPAY_KEY_ID,
            amount=(
                booking.payment_amount * 100
                if booking.payment_amount
                else 50000
            )
        )


    # -----------------------------------------------------
    # Amount
    # ₹500 = 50000 paise
    # -----------------------------------------------------

    amount = 50000


    try:

        print(
            "Creating Razorpay order..."
        )

        print(
            "RAZORPAY KEY:",
            RAZORPAY_KEY_ID
        )

        print(
            "RAZORPAY SECRET FOUND:",
            bool(RAZORPAY_KEY_SECRET)
        )


        order = client.order.create(

            {
                "amount": amount,

                "currency": "INR",

                "receipt":
                    f"booking_{booking.id}"
            }

        )


        # -------------------------------------------------
        # Order ID database me save
        # -------------------------------------------------

        booking.order_id = order["id"]

        booking.payment_amount = 500

        booking.payment_status = "Pending"

        db.session.commit()


        return render_template(

            "payment.html",

            booking=booking,

            order=order,

            razorpay_key=RAZORPAY_KEY_ID,

            amount=amount,

            already_paid=False

        )


    except Exception as e:

        print(
            "Razorpay Error:",
            e
        )


        return """

        <h2>Payment Setup Error</h2>

        <p>Razorpay payment setup me problem aa gayi.</p>

        <p>Please try again later.</p>

        """

# =========================================================
# SEND PAYMENT LINK BY EMAIL
# =========================================================

@app.route("/send-payment-email/<int:id>", methods=["POST"])
def send_payment_email(id):

    # Admin login check
    if "admin" not in session:
        return redirect("/login")

    booking = Booking.query.get_or_404(id)

    # =====================================================
    # PAYMENT LINK
    # =====================================================

    payment_link = (
        request.url_root.rstrip("/")
        + f"/pay/{booking.id}"
    )

    # =====================================================
    # EMAIL SETTINGS
    # =====================================================

    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    context = ssl.create_default_context()

    # =====================================================
    # CUSTOMER EMAIL
    # =====================================================

    customer = EmailMessage()

    customer["Subject"] = (
        "Payment Link - Radhika Makeup Studio"
    )

    customer["From"] = email

    customer["To"] = booking.email

    customer.set_content(
        f"""
Hello {booking.name},

Your {booking.service} booking with
Radhika Makeup Studio is confirmed.

Please complete your booking payment
using the link below:

{payment_link}

Payment Amount: ₹500

Thank you,
Radhika Makeup Studio
"""
    )

    try:

        # Gmail SMTP
        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465,
            context=context
        ) as smtp:

            smtp.login(
                email,
                password
            )

            smtp.send_message(
                customer
            )

        print(
            "Payment link email sent successfully."
        )

        flash(
            "Payment link email sent successfully.",
            "success"
        )

    except Exception as e:

        print(
            "Payment Email Error:",
            e
        )

        flash(
            "Payment email send nahi hua.",
            "danger"
        )

    return redirect("/dashboard")
# =========================================================
# RAZORPAY PAYMENT SUCCESS / VERIFICATION
# =========================================================

@app.route(
    "/payment-success",
    methods=["POST"]
)
def payment_success():

    try:

        data = request.get_json()


        if not data:

            return jsonify(

                {
                    "success": False,

                    "message":
                        "Payment data missing."
                }

            ), 400


        booking_id = data.get(
            "booking_id"
        )


        payment_id = data.get(
            "razorpay_payment_id"
        )


        order_id = data.get(
            "razorpay_order_id"
        )


        signature = data.get(
            "razorpay_signature"
        )


        if not all(
            [
                booking_id,
                payment_id,
                order_id,
                signature
            ]
        ):

            return jsonify(

                {
                    "success": False,

                    "message":
                        "Payment details incomplete."
                }

            ), 400


        booking = Booking.query.get_or_404(
            int(booking_id)
        )


        # =================================================
        # SECURITY:
        # Razorpay signature verify
        # =================================================

        verification_data = {

            "razorpay_order_id":
                order_id,

            "razorpay_payment_id":
                payment_id,

            "razorpay_signature":
                signature

        }


        client.utility.verify_payment_signature(
            verification_data
        )


        # =================================================
        # SAVE PAYMENT DETAILS
        # =================================================

        booking.payment_status = "Paid"

        booking.payment_id = payment_id

        booking.order_id = order_id

        booking.payment_amount = 500


        db.session.commit()


        print(
            "Payment verified successfully."
        )

        print(
            "Booking ID:",
            booking.id
        )

        print(
            "Payment ID:",
            payment_id
        )

        print(
            "Order ID:",
            order_id
        )


        return jsonify(

            {
                "success": True,

                "message":
                    "Payment verified successfully.",

                "redirect":
                    f"/payment-success/{booking.id}"
            }

        )


    except Exception as e:

        print(
            "Payment Verification Error:",
            e
        )


        return jsonify(

            {
                "success": False,

                "message":
                    "Payment verification failed."
            }

        ), 400


# =========================================================
# PAYMENT SUCCESS PAGE
# =========================================================

@app.route(
    "/payment-success/<int:id>"
)
def payment_success_page(id):

    booking = Booking.query.get_or_404(id)


    return render_template(

        "payment_success.html",

        booking=booking

    )


# =========================================================
# LOGOUT
# =========================================================

@app.route(
    "/logout"
)
def logout():

    session.clear()


    flash(
        "Logged Out Successfully",
        "success"
    )


    return redirect(
        "/login"
    )


# =========================================================
# GALLERY
# =========================================================

@app.route(
    "/gallery",
    methods=["GET", "POST"]
)
def gallery_upload():

    if "admin" not in session:

        return redirect("/login")


    if request.method == "POST":

        image = request.files["image"]

        category = request.form["category"]


        if image:

            filename = secure_filename(
                image.filename
            )


            image.save(

                os.path.join(

                    app.config[
                        "UPLOAD_FOLDER"
                    ],

                    filename

                )

            )


            new_image = Gallery(

                image=filename,

                category=category

            )


            db.session.add(
                new_image
            )

            db.session.commit()


            flash(
                "Image Uploaded Successfully",
                "success"
            )


            return redirect(
                "/gallery"
            )


    images = Gallery.query.all()


    return render_template(

        "gallery.html",

        images=images

    )


# =========================================================
# DELETE GALLERY IMAGE
# =========================================================

@app.route(
    "/delete-image/<int:id>"
)
def delete_image(id):

    if "admin" not in session:

        return redirect("/login")


    image = Gallery.query.get_or_404(id)


    image_path = os.path.join(

        app.config[
            "UPLOAD_FOLDER"
        ],

        image.image

    )


    if os.path.exists(
        image_path
    ):

        os.remove(
            image_path
        )


    db.session.delete(
        image
    )

    db.session.commit()


    flash(
        "Image Deleted Successfully",
        "success"
    )


    return redirect(
        "/gallery"
    )


# =========================================================
# REVIEWS
# =========================================================

@app.route(
    "/reviews",
    methods=["GET", "POST"]
)
def reviews():

    if "admin" not in session:

        return redirect("/login")


    if request.method == "POST":

        new_review = Review(

            client_name=
                request.form[
                    "client_name"
                ],

            rating=int(
                request.form[
                    "rating"
                ]
            ),

            review=
                request.form[
                    "review"
                ]

        )


        db.session.add(
            new_review
        )

        db.session.commit()


        flash(
            "Review Added Successfully",
            "success"
        )


        return redirect(
            "/reviews"
        )


    reviews = Review.query.order_by(

        Review.created_at.desc()

    ).all()


    return render_template(

        "reviews.html",

        reviews=reviews

    )


# =========================================================
# DELETE REVIEW
# =========================================================

@app.route(
    "/delete-review/<int:id>"
)
def delete_review(id):

    if "admin" not in session:

        return redirect("/login")


    review = Review.query.get_or_404(id)


    db.session.delete(
        review
    )

    db.session.commit()


    flash(
        "Review Deleted Successfully",
        "success"
    )


    return redirect(
        "/reviews"
    )


# =========================================================
# CREATE DEFAULT ADMIN
# =========================================================

@app.before_request
def create_default_admin():

    admin = Admin.query.filter_by(

        username="admin"

    ).first()


    if not admin:

        admin = Admin(

            username="admin",

            password=
                generate_password_hash(
                    "admin123"
                )

        )


        db.session.add(
            admin
        )

        db.session.commit()


# =========================================================
# 404
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "404.html"
    ), 404


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )