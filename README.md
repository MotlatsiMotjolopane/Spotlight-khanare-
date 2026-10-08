# Multi Social Media Growth Bots

A multi-platform social media growth management system using Flask, SQLite, Bootstrap 5.3, JavaScript, Font Awesome and WhatsApp.

## Bots included
1. Instagram Growth Bot
2. TikTok Growth Bot
3. Facebook Growth Bot
4. YouTube Growth Bot
5. X Growth Bot
6. LinkedIn Growth Bot

Each bot uses the same core workflow:
- Select platform
- Select target niche
- Add profile/page/channel
- Define growth objective
- Create campaign
- Track campaign status
- Capture WhatsApp leads
- Manage campaigns from dashboard

## Safety / platform compliance
This project does not perform fake engagement, credential collection, mass-following, spam, scraping, botting of likes/comments, or unauthorized account actions. It is a campaign/lead-management bot framework. Production publishing and analytics should be connected through each platform's official API and permitted scopes.

## Run
Windows:
```bat
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

Dashboard: http://127.0.0.1:5000/dashboard

Change WhatsApp number in `templates/base.html`.

Footer branding: created by Sportlight (Khanare)
