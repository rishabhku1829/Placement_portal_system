# Placement-Portal-App-Development

1. Student Details   
Name: Rishabh Kumar   
Roll Number: 24f2008155   
Email: 24f2008155@ds.study.iitm.ac.in  


2. Project Details   
Project Title: Placement System   
Problem Statement:   
To design and build a Placement Portal System (PPS) web application that allows Admins, 
Companies, and Students to interact with the system based on their roles.   
Approach:   
The app was built using Flask as the backend framework with a modular structure. Where admins 
can view upcoming applications and accept applications of new companies while Students can 
login or register and apply for drives and Companies can make their own drives. 


3. AI/LLM Declaration   
I used ChatGPT (GPT-5) to assist in writing SQL Alchemy model definitions, creating API 
documentation samples, and improving variable naming consistency.   
The extent of AI/LLM usage is around 10–15%, limited to code suggestions and documentation 
formatting.   
All final implementation logic, debugging, and integration were done manually.  


4. Technologies and Frameworks Used   
Technology / Library Purpose   
Flask   
Core backend web framework   
SQLAlchemy   
Jinja2   
Flask-Login   
WTForms   
SQLite   
Object Relational Mapper for SQLite database   
Template engine for rendering dynamic HTML pages   
User authentication and session management   
Frontend form validation   
Lightweight local database for storing user data   


5. Database Schema / ER Diagram   
Tables:   
1. User — stores user profile details (id, name, email, password, role, contact, is_active, etc)   
2. Drive — logs user activities (id, user_id, drive_name, company_id, job_title, etc)   
3. Application — stores predefined activity categories (id, student_name, student_id etc)   
4. Profile — stores predefined activity categories (company_id, company_name, contact, 
website etc )  
Relationships:   
● One-to-Many → User → Drive  
● One-to-Many → User → Profile  
● Many-to-One → Application → User(role=”student”)   
● Many-to-One → Drive→ Profile 


7. Architecture and Features   
Architecture Overview:   
● app.py – main Flask application entry point   
● /models – database models using SQLAlchemy    
● /database – database connection   
● /templates – Jinja2 HTML templates   
Implemented Features:   
User registration and login   
Doctor only able to login if admin approved its profile   
Applications cab be booked by students  
Doctor can also make their own drives for students     
Responsive UI built with manual css   


8. Video Presentation   
Drive Link:   
https://drive.google.com/file/d/1618PVV_lcur3DUh8_y7IPZsBXsoU68LZ/view?usp=sharing 
(Accessible to all with “View” permission.) 