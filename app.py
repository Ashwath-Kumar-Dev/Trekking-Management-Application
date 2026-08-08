from flask import Flask, flash,render_template,request,session,redirect,url_for
from extensions import db
from config import Config
from models import User,Trek,StaffProfile,Booking   
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from datetime import date
from sqlalchemy import or_

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

from flask import Flask, render_template, request, redirect, url_for, flash

#Register route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
        
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    role = request.form.get("role")
    contact = request.form.get("contact")
    experience = request.form.get("experience")
    
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash("Email already registered!", "danger")
        return redirect(url_for('register'))
        
    hashed_password = generate_password_hash(password)
    user = User(username=username, email=email, password=hashed_password, role=role, status="ACTIVE")
    db.session.add(user)
    db.session.commit()
    
    if role == "Staff":
        staff = StaffProfile(user_id=user.id, contact=contact, experience=experience, approval_status="Pending")
        db.session.add(staff)
        db.session.commit()
        flash("Staff Registration Submitted! Wait for Admin Approval.", "warning")
        return redirect(url_for('login'))
        
    flash("Registered successful!", "success")
    return redirect(url_for('login'))


#login route
@app.route("/login", methods=["GET", "POST"])

def login():
    if request.method == "GET":
        return render_template("login.html")

    email =request.form.get("email")
    password =request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if user.status == "BLACKLISTED":
        return "Your account has been deactivated."

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

# Admin Dashboard
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
#Staff dashboard route

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

    for trek in assigned_treks:
        trek.participant_count=Booking.query.filter_by(trek_id=trek.id,status="Booked").count()

    return render_template(
        "staff_dashboard.html",
        assigned_treks=assigned_treks,
        staff=staff
    )


# Update booking status
@app.route("/update_booking_status/<int:booking_id>", methods=["GET", "POST"])
def update_booking_status(booking_id):

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Staff":
        return "Access Denied!"

    staff = StaffProfile.query.filter_by(
        user_id=session["user_id"]
    ).first()

    if staff.approval_status != "Approved":
        return "Your account is not approved yet."

    booking = Booking.query.get_or_404(booking_id)

    if booking.trek.assigned_staff_id != staff.id:
        return "Access Denied!"

    booking.status = "Completed"

    db.session.commit()

    return redirect("/view_participants/" + str(booking.trek_id))


#trekker dashboard route

@app.route("/trekker_dashboard")
def trekker_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Trekker":
        return "Access Denied!"

    user = User.query.get(session["user_id"])

    total_bookings = Booking.query.filter_by(user_id=user.id).count()

    booked_treks= Booking.query.filter_by(user_id=user.id,status="Booked").count()

    completed_treks=Booking.query.filter_by(user_id=user.id,status="Completed").count()

    return render_template("trekker_dashboard.html",user=user,total_bookings=total_bookings,
    booked_treks=booked_treks,
    completed_treks=completed_treks)

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

    search=search = request.args.get("search")

    if search:
        treks= Trek.query.filter(or_(Trek.trek_name.contains(search),Trek.location.contains(search))).all()
    else:
        treks=Trek.query.all()

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

    existing_booked = Booking.query.filter_by(trek_id=trek.id,user_id = user.id,status="Booked").first()

    if existing_booked:
        return "You have already booked this trek!"
    
    if trek.status != "Open":
        return "This trek is not open for booking."

    if trek.available_slots <= 0:
        return "Sorry, this trek is full. Please browse other treks."
    booking = Booking(
    user_id=user.id,
    trek_id=trek.id,
    booking_date=date.today(),
    status="Booked")

    db.session.add(booking)

    trek.available_slots -= 1
    db.session.commit()

    return redirect("/booking_history")

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
    if booking.user_id != session["user_id"]:
        return "Access Denied!"
    if booking.status != "Booked":
        return "This booking cannot be cancelled!"
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

    search = request.args.get("search")

    if search:
        users = User.query.filter(or_(User.username.contains(search),User.email.contains(search))).all()

    else:
        users =User.query.all()

    return render_template(
        "view_users.html",
        users=users
    )
#View all Staff
@app.route("/view_staff")
def view_staff():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Admin":
        return "Access Denied!"

    search = request.args.get("search")
    
    if search:
        staffs = StaffProfile.query.join(User).filter(or_(User.username.contains(search),User.email.contains(search))).all()
    
    else:
        staffs =StaffProfile.query.all()
    

    return render_template("view_staff.html", staffs=staffs)

#Deactivate the staff
@app.route("/deactivate_staff/<int:staff_id>")
def deactivate_staff(staff_id):

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Admin":
        return "Access Denied!"

    staff = StaffProfile.query.get_or_404(staff_id)

    if staff.user.role == "Admin":
        return "Cannot deactivate Admin."

    staff.user.status = "BLACKLISTED"

    db.session.commit()

    return redirect("/view_staff")

#Activate the staff
@app.route("/activate_staff/<int:staff_id>")
def activate_staff(staff_id):

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Admin":
        return "Access Denied!"

    staff = StaffProfile.query.get_or_404(staff_id)

    if staff.approval_status != "Approved":
        return "Only approved staff can be activated."

    staff.user.status = "ACTIVE"

    db.session.commit()

    return redirect("/view_staff")
#View Participants in trek 
@app.route("/view_participants/<int:trek_id>")
def view_participants(trek_id):
    if "user_id" not in session:
        return redirect("/login")
    if session["role"] != "Staff":
            return "Access Denied!"
    staff = StaffProfile.query.filter_by(
    user_id=session["user_id"]).first()
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != staff.id:
        return "Access Denied!"
    bookings = Booking.query.filter_by(trek_id=trek.id).all()
    participant_count = Booking.query.filter_by(trek_id=trek.id,status="Booked").count()
    return render_template("view_participants.html",trek=trek,bookings=bookings,participant_count=participant_count)
    
    
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

#Deactivate the user
@app.route("/deactivate_user/<int:user_id>")
def deactivate_user(user_id):

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Admin":
        return "Access Denied!"

    user = User.query.get_or_404(user_id)

    if user.role == "Admin":
        return "Cannot deactivate Admin."

    user.status = "BLACKLISTED"

    db.session.commit()

    return redirect("/view_users")

#Activate the user
@app.route("/activate_user/<int:user_id>")
def activate_user(user_id):

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Admin":
        return "Access Denied!"

    user = User.query.get_or_404(user_id)

    user.status = "ACTIVE"

    db.session.commit()

    return redirect("/view_users")



with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)