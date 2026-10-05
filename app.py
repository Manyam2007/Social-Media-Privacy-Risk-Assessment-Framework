from datetime import datetime, timezone

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Assessment


# --------------------------------------------------
# 1. CREATE FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="Social Media Privacy Risk Assessment Framework",
    description="Assess social media privacy risks and view assessment history.",
    version="2.0.0",
)


# --------------------------------------------------
# 2. CORS CONFIGURATION
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# --------------------------------------------------
# 3. DATABASE INITIALIZATION
# --------------------------------------------------

Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# 4. ASSESSMENT QUESTIONS
# --------------------------------------------------

QUESTIONS = [

    # ==================================================
    # CATEGORY 1 — PROFILE & PERSONAL INFORMATION
    # ==================================================

    {
        "id": 1,
        "category": "Profile & Personal Information",
        "question": "How much personal information do you display on your social media profile?",
        "options": [
            {"label": "Very little", "risk_score": 0},
            {"label": "Some basic information", "risk_score": 1},
            {"label": "Several personal details", "risk_score": 3},
            {"label": "A lot of personal information", "risk_score": 4},
        ],
    },

    {
        "id": 2,
        "category": "Profile & Personal Information",
        "question": "Do you publicly display your phone number?",
        "options": [
            {"label": "Never", "risk_score": 0},
            {"label": "Only to trusted contacts", "risk_score": 1},
            {"label": "Sometimes", "risk_score": 3},
            {"label": "Yes, publicly", "risk_score": 4},
        ],
    },

    {
        "id": 3,
        "category": "Profile & Personal Information",
        "question": "Do you publicly display your email address?",
        "options": [
            {"label": "Never", "risk_score": 0},
            {"label": "Only when necessary", "risk_score": 1},
            {"label": "Sometimes", "risk_score": 2},
            {"label": "Yes, publicly", "risk_score": 4},
        ],
    },

    {
        "id": 4,
        "category": "Profile & Personal Information",
        "question": "Do you publicly share information about your school, college, or workplace?",
        "options": [
            {"label": "Never", "risk_score": 0},
            {"label": "Only with trusted people", "risk_score": 1},
            {"label": "Sometimes", "risk_score": 2},
            {"label": "Frequently", "risk_score": 4},
        ],
    },


    # ==================================================
    # CATEGORY 2 — LOCATION PRIVACY
    # ==================================================

    {
        "id": 5,
        "category": "Location Privacy",
        "question": "How often do you share your current location on social media?",
        "options": [
            {"label": "Never", "risk_score": 0},
            {"label": "Only with trusted people", "risk_score": 1},
            {"label": "Sometimes", "risk_score": 2},
            {"label": "Frequently", "risk_score": 4},
        ],
    },

    {
        "id": 6,
        "category": "Location Privacy",
        "question": "Do you tag your exact location when posting photos?",
        "options": [
            {"label": "Never", "risk_score": 0},
            {"label": "Rarely", "risk_score": 1},
            {"label": "Sometimes", "risk_score": 2},
            {"label": "Frequently", "risk_score": 4},
        ],
    },

    {
        "id": 7,
        "category": "Location Privacy",
        "question": "Do you post about your travel plans before or during a trip?",
        "options": [
            {"label": "Never", "risk_score": 0},
            {"label": "Only after returning", "risk_score": 1},
            {"label": "Sometimes", "risk_score": 3},
            {"label": "Frequently", "risk_score": 4},
        ],
    },

    {
        "id": 8,
        "category": "Location Privacy",
        "question": "Do you regularly allow social media apps to access your location?",
        "options": [
            {"label": "Only when necessary", "risk_score": 0},
            {"label": "Only while using the app", "risk_score": 1},
            {"label": "For some apps", "risk_score": 2},
            {"label": "Always", "risk_score": 4},
        ],
    },


    # ==================================================
    # CATEGORY 3 — CONTENT & POST PRIVACY
    # ==================================================

    {
        "id": 9,
        "category": "Content & Post Privacy",
        "question": "How often do you review your old social media posts?",
        "options": [
            {"label": "Frequently", "risk_score": 0},
            {"label": "Sometimes", "risk_score": 1},
            {"label": "Rarely", "risk_score": 3},
            {"label": "Never", "risk_score": 4},
        ],
    },

    {
        "id": 10,
        "category": "Content & Post Privacy",
        "question": "Do you post photos containing sensitive personal information?",
        "options": [
            {"label": "Never", "risk_score": 0},
            {"label": "Rarely", "risk_score": 1},
            {"label": "Sometimes", "risk_score": 3},
            {"label": "Frequently", "risk_score": 4},
        ],
    },

    {
        "id": 11,
        "category": "Content & Post Privacy",
        "question": "Do your social media posts reveal information about your daily routine?",
        "options": [
            {"label": "Never", "risk_score": 0},
            {"label": "Rarely", "risk_score": 1},
            {"label": "Sometimes", "risk_score": 2},
            {"label": "Frequently", "risk_score": 4},
        ],
    },

    {
        "id": 12,
        "category": "Content & Post Privacy",
        "question": "Do you share personal documents or screenshots on social media?",
        "options": [
            {"label": "Never", "risk_score": 0},
            {"label": "Only after removing sensitive details", "risk_score": 1},
            {"label": "Sometimes", "risk_score": 3},
            {"label": "Frequently", "risk_score": 4},
        ],
    },


    # ==================================================
    # CATEGORY 4 — CONNECTIONS & TAGGING
    # ==================================================

    {
        "id": 13,
        "category": "Connections & Tagging",
        "question": "Do you accept friend or follower requests from people you do not know?",
        "options": [
            {"label": "Never", "risk_score": 0},
            {"label": "Rarely", "risk_score": 1},
            {"label": "Sometimes", "risk_score": 3},
            {"label": "Frequently", "risk_score": 4},
        ],
    },

    {
        "id": 14,
        "category": "Connections & Tagging",
        "question": "Do you allow anyone to tag you in posts or photos?",
        "options": [
            {"label": "No", "risk_score": 0},
            {"label": "Only trusted people", "risk_score": 1},
            {"label": "Sometimes", "risk_score": 2},
            {"label": "Yes", "risk_score": 4},
        ],
    },

    {
        "id": 15,
        "category": "Connections & Tagging",
        "question": "Do you review tags before they appear on your profile?",
        "options": [
            {"label": "Always", "risk_score": 0},
            {"label": "Usually", "risk_score": 1},
            {"label": "Rarely", "risk_score": 3},
            {"label": "Never", "risk_score": 4},
        ],
    },

    {
        "id": 16,
        "category": "Connections & Tagging",
        "question": "Do you regularly check your followers or friends list?",
        "options": [
            {"label": "Frequently", "risk_score": 0},
            {"label": "Sometimes", "risk_score": 1},
            {"label": "Rarely", "risk_score": 3},
            {"label": "Never", "risk_score": 4},
        ],
    },


    # ==================================================
    # CATEGORY 5 — ACCOUNT SECURITY
    # ==================================================

    {
        "id": 17,
        "category": "Account Security",
        "question": "Do you use a unique password for each social media account?",
        "options": [
            {"label": "Always", "risk_score": 0},
            {"label": "For most accounts", "risk_score": 1},
            {"label": "For some accounts", "risk_score": 3},
            {"label": "No", "risk_score": 4},
        ],
    },

    {
        "id": 18,
        "category": "Account Security",
        "question": "Do you use two-factor authentication?",
        "options": [
            {"label": "On all important accounts", "risk_score": 0},
            {"label": "On some accounts", "risk_score": 1},
            {"label": "Rarely", "risk_score": 3},
            {"label": "No", "risk_score": 4},
        ],
    },

    {
        "id": 19,
        "category": "Account Security",
        "question": "How often do you review devices or sessions logged into your accounts?",
        "options": [
            {"label": "Frequently", "risk_score": 0},
            {"label": "Sometimes", "risk_score": 1},
            {"label": "Rarely", "risk_score": 3},
            {"label": "Never", "risk_score": 4},
        ],
    },

    {
        "id": 20,
        "category": "Account Security",
        "question": "Do you use a password manager or another secure method to manage passwords?",
        "options": [
            {"label": "Yes", "risk_score": 0},
            {"label": "Sometimes", "risk_score": 1},
            {"label": "I reuse some passwords", "risk_score": 3},
            {"label": "I use the same password everywhere", "risk_score": 4},
        ],
    },


    # ==================================================
    # CATEGORY 6 — SOCIAL ENGINEERING
    # ==================================================

    {
        "id": 21,
        "category": "Social Engineering",
        "question": "Do you click links sent by unknown social media accounts?",
        "options": [
            {"label": "Never", "risk_score": 0},
            {"label": "Only after verifying them", "risk_score": 1},
            {"label": "Sometimes", "risk_score": 3},
            {"label": "Frequently", "risk_score": 4},
        ],
    },

    {
        "id": 22,
        "category": "Social Engineering",
        "question": "Do you verify suspicious messages before responding?",
        "options": [
            {"label": "Always", "risk_score": 0},
            {"label": "Usually", "risk_score": 1},
            {"label": "Sometimes", "risk_score": 2},
            {"label": "Never", "risk_score": 4},
        ],
    },

    {
        "id": 23,
        "category": "Social Engineering",
        "question": "Would you share an account verification code with someone who contacts you?",
        "options": [
            {"label": "Never", "risk_score": 0},
            {"label": "Only if I independently verify the request", "risk_score": 1},
            {"label": "I might if the request looks legitimate", "risk_score": 3},
            {"label": "Yes", "risk_score": 4},
        ],
    },

    {
        "id": 24,
        "category": "Social Engineering",
        "question": "Do you verify whether a social media account is genuine before trusting it?",
        "options": [
            {"label": "Always", "risk_score": 0},
            {"label": "Usually", "risk_score": 1},
            {"label": "Sometimes", "risk_score": 2},
            {"label": "Never", "risk_score": 4},
        ],
    },


    # ==================================================
    # CATEGORY 7 — THIRD-PARTY APPLICATIONS
    # ==================================================

    {
        "id": 25,
        "category": "Third-Party Applications",
        "question": "How often do you review applications connected to your social media accounts?",
        "options": [
            {"label": "Frequently", "risk_score": 0},
            {"label": "Sometimes", "risk_score": 1},
            {"label": "Rarely", "risk_score": 3},
            {"label": "Never", "risk_score": 4},
        ],
    },

    {
        "id": 26,
        "category": "Third-Party Applications",
        "question": "Do you connect your social media account to apps you do not regularly use?",
        "options": [
            {"label": "Never", "risk_score": 0},
            {"label": "Rarely", "risk_score": 1},
            {"label": "Sometimes", "risk_score": 3},
            {"label": "Frequently", "risk_score": 4},
        ],
    },

    {
        "id": 27,
        "category": "Third-Party Applications",
        "question": "Do you check the permissions requested by third-party applications?",
        "options": [
            {"label": "Always", "risk_score": 0},
            {"label": "Usually", "risk_score": 1},
            {"label": "Rarely", "risk_score": 3},
            {"label": "Never", "risk_score": 4},
        ],
    },

    {
        "id": 28,
        "category": "Third-Party Applications",
        "question": "Do you remove access for third-party applications you no longer use?",
        "options": [
            {"label": "Always", "risk_score": 0},
            {"label": "Sometimes", "risk_score": 1},
            {"label": "Rarely", "risk_score": 3},
            {"label": "Never", "risk_score": 4},
        ],
    },


    # ==================================================
    # CATEGORY 8 — DIGITAL FOOTPRINT
    # ==================================================

    {
        "id": 29,
        "category": "Digital Footprint",
        "question": "How often do you search for your own name or username online?",
        "options": [
            {"label": "Regularly", "risk_score": 0},
            {"label": "Sometimes", "risk_score": 1},
            {"label": "Rarely", "risk_score": 2},
            {"label": "Never", "risk_score": 3},
        ],
    },

    {
        "id": 30,
        "category": "Digital Footprint",
        "question": "Do you delete old social media accounts that you no longer use?",
        "options": [
            {"label": "Yes", "risk_score": 0},
            {"label": "Usually", "risk_score": 1},
            {"label": "Rarely", "risk_score": 3},
            {"label": "No", "risk_score": 4},
        ],
    },

    {
        "id": 31,
        "category": "Digital Footprint",
        "question": "Do you review old posts for information you no longer want publicly available?",
        "options": [
            {"label": "Frequently", "risk_score": 0},
            {"label": "Sometimes", "risk_score": 1},
            {"label": "Rarely", "risk_score": 3},
            {"label": "Never", "risk_score": 4},
        ],
    },

    {
        "id": 32,
        "category": "Digital Footprint",
        "question": "Do you use the same username across many different websites?",
        "options": [
            {"label": "Rarely", "risk_score": 0},
            {"label": "For a few accounts", "risk_score": 1},
            {"label": "For many accounts", "risk_score": 3},
            {"label": "Almost everywhere", "risk_score": 4},
        ],
    },


    # ==================================================
    # CATEGORY 9 — PHOTO & METADATA AWARENESS
    # ==================================================

    {
        "id": 33,
        "category": "Photo & Metadata Awareness",
        "question": "Do you check photos for sensitive information before posting them?",
        "options": [
            {"label": "Always", "risk_score": 0},
            {"label": "Usually", "risk_score": 1},
            {"label": "Rarely", "risk_score": 3},
            {"label": "Never", "risk_score": 4},
        ],
    },

    {
        "id": 34,
        "category": "Photo & Metadata Awareness",
        "question": "Do your photos sometimes show addresses, ID cards, tickets, or other sensitive details?",
        "options": [
            {"label": "Never", "risk_score": 0},
            {"label": "Rarely", "risk_score": 1},
            {"label": "Sometimes", "risk_score": 3},
            {"label": "Frequently", "risk_score": 4},
        ],
    },

    {
        "id": 35,
        "category": "Photo & Metadata Awareness",
        "question": "Do you know that photos can contain metadata such as location information?",
        "options": [
            {"label": "Yes, and I check it", "risk_score": 0},
            {"label": "Yes, but I rarely check it", "risk_score": 1},
            {"label": "I have heard about it", "risk_score": 2},
            {"label": "No", "risk_score": 4},
        ],
    },

    {
        "id": 36,
        "category": "Photo & Metadata Awareness",
        "question": "Do you check backgrounds in photos before posting them?",
        "options": [
            {"label": "Always", "risk_score": 0},
            {"label": "Usually", "risk_score": 1},
            {"label": "Sometimes", "risk_score": 2},
            {"label": "Never", "risk_score": 4},
        ],
    },


    # ==================================================
    # CATEGORY 10 — PRIVACY SETTINGS
    # ==================================================

    {
        "id": 37,
        "category": "Privacy Settings",
        "question": "How often do you review your social media privacy settings?",
        "options": [
            {"label": "Frequently", "risk_score": 0},
            {"label": "Every few months", "risk_score": 1},
            {"label": "Rarely", "risk_score": 3},
            {"label": "Never", "risk_score": 4},
        ],
    },

    {
        "id": 38,
        "category": "Privacy Settings",
        "question": "Is your main social media profile publicly visible?",
        "options": [
            {"label": "No, it is private", "risk_score": 0},
            {"label": "Visible to friends/followers only", "risk_score": 1},
            {"label": "Partially public", "risk_score": 2},
            {"label": "Completely public", "risk_score": 4},
        ],
    },

    {
        "id": 39,
        "category": "Privacy Settings",
        "question": "Do you control who can see your posts?",
        "options": [
            {"label": "Yes, carefully", "risk_score": 0},
            {"label": "Usually", "risk_score": 1},
            {"label": "Sometimes", "risk_score": 2},
            {"label": "No, most posts are public", "risk_score": 4},
        ],
    },

    {
        "id": 40,
        "category": "Privacy Settings",
        "question": "Do you review who can find or contact you through your social media accounts?",
        "options": [
            {"label": "Frequently", "risk_score": 0},
            {"label": "Sometimes", "risk_score": 1},
            {"label": "Rarely", "risk_score": 3},
            {"label": "Never", "risk_score": 4},
        ],
    },
]


# --------------------------------------------------
# 5. PRIVACY RECOMMENDATIONS
# --------------------------------------------------

RECOMMENDATIONS = {

    "Profile & Personal Information": [
        "Avoid publicly displaying sensitive personal information.",
        "Limit public visibility of your phone number and email address.",
        "Avoid sharing unnecessary information about your school, college, or workplace.",
    ],

    "Location Privacy": [
        "Avoid sharing your live or exact location unnecessarily.",
        "Consider disabling location access for apps that do not require it.",
        "Avoid publicly announcing travel plans before or during a trip.",
    ],

    "Content & Post Privacy": [
        "Review old posts regularly.",
        "Avoid posting sensitive personal information.",
        "Check screenshots, documents, and photos before sharing them publicly.",
    ],

    "Connections & Tagging": [
        "Avoid accepting requests from unknown people.",
        "Enable tag-review controls where available.",
        "Regularly review your followers and friends list.",
    ],

    "Account Security": [
        "Use strong, unique passwords for each account.",
        "Enable two-factor authentication.",
        "Review active login sessions and remove unfamiliar devices.",
        "Consider using a reputable password manager.",
    ],

    "Social Engineering": [
        "Do not click suspicious links.",
        "Verify unexpected messages independently.",
        "Never share authentication or verification codes with other people.",
        "Check whether accounts are genuine before trusting them.",
    ],

    "Third-Party Applications": [
        "Review connected applications regularly.",
        "Remove applications that you no longer use.",
        "Check permissions before connecting third-party applications.",
        "Avoid granting unnecessary access to personal information.",
    ],

    "Digital Footprint": [
        "Review what information about you is publicly searchable.",
        "Delete unused social media accounts where appropriate.",
        "Review old posts and remove information that is no longer necessary.",
        "Consider using different usernames for different contexts.",
    ],

    "Photo & Metadata Awareness": [
        "Check photos before posting them.",
        "Avoid revealing addresses, IDs, tickets, or other sensitive details.",
        "Be aware that digital photos may contain metadata.",
        "Check the background of photos for unintended information.",
    ],

    "Privacy Settings": [
        "Review privacy settings regularly.",
        "Limit profile visibility to people you trust.",
        "Control who can see your posts.",
        "Review who can find or contact you through your accounts.",
    ],
}


# --------------------------------------------------
# 6. REQUEST VALIDATION
# --------------------------------------------------

class AssessmentRequest(BaseModel):
    answers: dict[str, int] = Field(
        ...,
        description="Question IDs mapped to selected risk scores",
    )


# --------------------------------------------------
# 7. RISK CALCULATION
# --------------------------------------------------

def get_risk_level(score: float) -> str:
    if score <= 20:
        return "Low"
    elif score <= 40:
        return "Moderate"
    elif score <= 70:
        return "High"
    else:
        return "Critical"


def calculate_assessment(answers: dict[str, int]):

    question_ids = {str(q["id"]) for q in QUESTIONS}

    # Check for missing and unexpected questions.
    received_ids = set(answers.keys())

    missing = question_ids - received_ids
    unexpected = received_ids - question_ids

    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Missing answers for question IDs: {sorted(missing)}",
        )

    if unexpected:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid question IDs: {sorted(unexpected)}",
        )

    # Validate that each answer is an allowed score.
    for question in QUESTIONS:

        question_id = str(question["id"])
        score = answers[question_id]

        allowed_scores = {
            option["risk_score"]
            for option in question["options"]
        }

        if score not in allowed_scores:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid risk score for question {question_id}",
            )

    # --------------------------------------------------
    # OVERALL RISK SCORE
    # --------------------------------------------------

    total_score = sum(
        answers[str(q["id"])]
        for q in QUESTIONS
    )

    maximum_score = len(QUESTIONS) * 4

    risk_score = round(
        (total_score / maximum_score) * 100,
        2
    )

    risk_level = get_risk_level(risk_score)

    # --------------------------------------------------
    # CATEGORY RISK SCORES
    # --------------------------------------------------

    category_totals = {}
    category_counts = {}

    for question in QUESTIONS:

        category = question["category"]
        score = answers[str(question["id"])]

        category_totals[category] = (
            category_totals.get(category, 0) + score
        )

        category_counts[category] = (
            category_counts.get(category, 0) + 1
        )

    category_scores = {}

    for category, total in category_totals.items():

        count = category_counts[category]

        category_scores[category] = round(
            (total / (count * 4)) * 100,
            2
        )

    # --------------------------------------------------
    # PERSONALIZED RECOMMENDATIONS
    # --------------------------------------------------

    recommendations = {}

    for category, total in category_totals.items():

        average_score = (
            total / category_counts[category]
        )

        if average_score >= 2:

            recommendations[category] = (
                RECOMMENDATIONS[category]
            )

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "category_scores": category_scores,
        "recommendations": recommendations,
        "answers": answers,
    }


# --------------------------------------------------
# 8. ROOT AND HEALTH ENDPOINTS
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "Social Media Privacy Risk Assessment API",
        "version": "2.0.0",
        "questions": len(QUESTIONS),
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "message": "API is running",
        "questions_available": len(QUESTIONS),
    }


# --------------------------------------------------
# 9. QUESTIONS ENDPOINT
# --------------------------------------------------

@app.get("/questions")
def get_questions():

    return QUESTIONS


# --------------------------------------------------
# 10. SUBMIT ASSESSMENT
# --------------------------------------------------

@app.post("/assess")
def submit_assessment(
    request: AssessmentRequest,
    db: Session = Depends(get_db),
):

    result = calculate_assessment(
        request.answers
    )

    assessment = Assessment(
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        category_scores=result["category_scores"],
        recommendations=result["recommendations"],
        answers=result["answers"],
    )

    try:

        db.add(assessment)
        db.commit()
        db.refresh(assessment)

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to save assessment.",
        )

    return {
        "id": assessment.id,
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "category_scores": result["category_scores"],
        "recommendations": result["recommendations"],
    }


# --------------------------------------------------
# 11. ASSESSMENT HISTORY
# --------------------------------------------------

@app.get("/assessments")
def get_assessments(
    db: Session = Depends(get_db)
):

    assessments = (
        db.query(Assessment)
        .order_by(Assessment.id.desc())
        .all()
    )

    return [

        {
            "id": item.id,
            "risk_score": item.risk_score,
            "risk_level": item.risk_level,
            "category_scores": item.category_scores,
            "recommendations": item.recommendations,
            "answers": item.answers,
            "created_at": (
                item.created_at.isoformat()
                if item.created_at
                else None
            ),
        }

        for item in assessments

    ]


# --------------------------------------------------
# 12. GET ONE ASSESSMENT
# --------------------------------------------------

@app.get("/assessments/{assessment_id}")
def get_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
):

    assessment = (
        db.query(Assessment)
        .filter(
            Assessment.id == assessment_id
        )
        .first()
    )

    if assessment is None:

        raise HTTPException(
            status_code=404,
            detail="Assessment not found",
        )

    return {

        "id": assessment.id,
        "risk_score": assessment.risk_score,
        "risk_level": assessment.risk_level,
        "category_scores": assessment.category_scores,
        "recommendations": assessment.recommendations,
        "answers": assessment.answers,

        "created_at": (
            assessment.created_at.isoformat()
            if assessment.created_at
            else None
        ),
    }