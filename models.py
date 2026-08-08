from extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username =db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False ,default="ACTIVE")
    staff_profile = db.relationship("StaffProfile", backref="user" ,uselist=False)

class StaffProfile(db.Model):
    id = db.Column(db.Integer , primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False,unique=True)
    contact = db.Column(db.String(20),nullable=False)
    experience = db.Column(db.Integer, default=0)
    approval_status = db.Column(db.String(20), default="Pending")
    assigned_treks = db.relationship("Trek" , backref = "assigned_staff", lazy=True)


class Trek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trek_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pending")
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("staff_profile.id"), nullable=True)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer , db.ForeignKey("user.id"), nullable=False)
    trek_id = db.Column(db.Integer , db.ForeignKey("trek.id"), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Booked")
    user = db.relationship("User", backref="bookings")
    trek = db.relationship("Trek", backref="bookings")