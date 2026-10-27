"""Catalog of job portals shown in V4Career.

Catalog presence makes a portal discoverable in the UI; it does not mean a
collector is configured or authorized. Configure and test an Actor/API/feed
before enabling collection. Popular portals are ordered first for sidebar UX.
"""
JOB_PORTALS = [
    {'name': 'Naukri', 'base_url': 'https://www.naukri.com', 'key': 'NAUKRI', 'popular': True},
    {'name': 'Indeed', 'base_url': 'https://in.indeed.com', 'key': 'INDEED', 'popular': True},
    {'name': 'Foundit', 'base_url': 'https://www.foundit.in', 'key': 'FOUNDIT', 'popular': True},
    {'name': 'TimesJobs', 'base_url': 'https://www.timesjobs.com', 'key': 'TIMESJOBS', 'popular': True},
    {'name': 'LinkedIn Jobs', 'base_url': 'https://www.linkedin.com/jobs/', 'key': 'LINKEDIN_JOBS', 'popular': False},
    {'name': 'Internshala', 'base_url': 'https://internshala.com', 'key': 'INTERNSHALA', 'popular': False},
    {'name': 'Freshersworld', 'base_url': 'https://www.freshersworld.com/', 'key': 'FRESHERSWORLD', 'popular': False},
    {'name': 'Cutshort', 'base_url': 'https://cutshort.io/', 'key': 'CUTSHORT', 'popular': False},
    {'name': 'Instahyre', 'base_url': 'https://www.instahyre.com/', 'key': 'INSTAHYRE', 'popular': False},
    {'name': 'Hirist', 'base_url': 'https://www.hirist.tech/', 'key': 'HIRIST', 'popular': False},
    {'name': 'Apna', 'base_url': 'https://apna.co/', 'key': 'APNA', 'popular': False},
    {'name': 'Shine.com', 'base_url': 'https://www.shine.com/', 'key': 'SHINE_COM', 'popular': False},
    {'name': 'Wellfound', 'base_url': 'https://wellfound.com', 'key': 'WELLFOUND', 'popular': False},
    {'name': 'National Career Service (NCS)', 'base_url': 'https://www.ncs.gov.in/', 'key': 'NATIONAL_CAREER_SERVICE_NCS', 'popular': False},
    {'name': 'iimjobs', 'base_url': 'https://www.iimjobs.com/', 'key': 'IIMJOBS', 'popular': False},
    {'name': 'HerKey', 'base_url': 'https://www.herkey.com/', 'key': 'HERKEY', 'popular': False},
    {'name': 'WorkIndia', 'base_url': 'https://www.workindia.in/', 'key': 'WORKINDIA', 'popular': False},
    {'name': 'Hirect', 'base_url': 'https://hirect.in/', 'key': 'HIRECT', 'popular': False},
    {'name': 'Jooble', 'base_url': 'https://in.jooble.org/', 'key': 'JOOBLE', 'popular': False},
    {'name': 'QuikrJobs', 'base_url': 'https://www.quikr.com/jobs', 'key': 'QUIKRJOBS', 'popular': False},
    {'name': 'Jobsora', 'base_url': 'https://in.jobsora.com/', 'key': 'JOBSORA', 'popular': False},
    {'name': 'Jora', 'base_url': 'https://in.jora.com/', 'key': 'JORA', 'popular': False},
    {'name': 'PlacementIndia', 'base_url': 'https://www.placementindia.com/', 'key': 'PLACEMENTINDIA', 'popular': False},
    {'name': 'LetsIntern', 'base_url': 'https://www.letsintern.com/', 'key': 'LETSINTERN', 'popular': False},
    {'name': 'Glassdoor', 'base_url': 'https://www.glassdoor.co.in/Job', 'key': 'GLASSDOOR', 'popular': False},
]


# Only these portals are exposed in the Job Portal UI based on successful
# job-save tests. Keep test candidates in JOB_PORTALS so they can be invoked
# from the CLI without prematurely presenting them as operational.
UI_PORTAL_KEYS = {
    "NAUKRI", "INDEED", "FOUNDIT", "TIMESJOBS", "INTERNSHALA",
    "WELLFOUND", "GLASSDOOR", "HIRIST", "SHINE_COM", "IIMJOBS", "JOOBLE",
    "FRESHERSWORLD", "QUIKRJOBS",
}

PORTAL_BY_KEY = {item["key"].lower(): item for item in JOB_PORTALS}
PORTAL_BY_NAME = {item["name"].strip().lower(): item for item in JOB_PORTALS}

# Community Actor candidates already used by this project. These are not
# pre-approved; collection still requires APIFY_ACCESS_APPROVED_<KEY>=true.
DEFAULT_APIFY_ACTORS = {
    "NAUKRI": "automation-lab~naukri-scraper",
    "INDEED": "unfenced-group~indeed-in-scraper",
    "FOUNDIT": "deriverge~foundit-jobs-scraper",
    "INTERNSHALA": "automation-lab~internshala-scraper",
    "TIMESJOBS": "unfenced-group~timesjobs-scraper",
    "WELLFOUND": "cprussin~wellfound-jobs",
    # Additional public Actor candidates; each remains approval-gated.
    "CUTSHORT": "silentflow~cutshort-jobs-scraper",
    "INSTAHYRE": "themineworks~instahyre-jobs-scraper",
    "HIRIST": "s_actors~hirist-jobs-scraper",
    "APNA": "automation-lab~apna-india-job-listings-scraper",
    "SHINE_COM": "bovi~shine-scraper",
    "IIMJOBS": "silentflow~iimjobs-scraper",
    "WORKINDIA": "jobsapi~workindia-jobs-search-scraper",
    "GLASSDOOR": "hgservices~glassdoor-jobs-scraper",
    # Additional candidates discovered in public Apify Store listings; not live-tested.
    "LINKEDIN_JOBS": "keklik~linkedin-jobs-scraper",
    "FRESHERSWORLD": "shahidirfan~freshersworld-jobs-scraper",
    "NATIONAL_CAREER_SERVICE_NCS": "jobsapi~ncs-jobs-search-scraper",
    "JOOBLE": "ahmed_jasarevic~jooble-scraper",
    "QUIKRJOBS": "jobsapi~quikr-jobs-search-scraper",
    "JORA": "scrapeai~jora-jobs-scraper",
}
