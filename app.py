from flask import Flask, flash,render_template,request,session,redirect
from extensions import db
from config import Config
from models import User,Trek,StaffProfile,Booking   
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from datetime import date

app= Flask(__name__)
app.secret_key = "my_super_secret_key"

app.config.from_object(Config)

db.init_app(app)

#home route
@app.route("/")
def home():
    return render_template("home.html")


#about route
@app.route("/about")
def about():
    return render_template("about.html")

#register route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    role= request.form.get("role")
    contact= request.form.get("contact")
    experience= request.form.get("experience")

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return "Email already registered!"

    hashed_password = generate_password_hash(password)

    user = User(username=username , email=email, password=hashed_password,role=role,status="ACTIVE")

    db.session.add(user)
    db.session.commit()

    if role == "Staff":

        staff = StaffProfile(user_id=user.id, contact=contact, experience=experience, approval_status="Pending")

        db.session.add(staff)
        db.session.commit()

        return "Staff Registration Submitted! Wait for Admin Approval."

    return "User Registered Successfully!"

#login route
@app.route("/login", methods=["GET", "POST"])

def login():
    if request.method == "GET":
        return render_template("login.html")

    email =request.form.get("email")
    password =request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        session["user_id"] = user.id
        session["role"] = user.role

        if user.role == "Admin":
            return redirect("/admin_dashboard")

        elif user.role == "Staff":
            return redirect("/staff_dashboard")

        else:
            return redirect("/trekker_dashboard")

    return "Invalid email or password!"
    
@app.route("/admin_dashboard")
def admin_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Admin":
        return "Access Denied!"

    total_users = User.query.count()

    total_treks = Trek.query.count()

    total_bookings = Booking.query.count()

    total_staff = StaffProfile.query.filter_by(
        approval_status="Approved"
    ).count()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_treks=total_treks,
        total_bookings=total_bookings,
        total_staff=total_staff
    )
#staff dashboard route

@app.route("/staff_dashboard")
def staff_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Staff":
        return "Access Denied!"
    staff = StaffProfile.query.filter_by(user_id=session["user_id"]).first()

    if staff.approval_status != "Approved":
        return "Your account is not approved yet."

    assigned_treks= Trek.query.filter_by(assigned_staff_id=staff.id).all()

    return render_template(
        "staff_dashboard.html",
        assigned_treks=assigned_treks,
        staff=staff
    )

#trekker dashboard route

@app.route("/trekker_dashboard")
def trekker_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Trekker":
        return "Access Denied!"

    return "Welcome Trekker!"

#logout route
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

#Create trek route
@app.route("/create_trek", methods=["GET","POST"])
def create_trek():
    if "user_id" not in session:
        return redirect("/login")

    elif session["role"] != "Admin":
        return "Access Denied!"

    else:
        if request.method == "GET":
            return render_template("create_trek.html")

        elif request.method == "POST":
            trek_name =request.form.get("trek_name")
            location =request.form.get("location")
            difficulty =request.form.get("difficulty")
            duration =request.form.get("duration")
            available_slots=request.form.get("available_slots")
            start_date=request.form.get("start_date")
            end_date=request.form.get("end_date")

            existing_trek = Trek.query.filter_by(trek_name=trek_name).first()

            if existing_trek:
                return "Trek with this name already exists!"
            


            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

            trek = Trek(trek_name=trek_name , location=location, difficulty=difficulty, duration=duration, available_slots=available_slots, start_date=start_date, end_date=end_date)

            db.session.add(trek)
            db.session.commit()

            
            return redirect("/admin_dashboard")
    
#View treks route

@app.route("/view_treks")
def view_treks():
    if "user_id" not in session:
        return redirect("/login")
    
    if session["role"] != "Admin":
        return "Access Denied!"

    treks = Trek.query.all()

    return render_template("view_treks.html", treks=treks)

#Edit trek route
@app.route("/edit_trek/<int:trek_id>", methods=["GET", "POST"])
def edit_trek(trek_id):
    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Admin":
        return "Access Denied!"

    trek = Trek.query.get_or_404(trek_id)

    if request.method == "POST":
        trek.trek_name = request.form.get("trek_name")
        trek.location = request.form.get("location")
        trek.difficulty = request.form.get("difficulty")
        trek.duration = request.form.get("duration")
        trek.available_slots = request.form.get("available_slots")
        trek.start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d").date()
        trek.end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d").date()
        db.session.commit()
        return redirect("/view_treks")

    if request.method == "GET":
        return render_template("edit_trek.html", trek=trek)
    
#Delete trek route
@app.route("/delete_trek/<int:trek_id>", methods=["GET", "POST"])
def delete_trek(trek_id):
    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Admin":
        return "Access Denied!"

    trek = Trek.query.get_or_404(trek_id)

    db.session.delete(trek)
    db.session.commit()

    return redirect("/view_treks")
        
#Pending staff approvals route
@app.route("/pending_staff")
def pending_staff():
    if "user_id" not in session:
        return redirect("/login")
    
    if session["role"] != "Admin":
        return "Access Denied!"

    pending = StaffProfile.query.filter_by(approval_status="Pending").all()

    return render_template("pending_staff.html", pending=pending)

#Approve staff route
@app.route("/approve_staff/<int:staff_id>")
def approve_staff(staff_id):
    if "user_id" not in session:
        return redirect("/login")
    
    if session["role"] != "Admin":
        return "Access Denied!"

    staff = StaffProfile.query.get_or_404(staff_id)
    staff.approval_status = "Approved"
    db.session.commit()
    
    return redirect("/pending_staff")

#Reject staff route
@app.route("/reject_staff/<int:staff_id>")
def reject_staff(staff_id):
    if "user_id" not in session:
        return redirect("/login")
    if session["role"] != "Admin":
        return "Access Denied!"
    
    staff = StaffProfile.query.get_or_404(staff_id)
    staff.approval_status = "Rejected"
    db.session.commit()

    return redirect("/pending_staff")

#Assign Staff to Trek route
@app.route("/assign_staff/<int:trek_id>", methods=["GET","POST"])
def assign_staff(trek_id):
    if "user_id" not in session:
        return redirect("/login")
    if session["role"] != "Admin":
        return "Access Denied"

    trek=Trek.query.get_or_404(trek_id)

    approved_staff=StaffProfile.query.filter_by(approval_status="Approved").all()

    if request.method == "POST":
        selected_staff_id = request.form.get("staff_id")

        trek.assigned_staff_id = selected_staff_id

        db.session.commit()

        return redirect("/view_treks")

    if request.method == "GET":

        return render_template(
            "assign_staff.html",
            trek=trek,
            approved_staff=approved_staff
        )

#Update Trek Status by Staff
@app.route("/update_status/<int:trek_id>", methods=["GET", "POST"])
def update_status(trek_id):

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Staff":
        return "Access Denied!"

    trek = Trek.query.get_or_404(trek_id)

    if request.method =="POST":
        status  =request.form.get("status")
        trek.status =status

        db.session.commit()

        return redirect("/staff_dashboard")

    if request.method == "GET":

        return render_template(
            "update_status.html",
            trek=trek
        )

#Browse trek by user
@app.route("/browse_treks")
def browse_treks():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Trekker":
        return "Access Denied!"
    user = User.query.get(session["user_id"])

    treks = Trek.query.filter(
    Trek.status == "Open",
    Trek.available_slots > 0).all()

    return render_template(
        "browse_treks.html",
        treks=treks,
        user=user
    )

#Book trek route
@app.route("/book_trek/<int:trek_id>")
def book_trek(trek_id):

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Trekker":
        return "Access Denied!"

    user = User.query.get(session["user_id"])

    trek = Trek.query.get_or_404(trek_id)

    existing_booked = Booking.query.filter_by(trek_id=trek.id,user_id = user.id).first()

    if existing_booked:
        return "You have already booked this trek!"

    if trek.available_slots <= 0:
        return "No slots available!"
    booking = Booking(
    user_id=user.id,
    trek_id=trek.id,
    booking_date=date.today(),
    status="Booked",
    payment_status="Pending")

    db.session.add(booking)

    trek.available_slots -= 1
    db.session.commit()

    return redirect("/browse_treks")

#Booking history route
@app.route("/booking_history")
def booking_history():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Trekker":
        return "Access Denied!"

    bookings = Booking.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "booking_history.html",
        bookings=bookings
    )

#Cancel booking by trekker

@app.route("/cancel_booking/<int:booking_id>")
def cancel_booking(booking_id):

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Trekker":
        return "Access Denied!"

    booking = Booking.query.get_or_404(booking_id)

    if booking.status == "Cancelled":
        return "Booking already cancelled!"

    booking.status = "Cancelled"

    booking.trek.available_slots += 1

    db.session.commit()

    return redirect("/booking_history")

#View all users
@app.route("/view_users")
def view_users():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Admin":
        return "Access Denied!"

    users = User.query.all()

    return render_template(
        "view_users.html",
        users=users
    )

# Views all bookings in admin
@app.route("/view_bookings")
def view_bookings():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Admin":
        return "Access Denied!"

    bookings = Booking.query.all()

    return render_template(
        "view_bookings.html",
        bookings=bookings
    )
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)