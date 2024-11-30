import unittest
import sqlite3
from io import BytesIO
from app import app

class TestCrowdCounting(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the test client and initialize the database."""
        app.testing = True
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

    def test_get_specific_record(self):
        """Test retrieval of a specific record by ID."""
        response = self.client.get('/get/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.json)
        self.assertIn('original_url', response.json)

    def test_get_specific_record_not_found(self):
        """Test retrieval of a non-existent record."""
        response = self.client.get('/get/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)


    def test_upload_file_no_file(self):
        """Test upload endpoint with no file provided."""
        response = self.client.post('/upload', data={}, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)

    def test_count_people_model_not_found(self):
        """Test counting with a non-existent model."""
        response = self.client.put('/count/1', json={'model_id': 999})
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)

    def test_count_people_record_not_found(self):
        """Test counting with a non-existent record."""
        response = self.client.put('/count/999', json={'model_id': 1})
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)

    def test_get_model_names(self):
        """Test retrieval of all model names."""
        response = self.client.get('/models')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json), 0)
        self.assertIn('id', response.json[0])
        self.assertIn('name', response.json[0])

    def test_get_model_names_empty(self):
        """Test retrieval of model names when no models exist."""
        # Clear models table
        conn = sqlite3.connect('instance/crowd-counting.db')
        c = conn.cursor()
        c.execute('DELETE FROM models')
        conn.commit()
        conn.close()

        response = self.client.get('/models')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 0)

if __name__ == '__main__':
    unittest.main()