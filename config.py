import os

class Config:

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "change_this_secret_key"
    )

    SQLALCHEMY_DATABASE_URI = "sqlite:///bookings.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = "smtp.gmail.com"

    MAIL_PORT = 465

    MAIL_USE_SSL = True

    MAIL_USERNAME = os.getenv("EMAIL")
    MAIL_PASSWORD = os.getenv("PASSWORD")

    # Razorpay
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")