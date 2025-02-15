# Project Student Assignment System for Supervisors

This is a Django-based application for automating the assignment of students to project supervisors based on rankings.

## Project Overview
The Department of Computer Science uses a ranking-based system to assign students to project supervisors. This web application automates the assignment process based on the rankings of both students and lecturers. The system ensures fairness and efficiency by following the department's policy of allocating the best student to the highest-ranked lecturer in successive rounds until all students are assigned.

## Core Features
1. **Ranking Management:**
    - Lecturer Ranking: Lecturers are ranked based on student's ratings
    - Student Ranking: Enable the entry and update of student rankings based on their academic performance.
2. **Assignment Algorithm:**
    - Implement an algorithm to assign students to supervisors based on their respective rankings.
    - Ensure that the assignment process follows the round-robin method:
      - Best student to the top-ranked lecturer in the first round.
      - Continue in successive rounds until all students are assigned.
3. **Assignment Display and Export:**
    - Display the finalized student-supervisor assignments.
    - Provide an option to export the assignments in formats like PDF or Excel for official use.
4. **Admin Dashboard:**
    - A centralized interface for administrators to input rankings, run the assignment algorithm, and manage results.
5. **User Roles:**
    - Admin Role: Manage rankings, run assignments, and view/export results.
    - Lecturer Role: View assigned students.
    - Student Role: View their assigned supervisor.

## Technologies to Use
- **Frontend:**
  - HTML and CSS for building a clean, user-friendly interface.
  - JavaScript for interactivity and responsiveness.
- **Backend:**
  - Django for server-side logic and implementing the assignment algorithm.
- **Database:**
  - PostgreSQL (or any preferred database) to store rankings, assignments, and other related data.

## Development Objectives
1. Automate the student-to-supervisor assignment process to save time and reduce manual errors.
2. Create a system that is intuitive and easy to use for all stakeholders.
3. Ensure scalability to accommodate future increases in students or lecturers.
4. Implement innovative features that add value to the system and improve user experience.

## Prerequisites
- Python 3.8 or higher
- Django 3.2 or higher
- PostgreSQL (or any preferred database)

## Installation
1. Clone the repository:
     ```sh
     git clone <repository-url>
     cd <repository-directory>
     ```

2. Create and activate a virtual environment:
     ```sh
     # in cd backend\
     python -m venv venv
     source venv/bin/activate  # On Windows use `venv\Scripts\activate`
     ```

3. Install dependencies:
     ```sh
     pip install -r backend/requirements.txt
     ```

4. Set up the database:
     ```sh
     python manage.py makemigrations
     python manage.py migrate
     ```

5. Create a superuser to access the admin panel:
     ```sh
     python manage.py createsuperuser
     ```

6. Run the server:
     ```sh
     python manage.py runserver
     ```

## Usage
1. Access the admin panel at `http://127.0.0.1:8000/admin` to manage users and assignments.
2. Use the API documentation at `http://127.0.0.1:8000/swagger` for API interactions.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. Ensure that you follow the project's coding standards and write tests for new features.

