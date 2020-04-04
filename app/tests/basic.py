import os
import unittest

from config import basedir
from news import app, db
from app.models import Users

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/testdb'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
         with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_user(self):
        with app.app_context():
            u = Users(username='john', password_hash="1234", email="test@gmail.com", number="0987654321")
            db.session.add(u)
            db.session.commit()

if __name__ == '__main__':
    unittest.main()