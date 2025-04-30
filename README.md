# 🧑‍💼 Flask Job Portal

This is a simple **Job Portal** web application built using **Flask**, **SQLite**, and **Bootstrap**. It supports three types of users: **Admin**, **Employer**, and **Job Seeker**.

---

## 🚀 Features

- **User Authentication** (Register/Login/Logout)
- **Admin Panel**
  - View job stats
  - Manage users (activate/deactivate)
- **Employer Dashboard**
  - Post jobs
  - View applicants
  - Delete (deactivate) jobs
- **Job Seeker Dashboard**
  - View applied jobs
  - Apply for jobs
- **Search Jobs** by location
- **Soft Deletion** for jobs and users using `is_active` flag

---

## 🗂 Project Structure

```
├── app.py
├── register_admin.py
├── jobportal.db
├── requirements.txt
├── README.md
├── migrations/
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── post_job.html
│   ├── job_list.html
│   ├── applications.html
│   ├── manage_users.html
│   └── admin_home.html
```

---

## 🛠 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/kiran-kurian/Job-Portal.git
cd Job Portal
```

### 2. Create Virtual Environment

```bash
python -m venv job_env
source job_env/bin/activate  # On Windows: job_env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up the Database

If you're starting fresh:

```bash
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
```

To create an admin user:

```bash
python register_admin.py
```

Follow the prompts to create an admin account.

### 5. Run the App

```bash
python app.py
```

Visit: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📂 Database

- The database used is **SQLite** (`jobportal.db`)
- It includes:
  - `User` model
  - `Job` model
  - `Application` model
- Soft deletion is implemented using `is_active` fields.

---

## 📦 Dependencies

Check `requirements.txt`, includes:

```
Flask
Flask_SQLAlchemy
Flask_Migrate
Werkzeug
```

---

## 📄 License

This project is open-source and free to use for educational purposes.

---

## 🙌 Acknowledgments

Built using:
- [Flask](https://flask.palletsprojects.com/)
- [Bootstrap](https://getbootstrap.com/)
