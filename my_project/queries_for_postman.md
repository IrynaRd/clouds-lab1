Reviews:
POST: 
{
    "film_id": 1,
    "user_id": 2,
    "review_text": "Great movie!",
    "review_date": "2020-12-12",
}

GET: http://127.0.0.1:5000/reviews/film/1/user/2
    http://127.0.0.1:5000/reviews/film/1
    http://127.0.0.1:5000/reviews/user/1

PUT: http://127.0.0.1:5000/reviews/film/1/user/2
    {
        "review_text": "smth"
    }
DELETE: http://127.0.0.1:5000/reviews/film/1/user/2



Users:
POST: 
{
    "nick_name": "andriy",
    "email": "andriy@gmail.com",
    "registration_date": "2020-10-12"
}

GET: http://127.0.0.1:5000/users/
    http://127.0.0.1:5000/users/1
    http://127.0.0.1:5000/users/1/reviews

PUT: http://127.0.0.1:5000/users/1
    {
        "username": "andriy_updated",
        "email": "new@gmail.com"
    }

DELETE: http://127.0.0.1:5000/users/1

Films:

POST: http://127.0.0.1:5000/films/
{
    "title": "Title",
    "year": "2025",
    "description": "description 1",
    "budget": "120000.000"
}

GET: http://127.0.0.1:5000/films/
     http://127.0.0.1:5000/films/1
     http://127.0.0.1:5000/films/1/reviews
    

PUT: http://127.0.0.1:5000/films/1
{
    "title": "Title"
    "year": "2026"
    "description": "description 1"
    "budget": "120000,000"
}
{
    "description": "description 11"
}


DELETE: http://127.0.0.1:5000/films/11




