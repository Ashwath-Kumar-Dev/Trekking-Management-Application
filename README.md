# 🥾 Trekking Management Application V1

A web-based Trekking Management System developed as part of the **IIT Madras BS in Data Science and Applications – Modern Application Development I** project.

The application helps manage trekking packages, users, staff, participants, and bookings through three different roles.

## 👥 User Roles

### 👨‍💼 Admin
- Manage trekking packages
- Create and edit treks
- Assign staff to treks
- Manage users and staff
- Activate / deactivate users and staff
- View all bookings
- Search users, staff, and treks

### 🧑‍💼 Staff
- View assigned treks
- View participant count
- View participants
- Update booking status
- Manage participants only for assigned treks

### 🥾 Trekker
- Browse available treks
- Search treks
- Book treks
- View booking history
- Cancel bookings
- Track completed bookings

## 🛠️ Technologies Used

- Python
- Flask
- SQLite
- Flask-SQLAlchemy
- HTML
- Jinja2
- Bootstrap
- CSS
- JavaScript

## 🔐 Key Features

- Role-based authentication and authorization
- Trek management
- Staff assignment
- User and staff management
- Search functionality
- Participant management
- Booking validation
- Duplicate booking prevention
- Available slot management
- Booking cancellation
- Booking history
- Activate / deactivate users and staff
- Security checks for unauthorized access

## 🗄️ Main Database Models

The application uses four main models:

- `User`
- `StaffProfile`
- `Trek`
- `Booking`

The models are connected using SQLAlchemy relationships and foreign keys.

## 🚀 How to Run

Clone the repository:

```bash
git clone https://github.com/25f2008445/Trekking-Management-Application.git