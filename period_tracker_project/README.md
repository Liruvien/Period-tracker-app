# Period Tracker App

A Django application that allows users to track their menstrual cycle, analyze health statistics, and access valuable information about women's health. The project includes a range of features such as user registration, login, cycle management, statistics generation, and a knowledge base on hormonal health.
Features

    User Registration and Login:
        Secure user registration.
        Login and logout functionality.

    Home Page:
        A clear and intuitive interface providing access to the app's core features.

    Calendar:
        Displays the user's menstrual cycle.
        Allows adding and editing cycle health information.

    Statistics:
        Analyzes menstrual cycle statistics.
        Exports statistics to a PDF file.

    Knowledge Base:
        Articles on hormonal health, diet, self-care during menstruation, and pregnancy-related health.

Installation
Prerequisites

    Python 3.8
    Django 4.0
    Virtualenv

Installation Steps

    Clone the repository:

git clone x(link or SSH)
cd repository-name

Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate   # for Linux/MacOS
venv\Scripts\activate      # for Windows

Install dependencies:

pip install -r requirements.txt

Apply migrations:

python manage.py makemigrations
python manage.py migrate

Run the development server:

    python manage.py runserver
    Open the app in your browser at http://127.0.0.1:8000.

URL Paths

    admin/: Django Admin Panel.
    register/: User registration.
    login/: User login.
    logout/: User logout.
    /: Home page.
    calendar/: Menstrual cycle calendar.
    statistics/: Health statistics view.
    statistics/export/pdf/: Export statistics to a PDF file.
    knowledge-base/: Knowledge base with articles.
    cycle-health-form-view/: Cycle health form view.
    hormonalne-zdrowie/: Article on hormonal health.
    dieta-wplywajaca-pozytywnie-na-kobiece-hormony/: Article on diet and hormonal health.
    zaopiekuj-sie-soba-podczas-miesiaczki/: Self-care tips during menstruation.
    zdrowie-kobiet-podczas-ciazy/: Health information for pregnancy.

Technology Stack

    Backend: Django 4.x
    Frontend: HTML, CSS
    Database: PostgreSQL
    Other Tools: ReportLab (for PDF generation)

Usage

    Register as a new user.
    Log in to the application.
    Add menstrual cycle data via the calendar view.
    Analyze your cycle statistics in the statistics view.
    Explore articles in the knowledge base.