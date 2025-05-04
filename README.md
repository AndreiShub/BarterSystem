Barter platform built with Django, where users can post ads to trade items, browse other users’ ads, and propose exchanges.

## Features

- User registration and login/logout
- Post, edit, and delete advertisements
- Search ads by title, description, category, and condition
- View incoming and sent exchange proposals
- Propose exchanges
- Image upload and compression

## Setup Instructions

1. Clone the repository
git clone https://github.com/AndreiShub/BarterSystem.git
cd BarterSystem
2. Create a virtual environment and activate it
python -m venv venv
source venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
4. Apply migrations and run the server
python manage.py migrate
python manage.py runserver
Visit http://127.0.0.1:8000 in your browser
5. Run tests
pytest
