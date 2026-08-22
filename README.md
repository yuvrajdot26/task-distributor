# AI Powered Task Distributor

A Django-based AI-powered Task Distribution System that intelligently manages employees, creates and assigns tasks based on skills and workload, tracks assignment history, and provides workload analytics through a modern dashboard.

## Features

### Employee Management

* Add, edit, and delete employees
* Track employee skills and experience levels
* Monitor employee availability
* View current task counts per employee

### AI-Powered Task Creation

* Create tasks using only a task title and description
* Uses the Groq API to analyze task requirements
* AI automatically determines:
  * Required skills
  * Task priority (Low, Medium, High)
  * Estimated completion hours
* Reduces manual task configuration and improves task classification

### Task Management

* Create, edit, and delete tasks
* Set task priority (Low, Medium, High)
* Define required skills
* Set estimated hours and deadlines
* Track task status (Pending, In Progress, Completed)

### Smart Task Assignment

* Automatic assignment based on:

  * Required skill match
  * Employee availability
  * Lowest current workload

### Assignment History

* Complete assignment tracking
* Assignment timestamps
* Completion timestamps
* History search functionality

### Dashboard Analytics

* Total Employees
* Total Tasks
* Pending Tasks
* Completed Tasks
* Recent Tasks
* Top Employees
* Workload Overview

### Search & Filtering

* Search employees by name and email
* Search tasks by title and description
* Filter tasks by status
* Filter tasks by required skill
* Search assignment history

### Pagination

* Employee listing pagination
* Task listing pagination
* Assignment history pagination

### Authentication

* Secure login system
* Protected routes using Django authentication

---

### AI Integration

The project integrates the Groq API to add AI-powered task analysis.
When a user creates a task, they provide only the title and description. The AI analyzes the task and automatically determines:

* Required Skill
* Priority
* Estimated Hours

This information is then used by the Task Distributor's assignment system to find the most suitable employee based on their skills, availability, and current workload.

---

## Tech Stack

### Backend

* Python
* Django
* Django ORM

### AI

* Groq API
* LLM-based Task Classification

### Database

* PostgreSQL

### Frontend

* HTML5
* CSS3
* Bootstrap 5

### Version Control

* Git
* GitHub

---

## Project Structure

```text
task-distributor/
│
├── Main_dict/
├── distributor/
├── frontend/
├── manage.py
├── requirements.txt
└── README.md
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/yuvrajdot26/task-distributor.git
cd task-distributor
```

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Environment

```bash
.venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Database

Update PostgreSQL settings inside:

```python
settings.py
```

### Run Migrations

```bash
python manage.py migrate
```

### Create Admin User

```bash
python manage.py createsuperuser
```

### Start Server

```bash
python manage.py runserver
```

---

## Future Improvements

* Email notifications
* REST API documentation
* Role-based access control
* Task comments
* Team management
* Advanced analytics dashboard
* Docker deployment
* CI/CD pipeline

---

## Author

**Yuvraj Dixit**

GitHub: https://github.com/yuvrajdot26
