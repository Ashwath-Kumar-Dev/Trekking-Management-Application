from flask import Flask,render_template,request,session,redirect
from extensions import db
from config import Config
from models import User
from werkzeug.security import generate_password_hash, check_password_hash


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

    

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return "Email already registered!"

    hashed_password = generate_password_hash(password)

    user = User(username=username , email=email, password=hashed_password,role="Trekker",status="ACTIVE")

    db.session.add(user)
    db.session.commit()

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
    
#admin dashboard route
@app.route("/admin_dashboard")

def admin_dashboard():
    if "user_id" not in session:
        return redirect("/login")
    elif session["role"] !="Admin":
        return "Access Denied!"
    return "Welcome Admin!"

#staff dashboard route

@app.route("/staff_dashboard")
def staff_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Staff":
        return "Access Denied!"

    return "Welcome Staff!"

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

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)