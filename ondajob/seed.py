"""
Seed the database with sample data.
Run: python seed.py
"""
from app import create_app
from app.extensions import db
from app.models import User, Profile, Company, Job, Application, Experience, Education, Message

app = create_app()

with app.app_context():
    db.create_all()

    # ── Check if already seeded ──────────────────────────────
    if User.query.first():
        print("Database already has data. Skipping seed.")
        exit()

    # ── Admin ────────────────────────────────────────────────
    admin = User(
        first_name="Super", last_name="Admin",
        email="admin@ondajob.com", role="admin",
        avatar_initials="SA",
    )
    admin.set_password("admin123")
    db.session.add(admin)

    # ── Job Seeker ───────────────────────────────────────────
    seeker = User(
        first_name="Juan", last_name="dela Cruz",
        email="juan@email.com", phone="+63 917 123 4567",
        role="jobseeker", avatar_initials="JD",
    )
    seeker.set_password("password123")
    db.session.add(seeker)
    db.session.flush()

    profile = Profile(
        user_id=seeker.id,
        title="Senior Frontend Developer",
        summary="Results-driven Frontend Developer with 5+ years of experience building scalable web applications using React.js and TypeScript.",
        location="Makati City, Philippines",
        skills="React.js,TypeScript,Next.js,Node.js,GraphQL,CSS/SASS",
        resume_score=72,
        experience_years=5,
    )
    db.session.add(profile)
    db.session.flush()

    exp1 = Experience(
        profile_id=profile.id, job_title="Frontend Developer",
        company="TechSolutions Inc.", start_date="Jan 2022", end_date="Present",
        description="Built and maintained React.js components for the company's main SaaS product."
    )
    exp2 = Experience(
        profile_id=profile.id, job_title="Junior Web Developer",
        company="StartupPH", start_date="Mar 2020", end_date="Dec 2021",
        description="Developed responsive web interfaces using HTML, CSS, and Vue.js."
    )
    edu = Education(
        profile_id=profile.id, degree="BS Computer Science",
        school="University of the Philippines", start_year="2016", end_year="2020",
    )
    db.session.add_all([exp1, exp2, edu])

    # ── Employer ─────────────────────────────────────────────
    employer = User(
        first_name="HR", last_name="Manager",
        email="hr@techcorp.ph", role="employer",
        avatar_initials="TC",
    )
    employer.set_password("password123")
    db.session.add(employer)
    db.session.flush()

    company = Company(
        user_id=employer.id, name="TechCorp Philippines",
        description="Leading tech company in the Philippines.",
        industry="Technology", location="Makati City",
        employee_count="500+", logo_emoji="🏢",
    )
    db.session.add(company)
    db.session.flush()

    # ── Jobs ─────────────────────────────────────────────────
    jobs_data = [
        {"title": "Senior Frontend Developer", "location": "Remote", "job_type": "full-time",
         "work_setup": "remote", "experience_level": "senior", "salary_min": 80000, "salary_max": 120000,
         "skills_required": "React.js,TypeScript,Next.js,GraphQL", "industry": "Technology",
         "is_featured": True},
        {"title": "Product Designer (UX/UI)", "location": "BGC, Taguig", "job_type": "full-time",
         "work_setup": "hybrid", "experience_level": "mid", "salary_min": 45000, "salary_max": 65000,
         "skills_required": "Figma,Prototyping,Design Systems", "industry": "Technology"},
        {"title": "Data Scientist", "location": "Pasig City", "job_type": "full-time",
         "work_setup": "on-site", "experience_level": "senior", "salary_min": 100000, "salary_max": 160000,
         "skills_required": "Python,TensorFlow,SQL,Power BI", "industry": "Technology",
         "is_featured": True, "is_urgent": True},
        {"title": "Mobile Developer (Flutter)", "location": "Cebu City", "job_type": "full-time",
         "work_setup": "remote", "experience_level": "mid", "salary_min": 60000, "salary_max": 90000,
         "skills_required": "Flutter,Dart,Firebase,REST APIs", "industry": "Technology"},
        {"title": "Backend Engineer (Node.js)", "location": "Makati City", "job_type": "full-time",
         "work_setup": "hybrid", "experience_level": "senior", "salary_min": 90000, "salary_max": 140000,
         "skills_required": "Node.js,PostgreSQL,Docker,AWS", "industry": "Technology"},
        {"title": "Cloud Solutions Architect", "location": "Ortigas Center", "job_type": "full-time",
         "work_setup": "hybrid", "experience_level": "lead", "salary_min": 150000, "salary_max": 200000,
         "skills_required": "AWS,Azure,Terraform,Kubernetes", "industry": "Technology",
         "is_featured": True},
    ]
    for jd in jobs_data:
        job = Job(employer_id=employer.id, company_id=company.id, **jd)
        db.session.add(job)
    db.session.flush()

    # ── Applications ─────────────────────────────────────────
    jobs = Job.query.all()
    if len(jobs) >= 3:
        db.session.add(Application(user_id=seeker.id, job_id=jobs[0].id, status="interview"))
        db.session.add(Application(user_id=seeker.id, job_id=jobs[1].id, status="reviewing"))
        db.session.add(Application(user_id=seeker.id, job_id=jobs[2].id, status="applied"))

    # ── Messages ─────────────────────────────────────────────
    db.session.add(Message(sender_id=employer.id, receiver_id=seeker.id,
        content="Hello Juan! We've reviewed your resume and we're very impressed!"))
    db.session.add(Message(sender_id=employer.id, receiver_id=seeker.id,
        content="We'd like to invite you for a technical interview. Would you be available this Friday?"))
    db.session.add(Message(sender_id=seeker.id, receiver_id=employer.id,
        content="Thank you so much for the opportunity. Friday works perfectly for me!"))

    db.session.commit()
    print("✅ Database seeded successfully!")
    print("  Admin:     admin@ondajob.com / admin123")
    print("  Seeker:    juan@email.com / password123")
    print("  Employer:  hr@techcorp.ph / password123")
