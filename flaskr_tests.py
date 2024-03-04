import os
import app as flaskr
import unittest
import tempfile
import flask

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.testing = True
        self.app = flaskr.app.test_client()
        with flaskr.app.app_context():
            flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'No entries here so far' in rv.data

    def test_add(self):
        rv = self.app.post('/add', data=dict(
            title='<Hello>', category='<Category>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data

    def test_delete(self):
        rm = self.app.post('/delete', data=dict(
            title='<Hello>', category='<Category>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert b'No entries here so far' in rm.data
        assert b'&lt;Hello&gt;' not in rm.data
        assert b'<strong>HTML</strong> allowed here' not in rm.data

    def test_sort(self):
        self.app.post('/add', data=dict(
            title='<Hello>', category='<Category>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)

        rv = self.app.get('/?filter=<Category>')
        print(rv.data)
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data

        rb = self.app.get('/?filter=<notCategory>')
        assert b'No entries here so far' in rb.data
        assert b'&lt;Hello&gt;' not in rb.data
        assert b'<strong>HTML</strong> allowed here' not in rb.data


if __name__ == '__main__':
    unittest.main()