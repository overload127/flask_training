import os
import first_blog
import unittest
import tempfile


class FirstBlogTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, first_blog.app.config['DATABASE'] = tempfile.mkstemp()
        first_blog.app.config['TESTING'] = True
        self.app = first_blog.app.test_client()
        first_blog.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(first_blog.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'Unbelievable. No entries here so far' in rv.data

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        rv = self.login('admin', '1234')
        assert b'You were logged in' in rv.data
        rv = self.logout()
        assert b'You were logged out' in rv.data
        rv = self.login('admin322', '1234')
        assert b'Invalid username' in rv.data
        rv = self.login('admin', '12345678')
        assert b'Invalid password' in rv.data

    def test_messages(self):
        self.login('admin', '1234')
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert b'New entry was successfully posted' in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data


if __name__ == '__main__':
    unittest.main()
