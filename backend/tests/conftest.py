import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


SAMPLE_RESUME = """John Doe
john.doe@email.com | (555) 123-4567
linkedin.com/in/johndoe | github.com/johndoe

SUMMARY
Backend engineer with 5 years of experience building Python web services and data pipelines.

EXPERIENCE

Senior Software Engineer | Acme Corp | Jan 2022 - Present
- Rewrote the payment processing pipeline in Python, cutting transaction failures from 12% to 2.3%
- Owned on-call for 3 microservices handling 50K requests per minute across AWS ECS clusters
- Debugged a race condition in the order queue that had been open for 6 months, root-caused to a missing Redis lock
- Mentored 2 junior engineers through weekly 1:1 pairing sessions on system design

Software Engineer | StartupXYZ | Jun 2019 - Dec 2021
- The recommendation engine I built served 10M daily users with p99 latency under 200ms
- Under a 3-week deadline, shipped a FastAPI service that replaced a legacy Django monolith
- Collaborated with the data science team to deploy a PyTorch model to production via Docker and Kubernetes
- 4 production incidents resolved as primary on-call, including a database failover during Black Friday

EDUCATION
BS Computer Science | State University | 2019

SKILLS
Python, JavaScript, FastAPI, Django, React, PostgreSQL, Redis, Docker, Kubernetes, AWS, Git

PROJECTS
- Open source contributor to FastAPI (3 merged PRs fixing edge cases in dependency injection)
"""

SAMPLE_JD = """Senior Backend Engineer

We are looking for a Senior Backend Engineer to join our platform team. You will design and build
scalable microservices that power our core product.

Requirements:
- 5+ years of experience in backend development
- Strong proficiency in Python (FastAPI or Django preferred)
- Experience with PostgreSQL, Redis, and message queues
- Hands-on experience with Docker, Kubernetes, and AWS
- Understanding of microservice architecture and distributed systems
- Experience with CI/CD pipelines and infrastructure as code
- Strong communication and collaboration skills
- BS in Computer Science or equivalent

Nice to have:
- Experience with machine learning model deployment
- Familiarity with React or frontend technologies
- Open source contributions
- Experience with high-traffic systems (10K+ requests/second)
"""

AI_HEAVY_RESUME = """Jane Smith
jane@email.com

SUMMARY
Passionate and results-driven dynamic professional with a proven track record of delivering innovative solutions in fast-paced environments. Detail-oriented self-starter with strong communication skills.

EXPERIENCE

Software Engineer | TechCo | 2020 - Present
- Developed a scalable microservice architecture using Docker, reducing deployment time by 50%
- Implemented a comprehensive data pipeline leveraging Python, improving data processing efficiency by 40%
- Designed an end-to-end solution for customer onboarding, resulting in a 30% increase in user retention
- Developed a robust API gateway using Node.js, enhancing system reliability by 45%
- Implemented automated testing frameworks utilizing Jest, increasing code coverage by 60%
- Developed a real-time analytics dashboard using React, boosting team productivity by 35%
- Implemented a seamless integration with third-party services, reducing manual work by 70%
- Developed a cutting-edge recommendation engine using machine learning, improving conversion by 25%

EDUCATION
BS Computer Science | University | 2020

SKILLS
Python, JavaScript, React, Node.js, Docker, AWS, PostgreSQL
"""


@pytest.fixture
def sample_resume():
    return SAMPLE_RESUME


@pytest.fixture
def sample_jd():
    return SAMPLE_JD


@pytest.fixture
def ai_heavy_resume():
    return AI_HEAVY_RESUME


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
