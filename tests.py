from flask import url_for, request
from app import app
import unittest

class FlaskTestCase(unittest.TestCase):

    # user can access the home page.
    def test_home_loads(self):
        tester = app.test_client(self)
        response = tester.get('/home', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # User can access the about page.
    def test_about_loads(self):
        tester = app.test_client(self)
        response = tester.get('/about', content_type='html/text')
        self.assertEqual(response.status_code, 200)
    
    # User receives 404 if attempting to goto an invalid location.
    def test_404(self):
        tester = app.test_client(self)
        response = tester.get('/location_not_here', content_type='html/text')
        self.assertEqual(response.status_code, 404)
    
    # User can access the login route
    def test_login_get(self):
        tester = app.test_client(self)
        response = tester.get('/login', content_type='html/text')
        self.assertTrue(b'Login' in response.data)
        self.assertEqual(response.status_code, 200)

    # Login works with correct credentials.
    def test_login_post_working(self):
        tester = app.test_client(self)
        response = tester.post('/login', data=dict(email='test@test.com', password='test'),
                                follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    # Login lets user know if the password is missing.
    def test_login_post_failing(self):
        tester = app.test_client(self)
        response = tester.post('/login', data=dict(email='test@test.com', password=''),
                                follow_redirects=True)
        self.assertTrue(b'This field is required' in response.data)
    
    # User can access the registration page.
    def test_register_get(self):
        tester = app.test_client(self)
        response = tester.get('/register', content_type='html/text')
        self.assertTrue(b'Register' in response.data)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()