import unittest
import sqlite3
from io import BytesIO
from app import app

class TestCrowdCounting(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the test client and initialize the database."""
        cls.client = app.test_client()

        conn = sqlite3.connect('instance/crowd-counting.db')
        c = conn.cursor()
        c.execute('INSERT INTO models (name) VALUES (?)', ('model_1',))
        c.execute('INSERT INTO crowdCounting (original_url, annotated_url, averageCountPerFrame, model_id) VALUES (?, ?, ?, ?)', 
                ('http://localhost:10000/container/file1.jpg', 
                'http://localhost:10000/container/annotated_file1.jpg', 
                10, 1))
        conn.commit()
        conn.close()

    def test_get_all_data_success(self):
        """Test retrieval of all data from the database."""
        response = self.client.get('/archive')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json), 0)
        self.assertIn('id', response.json[0])
        self.assertIn('original_url', response.json[0])

if __name__ == '__main__':
    unittest.main()
