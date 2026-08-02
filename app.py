from flask import Flask,render_template
from extensions import db
from config import Config
from models import User
app= Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)