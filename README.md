Period Tracker App

Project Description

Period Tracker App is an application designed to track menstrual cycles, hormonal health, and overall well-being. The app allows users to log symptoms, monitor moods, and analyze cycle statistics.

Features • Registration and Login – Users can create an account and log in. • Cycle Calendar – An interactive calendar to track menstrual cycle phases. • Health and Cycle Form – Users can log symptoms, mood, and other health-related data. • Statistics – Analysis of cycle, symptoms, pain levels, and moods based on collected data. • PDF Export – Ability to export cycle statistics in PDF format. • Knowledge Base – Access to articles and information on hormonal and menstrual health.

Technologies

The application is built using: • Backend: Django (Python) • Frontend: HTML, CSS, JavaScript • Database: PostgreSQL • Report Generation: ReportLab (PDF)

Installation and Configuration

    Clone the repository: git clone https://github.com/user/period-tracker.git 
    cd period-tracker
    Create and activate a virtual environment: python3 -m venv venv source venv/bin/activate # (Windows: venv\Scripts\activate)
    Install dependencies: pip install -r requirements.txt
    Apply database migrations: python manage.py migrate
    Run the development server: python manage.py runserver
    
License This project is released under the GNU General Public License v3.0
