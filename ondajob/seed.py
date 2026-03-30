#!/usr/bin/env python
"""
Comprehensive seed data for Online Job Portal
Creates realistic test data for all user types and features
"""

from app import create_app, db
from app.models import (
    User, Profile, Experience, Education, Company, Job, Application,
    SavedJob, Message, Notification, Interview, Report
)
from datetime import datetime, timedelta
import random


def clear_data():
    """Clear all tables"""
    db.session.query(Interview).delete()
    db.session.query(Application).delete()
    db.session.query(SavedJob).delete()
    db.session.query(Report).delete()
    db.session.query(Message).delete()
    db.session.query(Notification).delete()
    db.session.query(Job).delete()
    db.session.query(Experience).delete()
    db.session.query(Education).delete()
    db.session.query(Profile).delete()
    db.session.query(Company).delete()
    db.session.query(User).delete()
    db.session.commit()


def create_users():
    """Create admin, jobseekers, and employers"""
    users = []

    # Admin user
    admin = User(
        first_name="Admin",
        last_name="User",
        email="admin@ondajob.com",
        phone="+63917123456",
        role="admin",
        is_active=True
    )
    admin.set_password("admin123")
    users.append(admin)

    # Job Seekers
    jobseeker_data = [
        ("Maria", "Santos", "maria.santos@email.com", "+639171111111"),
        ("Juan", "Cruz", "juan.cruz@email.com", "+639172222222"),
        ("Ana", "Garcia", "ana.garcia@email.com", "+639173333333"),
        ("Carlos", "Lopez", "carlos.lopez@email.com", "+639174444444"),
        ("Rosa", "Reyes", "rosa.reyes@email.com", "+639175555555"),
    ]

    for first, last, email, phone in jobseeker_data:
        user = User(
            first_name=first,
            last_name=last,
            email=email,
            phone=phone,
            role="jobseeker",
            is_active=True
        )
        user.set_password("password123")
        users.append(user)

    # Employers
    employer_data = [
        ("Tech", "Innovations", "john.tech@email.com", "+639176666666"),
        ("Cloud", "Solutions", "sarah.cloud@email.com", "+639177777777"),
        ("Digital", "Agency", "mike.digital@email.com", "+639178888888"),
        ("Data", "Analytics", "emma.data@email.com", "+639179999999"),
    ]

    for first, last, email, phone in employer_data:
        user = User(
            first_name=first,
            last_name=last,
            email=email,
            phone=phone,
            role="employer",
            is_active=True
        )
        user.set_password("employer123")
        users.append(user)

    db.session.add_all(users)
    db.session.commit()
    return users


def create_profiles(users):
    """Create job seeker profiles"""
    jobseekers = [u for u in users if u.role == "jobseeker"]

    profiles_data = [
        {
            "title": "Senior Frontend Developer",
            "summary": "Passionate about building beautiful, responsive web applications with modern frameworks",
            "location": "Manila, Philippines",
            "linkedin_url": "https://linkedin.com/in/maria-santos",
            "portfolio_url": "https://mariaportfolio.com",
            "skills": "React, TypeScript, Tailwind CSS, Next.js, Vue.js",
            "experience_years": 5
        },
        {
            "title": "Full Stack Developer",
            "summary": "Experienced in building scalable web applications with Node.js and React",
            "location": "Cebu, Philippines",
            "linkedin_url": "https://linkedin.com/in/juan-cruz",
            "portfolio_url": None,
            "skills": "Node.js, Express, React, MongoDB, PostgreSQL",
            "experience_years": 4
        },
        {
            "title": "Data Scientist",
            "summary": "Specialized in machine learning and data analysis",
            "location": "Makati, Philippines",
            "linkedin_url": "https://linkedin.com/in/ana-garcia",
            "portfolio_url": "https://anadatascience.com",
            "skills": "Python, TensorFlow, SQL, Pandas, Scikit-learn",
            "experience_years": 3
        },
        {
            "title": "DevOps Engineer",
            "summary": "Infrastructure automation and cloud deployment expert",
            "location": "BGC, Philippines",
            "linkedin_url": "https://linkedin.com/in/carlos-lopez",
            "portfolio_url": None,
            "skills": "Docker, Kubernetes, AWS, CI/CD, Linux",
            "experience_years": 6
        },
        {
            "title": "UI/UX Designer",
            "summary": "Focused on creating intuitive and beautiful user experiences",
            "location": "Quezon City, Philippines",
            "linkedin_url": "https://linkedin.com/in/rosa-reyes",
            "portfolio_url": "https://rosadeigns.com",
            "skills": "Figma, Sketch, UI Design, UX Research, Prototyping",
            "experience_years": 4
        }
    ]

    profiles = []
    for user, data in zip(jobseekers, profiles_data):
        profile = Profile(
            user_id=user.id,
            title=data["title"],
            summary=data["summary"],
            location=data["location"],
            linkedin_url=data["linkedin_url"],
            portfolio_url=data["portfolio_url"],
            skills=data["skills"],
            experience_years=data["experience_years"],
            resume_score=65
        )
        profiles.append(profile)

    db.session.add_all(profiles)
    db.session.commit()

    # Add experiences
    experiences = [
        # Maria's experiences
        (profiles[0].id, "Senior Frontend Developer", "Tech Startup Inc", "Jan 2022", "Present",
         "Leading frontend team, architecting React applications"),
        (profiles[0].id, "Frontend Developer", "Digital Agency", "Jun 2019", "Dec 2021",
         "Built responsive web applications for various clients"),

        # Juan's experiences
        (profiles[1].id, "Full Stack Developer", "E-commerce Platform", "Mar 2021", "Present",
         "Developed and maintained MERN stack applications"),
        (profiles[1].id, "Junior Developer", "Software House", "Jan 2020", "Feb 2021",
         "Worked on backend and frontend features"),

        # Ana's experiences
        (profiles[2].id, "Data Scientist", "Analytics Company", "Jul 2022", "Present",
         "Building machine learning models for business insights"),
        (profiles[2].id, "Data Analyst", "Financial Services", "Sep 2020", "Jun 2022",
         "Analyzed datasets and created visualizations"),

        # Carlos's experiences
        (profiles[3].id, "Senior DevOps Engineer", "Cloud Company", "Nov 2021", "Present",
         "Managing Kubernetes clusters and AWS infrastructure"),
        (profiles[3].id, "DevOps Engineer", "Tech Services", "Apr 2019", "Oct 2021",
         "CI/CD pipeline management and server maintenance"),

        # Rosa's experiences
        (profiles[4].id, "UI/UX Designer", "Design Studio", "Feb 2022", "Present",
         "Designing user interfaces and conducting UX research"),
        (profiles[4].id, "Graphic Designer", "Marketing Agency", "Aug 2020", "Jan 2022",
         "Created digital designs and brand materials"),
    ]

    for profile_id, job_title, company, start_date, end_date, description in experiences:
        exp = Experience(
            profile_id=profile_id,
            job_title=job_title,
            company=company,
            start_date=start_date,
            end_date=end_date,
            description=description
        )
        db.session.add(exp)

    db.session.commit()

    # Add educations
    educations = [
        # Maria
        (profiles[0].id, "Bachelor of Science", "University of the Philippines", "2017", "2021"),
        (profiles[0].id, "React Advanced Course", "Codecademy", "2022", "2022"),

        # Juan
        (profiles[1].id, "Bachelor of Science", "De La Salle University", "2016", "2020"),

        # Ana
        (profiles[2].id, "Master of Science", "Ateneo de Manila University", "2020", "2022"),
        (profiles[2].id, "Bachelor of Science", "Ateneo de Manila University", "2016", "2020"),

        # Carlos
        (profiles[3].id, "Bachelor of Science", "University of Santo Tomas", "2015", "2019"),
        (profiles[3].id, "AWS Certified Solutions Architect", "AWS Academy", "2021", "2021"),

        # Rosa
        (profiles[4].id, "Bachelor of Fine Arts", "Philippine Women's University", "2017", "2021"),
        (profiles[4].id, "UX Design Certification", "Google Career Certificates", "2022", "2022"),
    ]

    for profile_id, degree, school, start_year, end_year in educations:
        edu = Education(
            profile_id=profile_id,
            degree=degree,
            school=school,
            start_year=start_year,
            end_year=end_year
        )
        db.session.add(edu)

    db.session.commit()


def create_companies(users):
    """Create employer companies"""
    employers = [u for u in users if u.role == "employer"]

    companies_data = [
        {
            "name": "Tech Innovations Corp",
            "description": "Leading software development company specializing in web and mobile applications",
            "industry": "Software/Technology",
            "location": "Manila, Philippines",
            "website": "https://techinnovations.com",
            "employee_count": "50-100",
            "logo_emoji": "🚀"
        },
        {
            "name": "Cloud Solutions Ltd",
            "description": "Cloud infrastructure and DevOps services for enterprises",
            "industry": "Cloud Services",
            "location": "BGC, Philippines",
            "website": "https://cloudsolutions.com",
            "employee_count": "100-500",
            "logo_emoji": "☁️"
        },
        {
            "name": "Digital Agency Plus",
            "description": "Full-service digital marketing and design agency",
            "industry": "Marketing/Design",
            "location": "Quezon City, Philippines",
            "website": "https://digitalagencyplus.com",
            "employee_count": "20-50",
            "logo_emoji": "🎨"
        },
        {
            "name": "Data Analytics Pro",
            "description": "Data science and analytics solutions for business intelligence",
            "industry": "Data Analytics",
            "location": "Makati, Philippines",
            "website": "https://dataanalyticspro.com",
            "employee_count": "30-100",
            "logo_emoji": "📊"
        }
    ]

    companies = []
    for user, data in zip(employers, companies_data):
        company = Company(
            user_id=user.id,
            name=data["name"],
            description=data["description"],
            industry=data["industry"],
            location=data["location"],
            website=data["website"],
            employee_count=data["employee_count"],
            logo_emoji=data["logo_emoji"]
        )
        companies.append(company)

    db.session.add_all(companies)
    db.session.commit()
    return companies


def create_jobs(users, companies):
    """Create job listings"""
    employers = [u for u in users if u.role == "employer"]

    jobs_data = [
        # Tech Innovations jobs
        {
            "title": "Senior React Developer",
            "description": "We're looking for an experienced React developer to lead our frontend team...",
            "location": "Manila (Remote Available)",
            "job_type": "full-time",
            "work_setup": "hybrid",
            "experience_level": "senior",
            "salary_min": 150000,
            "salary_max": 250000,
            "skills_required": "React, TypeScript, Next.js, Tailwind CSS",
            "industry": "Software/Technology",
            "is_featured": True,
            "is_urgent": False,
        },
        {
            "title": "Node.js Backend Developer",
            "description": "Join our backend team to build scalable APIs and services...",
            "location": "Manila",
            "job_type": "full-time",
            "work_setup": "on-site",
            "experience_level": "mid",
            "salary_min": 120000,
            "salary_max": 180000,
            "skills_required": "Node.js, Express, PostgreSQL, MongoDB",
            "industry": "Software/Technology",
            "is_featured": False,
            "is_urgent": True,
        },
        # Cloud Solutions jobs
        {
            "title": "DevOps Engineer",
            "description": "Help us manage and improve our cloud infrastructure...",
            "location": "BGC (Remote)",
            "job_type": "full-time",
            "work_setup": "remote",
            "experience_level": "mid",
            "salary_min": 130000,
            "salary_max": 200000,
            "skills_required": "Docker, Kubernetes, AWS, Linux",
            "industry": "Cloud Services",
            "is_featured": True,
            "is_urgent": False,
        },
        {
            "title": "Cloud Architect",
            "description": "Design and implement cloud solutions for our clients...",
            "location": "BGC",
            "job_type": "full-time",
            "work_setup": "hybrid",
            "experience_level": "senior",
            "salary_min": 200000,
            "salary_max": 350000,
            "skills_required": "AWS, Azure, Cloud Architecture, Terraform",
            "industry": "Cloud Services",
            "is_featured": False,
            "is_urgent": False,
        },
        # Digital Agency jobs
        {
            "title": "UI/UX Designer",
            "description": "Create beautiful and intuitive designs for web and mobile projects...",
            "location": "Quezon City",
            "job_type": "full-time",
            "work_setup": "on-site",
            "experience_level": "mid",
            "salary_min": 90000,
            "salary_max": 150000,
            "skills_required": "Figma, UI Design, UX Research, Prototyping",
            "industry": "Marketing/Design",
            "is_featured": True,
            "is_urgent": False,
        },
        {
            "title": "Digital Marketing Specialist",
            "description": "Plan and execute digital marketing campaigns...",
            "location": "Quezon City (Remote Available)",
            "job_type": "full-time",
            "work_setup": "hybrid",
            "experience_level": "entry",
            "salary_min": 60000,
            "salary_max": 100000,
            "skills_required": "Social Media, SEO, Google Analytics, Content Marketing",
            "industry": "Marketing/Design",
            "is_featured": False,
            "is_urgent": True,
        },
        # Data Analytics jobs
        {
            "title": "Data Scientist",
            "description": "Build machine learning models and analyze complex datasets...",
            "location": "Makati (Remote)",
            "job_type": "full-time",
            "work_setup": "remote",
            "experience_level": "mid",
            "salary_min": 140000,
            "salary_max": 220000,
            "skills_required": "Python, TensorFlow, SQL, Machine Learning",
            "industry": "Data Analytics",
            "is_featured": False,
            "is_urgent": False,
        },
        {
            "title": "Data Analyst",
            "description": "Transform data into actionable business insights...",
            "location": "Makati",
            "job_type": "full-time",
            "work_setup": "on-site",
            "experience_level": "entry",
            "salary_min": 70000,
            "salary_max": 120000,
            "skills_required": "SQL, Excel, Tableau, Python",
            "industry": "Data Analytics",
            "is_featured": False,
            "is_urgent": False,
        },
    ]

    jobs = []
    for idx, job_data in enumerate(jobs_data):
        employer = employers[idx % len(employers)]
        company = companies[idx % len(companies)]

        job = Job(
            employer_id=employer.id,
            company_id=company.id,
            title=job_data["title"],
            description=job_data["description"],
            location=job_data["location"],
            job_type=job_data["job_type"],
            work_setup=job_data["work_setup"],
            experience_level=job_data["experience_level"],
            salary_min=job_data["salary_min"],
            salary_max=job_data["salary_max"],
            skills_required=job_data["skills_required"],
            industry=job_data["industry"],
            is_featured=job_data["is_featured"],
            is_urgent=job_data["is_urgent"],
            views_count=random.randint(10, 200)
        )
        jobs.append(job)

    db.session.add_all(jobs)
    db.session.commit()
    return jobs


def create_applications(users, jobs):
    """Create job applications"""
    jobseekers = [u for u in users if u.role == "jobseeker"]

    applications = []
    # Each jobseeker applies to 2-3 random jobs
    for jobseeker in jobseekers:
        selected_jobs = random.sample(jobs, min(3, len(jobs)))
        for job in selected_jobs:
            app = Application(
                user_id=jobseeker.id,
                job_id=job.id,
                status=random.choice(["applied", "reviewing", "interview", "offered", "rejected"]),
                cover_letter=f"I am very interested in this {job.title} position because of my experience in {job.skills_required}",
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            applications.append(app)

    db.session.add_all(applications)
    db.session.commit()
    return applications


def create_saved_jobs(users, jobs):
    """Create saved jobs"""
    jobseekers = [u for u in users if u.role == "jobseeker"]

    saved_jobs = []
    for jobseeker in jobseekers:
        selected_jobs = random.sample(jobs, min(2, len(jobs)))
        for job in selected_jobs:
            saved = SavedJob(
                user_id=jobseeker.id,
                job_id=job.id
            )
            saved_jobs.append(saved)

    db.session.add_all(saved_jobs)
    db.session.commit()


def create_messages(users):
    """Create sample messages"""
    jobseekers = [u for u in users if u.role == "jobseeker"]
    employers = [u for u in users if u.role == "employer"]

    messages = []
    for jobseeker in jobseekers:
        employer = random.choice(employers)
        msg1 = Message(
            sender_id=employer.id,
            receiver_id=jobseeker.id,
            content=f"Hi {jobseeker.first_name}, we're impressed with your application. Would you be available for an interview next week?",
            is_read=random.choice([True, False]),
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 7))
        )
        messages.append(msg1)

        # Jobseeker reply
        msg2 = Message(
            sender_id=jobseeker.id,
            receiver_id=employer.id,
            content="Thank you for reaching out! I'm very interested and would love to discuss this opportunity further.",
            is_read=True,
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 6))
        )
        messages.append(msg2)

    db.session.add_all(messages)
    db.session.commit()


def create_notifications(users):
    """Create sample notifications"""
    notification_types = ["application", "interview", "message", "job_match"]
    messages_list = [
        "Your application has been reviewed",
        "You have a new message from an employer",
        "Interview scheduled for next week",
        "New jobs matching your profile",
        "Your application was accepted"
    ]

    notifications = []
    jobseekers = [u for u in users if u.role == "jobseeker"]
    employers = [u for u in users if u.role == "employer"]

    for user in jobseekers + employers:
        for i in range(random.randint(2, 5)):
            notif = Notification(
                user_id=user.id,
                title=random.choice(["Job Alert", "Interview Update", "New Message", "Application Status"]),
                message=random.choice(messages_list),
                is_read=random.choice([True, False, False]),
                notification_type=random.choice(notification_types),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            notifications.append(notif)

    db.session.add_all(notifications)
    db.session.commit()


def create_interviews(applications):
    """Create sample interviews for applications in interview stage"""
    interview_statuses = ["scheduled", "completed", "cancelled"]
    interview_types = ["phone", "video", "in-person"]

    interviews = []
    for app in applications:
        if app.status == "interview" or app.status == "offered":
            interview = Interview(
                application_id=app.id,
                scheduled_date=datetime.utcnow() + timedelta(days=random.randint(1, 14)),
                interview_type=random.choice(interview_types),
                notes="Preliminary technical screening",
                status=random.choice(interview_statuses),
                feedback="Candidate showed good technical understanding"
            )
            interviews.append(interview)

    db.session.add_all(interviews)
    db.session.commit()


def seed_database():
    """Main seeding function"""
    print("Clearing existing data...")
    clear_data()

    print("Creating users...")
    users = create_users()

    print("Creating job seeker profiles...")
    create_profiles(users)

    print("Creating companies...")
    companies = create_companies(users)

    print("Creating jobs...")
    jobs = create_jobs(users, companies)

    print("Creating applications...")
    applications = create_applications(users, jobs)

    print("Creating saved jobs...")
    create_saved_jobs(users, jobs)

    print("Creating messages...")
    create_messages(users)

    print("Creating notifications...")
    create_notifications(users)

    print("Creating interviews...")
    create_interviews(applications)

    print("\n✅ Database seeded successfully!")
    print(f"\nCreated:")
    print(f"  - {len(users)} users (1 admin, 5 jobseekers, 4 employers)")
    print(f"  - {len(companies)} companies")
    print(f"  - {len(jobs)} job listings")
    print(f"  - {Application.query.count()} applications")
    print(f"  - {SavedJob.query.count()} saved jobs")
    print(f"  - {Message.query.count()} messages")
    print(f"  - {Interview.query.count()} interviews")


if __name__ == "__main__":
    app = create_app("default")
    with app.app_context():
        seed_database()
