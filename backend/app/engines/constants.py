BANNED_FIRST_WORDS: set[str] = {
    "developed", "implemented", "managed", "built", "designed", "created", "ensured",
    "delivered", "configured", "resolved", "coordinated", "maintained", "supported",
    "led", "established", "automated", "improved", "worked", "helped", "assisted",
    "utilized", "leveraged", "spearheaded", "oversaw", "championed", "drove",
    "enabled", "handled", "performed", "executed", "orchestrated",
}

BANNED_PHRASES: list[str] = [
    "responsible for", "in charge of", "helped with", "worked on", "involved in",
    "passionate about", "results-driven", "dynamic professional", "dedicated team player",
    "detail-oriented", "seamless integration", "end-to-end solution", "drive continuous improvement",
    "innovative solution", "best practices", "fast-paced environment", "strong communication skills",
    "proven track record", "self-starter", "thought leader", "cutting-edge", "state-of-the-art",
    "robust solution", "value-add", "deep dive", "scalable architecture", "played a key role",
    "in today's rapidly evolving", "it is worth noting", "at the forefront of", "with a focus on",
    "ensuring seamless", "end-to-end ownership", "drove significant improvements",
    "cross-functional collaboration", "key stakeholder", "actionable insights",
    "data-driven decision", "mission-critical", "high-impact", "world-class",
    "industry-leading", "next-generation", "game-changing", "synergy",
    "holistic approach", "paradigm shift", "core competency", "value proposition",
    "strategic initiative", "operational excellence", "thought leadership",
]

BANNED_EXTENDED_WORDS: set[str] = {
    "delve", "pivotal", "intricate", "showcasing", "synergy", "harnessed",
    "facilitated", "holistic", "transformative", "meticulous", "revolutionized",
    "realm", "landscape", "paradigm", "ecosystem", "proactively", "strategically",
    "comprehensive", "streamlined", "utilized", "furthermore", "moreover", "additionally",
}

AI_STRUCTURE_PATTERNS: list[str] = [
    r"(?i)\b\w+\b\s+while\s+also\s+\w+",
    r"(?i)not\s+only\s+.+?\s+but\s+also",
    r"(?i)this\s+(allowed|enabled)\s+\w+\s+to",
    r"(?i)in\s+order\s+to\s+\w+",
    r"(?i)^(furthermore|moreover|additionally),?\s",
]

ROUND_NUMBERS: set[int] = {20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95}

TRANSITIONAL_OPENERS: set[str] = {
    "additionally", "furthermore", "moreover", "subsequently", "consequently", "notably",
}

RESUME_SECTIONS: list[str] = [
    "contact", "summary", "objective", "experience", "work experience",
    "employment", "education", "skills", "technical skills", "projects",
    "certifications", "certifications & training", "awards", "publications",
    "volunteer", "languages", "interests", "references",
]

REQUIRED_SECTIONS: list[str] = ["contact", "experience", "education", "skills"]
RECOMMENDED_SECTIONS: list[str] = ["summary", "projects", "certifications"]

SKILL_CATEGORIES: dict[str, list[str]] = {
    "programming_languages": [
        "python", "java", "javascript", "typescript", "c#", "c++", "go", "rust",
        "ruby", "swift", "kotlin", "php", "scala", "r",
    ],
    "frontend": [
        "react", "angular", "vue", "svelte", "next.js", "nuxt", "html", "css",
        "sass", "tailwind", "bootstrap", "jquery", "webpack", "vite",
    ],
    "backend": [
        "node.js", "express", "fastapi", "django", "flask", "spring", "spring boot",
        ".net", ".net core", "asp.net", "rails", "laravel", "gin",
    ],
    "databases": [
        "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "dynamodb",
        "cassandra", "sqlite", "oracle", "sql server", "mariadb",
    ],
    "cloud": ["aws", "azure", "gcp", "heroku", "vercel", "netlify", "digitalocean", "cloudflare"],
    "devops": [
        "docker", "kubernetes", "terraform", "ansible", "jenkins", "github actions",
        "gitlab ci", "circleci", "helm", "prometheus", "grafana",
    ],
    "ai_ml": [
        "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "keras",
        "langchain", "openai", "huggingface", "spacy", "nltk",
    ],
    "tools": [
        "git", "jira", "confluence", "slack", "figma", "postman", "swagger",
        "datadog", "sentry", "new relic",
    ],
}

# Flatten all skills for quick lookup
ALL_SKILLS: set[str] = set()
for _skills in SKILL_CATEGORIES.values():
    ALL_SKILLS.update(_skills)

SOFT_SKILLS: list[str] = [
    "communication", "teamwork", "leadership", "problem-solving", "problem solving",
    "critical thinking", "time management", "adaptability", "collaboration",
    "creativity", "attention to detail", "work ethic", "interpersonal",
    "negotiation", "conflict resolution", "decision making", "mentoring",
    "presentation", "public speaking", "analytical",
]

KEYWORD_ALIASES: dict[str, list[str]] = {
    "javascript": ["js", "es6", "es2015", "ecmascript"],
    "typescript": ["ts"],
    "python": ["py", "python3"],
    "kubernetes": ["k8s", "kube"],
    "react": ["react.js", "reactjs"],
    "node.js": ["node", "nodejs"],
    "vue": ["vue.js", "vuejs"],
    "angular": ["angularjs", "angular.js"],
    "next.js": ["next", "nextjs"],
    "postgresql": ["postgres", "psql", "pg"],
    "mongodb": ["mongo"],
    "elasticsearch": ["elastic", "es"],
    "amazon web services": ["aws"],
    "google cloud platform": ["gcp", "google cloud"],
    "microsoft azure": ["azure"],
    "machine learning": ["ml"],
    "artificial intelligence": ["ai"],
    "continuous integration": ["ci"],
    "continuous deployment": ["cd"],
    "ci/cd": ["cicd", "ci cd"],
    "docker": ["containerization"],
    ".net": ["dotnet", "dot net"],
    "c#": ["csharp", "c sharp"],
    "c++": ["cpp"],
    "rest api": ["restful", "rest"],
    "graphql": ["gql"],
    "sql": ["structured query language"],
    "nosql": ["no-sql"],
    "html": ["html5"],
    "css": ["css3"],
    "sass": ["scss"],
    "tailwind": ["tailwindcss", "tailwind css"],
    "spring boot": ["springboot"],
    "github actions": ["gh actions"],
    "gitlab ci": ["gitlab-ci"],
    "terraform": ["tf"],
    "infrastructure as code": ["iac"],
    "object oriented programming": ["oop"],
    "test driven development": ["tdd"],
    "behavior driven development": ["bdd"],
    "agile": ["scrum", "kanban"],
    "devops": ["dev ops"],
    "microservices": ["micro-services", "micro services"],
    "api": ["apis"],
    "sdk": ["sdks"],
    "ui": ["user interface"],
    "ux": ["user experience"],
    "sre": ["site reliability engineering"],
}

# Build reverse alias map: alias -> canonical
REVERSE_ALIASES: dict[str, str] = {}
for canonical, aliases in KEYWORD_ALIASES.items():
    for alias in aliases:
        REVERSE_ALIASES[alias.lower()] = canonical.lower()

OPENER_SYNONYM_GROUPS: list[set[str]] = [
    {"built", "created", "developed", "designed", "constructed", "crafted"},
    {"led", "managed", "oversaw", "directed", "headed", "supervised"},
    {"improved", "enhanced", "optimized", "boosted", "elevated", "upgraded"},
    {"implemented", "deployed", "launched", "released", "shipped", "rolled out"},
    {"automated", "streamlined", "simplified", "accelerated"},
    {"analyzed", "evaluated", "assessed", "examined", "investigated"},
    {"collaborated", "partnered", "worked", "cooperated", "teamed"},
    {"configured", "set up", "established", "initialized"},
]

CERTIFICATION_PATTERNS: list[str] = [
    r"(?i)aws\s+certified",
    r"(?i)pmp",
    r"(?i)google\s+cloud\s+certified",
    r"(?i)azure\s+(administrator|developer|architect|fundamentals)",
    r"(?i)certified\s+scrum\s+master",
    r"(?i)csm",
    r"(?i)cissp",
    r"(?i)cka",
    r"(?i)ckad",
    r"(?i)comptia\s+(security|network|a)\+?",
    r"(?i)itil",
    r"(?i)six\s+sigma",
    r"(?i)certified\s+kubernetes",
    r"(?i)professional\s+engineer",
    r"(?i)cpa",
    r"(?i)cfa",
]

JD_DETECTION_PHRASES: list[str] = [
    "we are looking for",
    "requirements",
    "apply now",
    "about the role",
    "responsibilities include",
    "qualifications",
    "what you'll do",
    "who you are",
    "about us",
    "benefits",
    "equal opportunity employer",
]
