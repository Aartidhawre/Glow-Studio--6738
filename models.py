from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# ==========================
# Booking Model
# ==========================

class Booking(db.Model):

    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        nullable=False
    )

    phone = db.Column(
        db.String(15),
        nullable=False
    )

    service = db.Column(
        db.String(100),
        nullable=False
    )

    booking_date = db.Column(
        db.String(30),
        nullable=False
    )

    message = db.Column(
        db.Text
    )

    # Booking Status
    status = db.Column(
        db.String(20),
        default="Pending"
    )

    # ==========================
    # Payment Details
    # ==========================

    payment_status = db.Column(
        db.String(20),
        default="Pending"
    )

    payment_id = db.Column(
        db.String(100)
    )

    order_id = db.Column(
        db.String(100)
    )

    payment_amount = db.Column(
        db.Integer,
        default=500
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):

        return f"<Booking {self.name}>"


# ==========================
# Admin Model
# ==========================

class Admin(db.Model):

    __tablename__ = "admin"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    def __repr__(self):

        return f"<Admin {self.username}>"


# ==========================
# Reviews
# ==========================

class Review(db.Model):

    __tablename__ = "reviews"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    client_name = db.Column(
        db.String(100),
        nullable=False
    )

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    review = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# ==========================
# Gallery
# ==========================

class Gallery(db.Model):

    __tablename__ = "gallery"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    image = db.Column(
        db.String(255),
        nullable=False
    )

    category = db.Column(
        db.String(50)
    )

    uploaded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )