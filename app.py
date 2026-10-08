from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify
)

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from urllib.parse import quote
import os


# =========================================================
# SOCIAL BOTS / CAMPAIGN MANAGER
# =========================================================

app = Flask(__name__)


# =========================================================
# CONFIGURATION
# =========================================================

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "change-this-secret"
)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///socialbots.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================================================
# DATABASE MODELS
# =========================================================

class Campaign(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(120),
        nullable=False
    )

    platform = db.Column(
        db.String(40),
        nullable=False
    )

    niche = db.Column(
        db.String(80),
        nullable=False
    )

    username = db.Column(
        db.String(120),
        nullable=False
    )

    goal = db.Column(
        db.String(255),
        default=""
    )

    status = db.Column(
        db.String(40),
        default="Draft",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )


class Lead(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(120),
        nullable=False
    )

    whatsapp = db.Column(
        db.String(50),
        nullable=False
    )

    platform = db.Column(
        db.String(40),
        default=""
    )

    niche = db.Column(
        db.String(80),
        default=""
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )


# =========================================================
# APPLICATION OPTIONS
# =========================================================

PLATFORMS = [

    (
        "Instagram",
        "fa-instagram",
        "Instagram visibility, niche audience and profile growth"
    ),

    (
        "TikTok",
        "fa-tiktok",
        "Short-video discovery and content growth"
    ),

    (
        "Facebook",
        "fa-facebook",
        "Page visibility, engagement and community growth"
    ),

    (
        "YouTube",
        "fa-youtube",
        "Channel discovery, content strategy and audience growth"
    ),

    (
        "X",
        "fa-x-twitter",
        "Profile visibility and conversation strategy"
    ),

    (
        "LinkedIn",
        "fa-linkedin",
        "Professional profile and business audience growth"
    )

]


NICHES = [
    "Business",
    "Fashion",
    "Fitness",
    "Gaming",
    "Travel",
    "Food",
    "Music",
    "Beauty",
    "Education",
    "Photography",
    "Real Estate",
    "Technology",
    "Other"
]


CAMPAIGN_STATUSES = [
    "Draft",
    "Active",
    "Paused",
    "Completed"
]


# =========================================================
# TEMPLATE GLOBALS
# =========================================================

@app.context_processor
def globals():

    return {
        "platforms": PLATFORMS,
        "niches": NICHES,
        "campaign_statuses": CAMPAIGN_STATUSES
    }


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def clean_text(value, max_length=None):

    value = str(value or "").strip()

    if max_length:
        value = value[:max_length]

    return value


def clean_username(value):

    return clean_text(
        value
    ).lstrip("@").strip()


def clean_whatsapp(value):

    # Keep digits and leading +
    value = clean_text(value)

    if value.startswith("+"):

        return "+" + "".join(
            char
            for char in value[1:]
            if char.isdigit()
        )

    return "".join(
        char
        for char in value
        if char.isdigit()
    )


def whatsapp_url(phone, message=""):

    phone = clean_whatsapp(phone)

    if not phone:
        return "#"

    url = "https://wa.me/" + phone

    if message:

        url += "?text=" + quote(
            message
        )

    return url


def valid_platform(platform):

    return any(
        platform == item[0]
        for item in PLATFORMS
    )


def valid_niche(niche):

    return niche in NICHES


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# =========================================================
# CREATE CAMPAIGN
# =========================================================

@app.post("/campaign")
def campaign():

    form = request.form

    name = clean_text(
        form.get("name"),
        120
    )

    platform = clean_text(
        form.get("platform"),
        40
    )

    niche = clean_text(
        form.get("niche"),
        80
    )

    username = clean_username(
        form.get("username")
    )

    goal = clean_text(
        form.get("goal"),
        255
    )

    whatsapp = clean_whatsapp(
        form.get("whatsapp")
    )

    # -----------------------------------------------------
    # REQUIRED FIELDS
    # -----------------------------------------------------

    if not name or not platform or not niche or not username:

        flash(
            "Please complete all required fields.",
            "danger"
        )

        return redirect(
            url_for("index") + "#launch"
        )

    # -----------------------------------------------------
    # VALIDATE PLATFORM
    # -----------------------------------------------------

    if not valid_platform(platform):

        flash(
            "Please select a valid social media platform.",
            "danger"
        )

        return redirect(
            url_for("index") + "#launch"
        )

    # -----------------------------------------------------
    # VALIDATE NICHE
    # -----------------------------------------------------

    if not valid_niche(niche):

        flash(
            "Please select a valid niche.",
            "danger"
        )

        return redirect(
            url_for("index") + "#launch"
        )

    # -----------------------------------------------------
    # CREATE CAMPAIGN
    # -----------------------------------------------------

    campaign_record = Campaign(
        name=name,
        platform=platform,
        niche=niche,
        username=username,
        goal=goal,
        status="Draft"
    )

    db.session.add(
        campaign_record
    )

    # -----------------------------------------------------
    # CREATE LEAD
    # -----------------------------------------------------

    # Only create a lead when WhatsApp was supplied.
    if whatsapp:

        lead_record = Lead(
            name=name,
            whatsapp=whatsapp,
            platform=platform,
            niche=niche
        )

        db.session.add(
            lead_record
        )

    try:

        db.session.commit()

    except Exception:

        db.session.rollback()

        flash(
            "Unable to create the campaign. Please try again.",
            "danger"
        )

        return redirect(
            url_for("index") + "#launch"
        )

    return redirect(
        url_for(
            "campaign_success",
            campaign_id=campaign_record.id
        )
    )


# =========================================================
# CAMPAIGN SUCCESS
# =========================================================

@app.route(
    "/success/<int:campaign_id>"
)
def campaign_success(campaign_id):

    campaign_record = Campaign.query.get_or_404(
        campaign_id
    )

    return render_template(
        "success.html",
        campaign=campaign_record
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    campaigns = Campaign.query.order_by(
        Campaign.created_at.desc()
    ).all()

    stats = {

        "campaigns": Campaign.query.count(),

        "active": Campaign.query.filter_by(
            status="Active"
        ).count(),

        "leads": Lead.query.count(),

        "drafts": Campaign.query.filter_by(
            status="Draft"
        ).count(),

        "paused": Campaign.query.filter_by(
            status="Paused"
        ).count(),

        "completed": Campaign.query.filter_by(
            status="Completed"
        ).count()
    }

    return render_template(
        "dashboard.html",
        campaigns=campaigns,
        stats=stats
    )


# =========================================================
# UPDATE CAMPAIGN STATUS
# =========================================================

@app.post(
    "/dashboard/<int:campaign_id>/status"
)
def status(campaign_id):

    campaign_record = Campaign.query.get_or_404(
        campaign_id
    )

    new_status = clean_text(
        request.form.get(
            "status",
            "Draft"
        ),
        40
    )

    if new_status not in CAMPAIGN_STATUSES:

        flash(
            "Invalid campaign status.",
            "danger"
        )

        return redirect(
            url_for("dashboard")
        )

    campaign_record.status = new_status

    try:

        db.session.commit()

        flash(
            "Campaign status updated successfully.",
            "success"
        )

    except Exception:

        db.session.rollback()

        flash(
            "Unable to update campaign status.",
            "danger"
        )

    return redirect(
        url_for("dashboard")
    )


# =========================================================
# API - CREATE LEAD
# =========================================================

@app.post("/api/lead")
def lead():

    data = request.get_json(
        silent=True
    ) or {}

    name = clean_text(
        data.get("name"),
        120
    )

    whatsapp = clean_whatsapp(
        data.get("whatsapp")
    )

    platform = clean_text(
        data.get("platform"),
        40
    )

    niche = clean_text(
        data.get("niche"),
        80
    )

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not name or not whatsapp:

        return jsonify(
            ok=False,
            message="Name and WhatsApp are required."
        ), 400

    # -----------------------------------------------------
    # CREATE LEAD
    # -----------------------------------------------------

    new_lead = Lead(
        name=name,
        whatsapp=whatsapp,
        platform=platform,
        niche=niche
    )

    db.session.add(
        new_lead
    )

    try:

        db.session.commit()

    except Exception:

        db.session.rollback()

        return jsonify(
            ok=False,
            message="Unable to save lead."
        ), 500

    return jsonify(
        ok=True,
        id=new_lead.id,
        message="Lead saved successfully."
    )


# =========================================================
# API - GET CAMPAIGNS
# =========================================================

@app.get("/api/campaigns")
def api_campaigns():

    campaigns = Campaign.query.order_by(
        Campaign.created_at.desc()
    ).all()

    results = []

    for campaign_record in campaigns:

        results.append({

            "id": campaign_record.id,

            "name": campaign_record.name,

            "platform": campaign_record.platform,

            "niche": campaign_record.niche,

            "username": campaign_record.username,

            "goal": campaign_record.goal,

            "status": campaign_record.status,

            "created_at": (
                campaign_record.created_at.isoformat()
                if campaign_record.created_at
                else None
            )

        })

    return jsonify(
        ok=True,
        campaigns=results
    )


# =========================================================
# API - GET LEADS
# =========================================================

@app.get("/api/leads")
def api_leads():

    leads = Lead.query.order_by(
        Lead.created_at.desc()
    ).all()

    results = []

    for lead_record in leads:

        results.append({

            "id": lead_record.id,

            "name": lead_record.name,

            "whatsapp": lead_record.whatsapp,

            "platform": lead_record.platform,

            "niche": lead_record.niche,

            "created_at": (
                lead_record.created_at.isoformat()
                if lead_record.created_at
                else None
            )

        })

    return jsonify(
        ok=True,
        leads=results
    )


# =========================================================
# API - CAMPAIGN STATISTICS
# =========================================================

@app.get("/api/stats")
def api_stats():

    return jsonify({

        "ok": True,

        "stats": {

            "campaigns": Campaign.query.count(),

            "active": Campaign.query.filter_by(
                status="Active"
            ).count(),

            "drafts": Campaign.query.filter_by(
                status="Draft"
            ).count(),

            "paused": Campaign.query.filter_by(
                status="Paused"
            ).count(),

            "completed": Campaign.query.filter_by(
                status="Completed"
            ).count(),

            "leads": Lead.query.count()
        }

    })


# =========================================================
# WHATSAPP CAMPAIGN CONTACT
# =========================================================

@app.route(
    "/whatsapp/<int:campaign_id>"
)
def campaign_whatsapp(campaign_id):

    campaign_record = Campaign.query.get_or_404(
        campaign_id
    )

    # Find the latest lead associated with the campaign
    lead_record = Lead.query.filter_by(
        name=campaign_record.name,
        platform=campaign_record.platform,
        niche=campaign_record.niche
    ).order_by(
        Lead.created_at.desc()
    ).first()

    if not lead_record or not lead_record.whatsapp:

        flash(
            "No WhatsApp number is available for this campaign.",
            "warning"
        )

        return redirect(
            url_for("dashboard")
        )

    message = (
        f"Hello {lead_record.name}, "
        f"we are following up regarding your "
        f"{campaign_record.platform} campaign "
        f"for the {campaign_record.niche} niche."
    )

    return redirect(
        whatsapp_url(
            lead_record.whatsapp,
            message
        )
    )


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(404)
def not_found(error):

    return render_template(
        "404.html"
    ), 404


@app.errorhandler(500)
def server_error(error):

    db.session.rollback()

    return render_template(
        "500.html"
    ), 500


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

with app.app_context():

    db.create_all()


# =========================================================
# APPLICATION START
# =========================================================

if __name__ == "__main__":

    # -----------------------------------------------------
    # IMPORTANT WINDOWS FIX
    #
    # Do NOT use:
    #
    # app.run(host="0.0.0.0", port=5000)
    #
    # We use localhost and port 8000 instead.
    # -----------------------------------------------------

    host = os.environ.get(
        "HOST",
        "127.0.0.1"
    )

    try:

        port = int(
            os.environ.get(
                "PORT",
                "8000"
            )
        )

    except ValueError:

        port = 8000

    print()
    print("=" * 60)
    print(" SOCIAL BOTS CAMPAIGN MANAGER")
    print("=" * 60)
    print(
        f" Server: http://{host}:{port}"
    )
    print(
        " Press CTRL+C to stop the server"
    )
    print("=" * 60)
    print()

    app.run(
        host=host,
        port=port,
        debug=True,
        use_reloader=True
    )