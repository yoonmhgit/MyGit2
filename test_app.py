import unittest
import json
import base64
from io import BytesIO
from PIL import Image
from app import app


class FlaskImageEditorTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
    def create_test_image(self):
        img = Image.new('RGB', (100, 100), color='red')
        buffered = BytesIO()
        img.save(buffered, format='JPEG')
        buffered.seek(0)
        return buffered
    
    def test_index_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>', response.data)
    
    def test_upload_image(self):
        test_image = self.create_test_image()
        
        data = {
            'image': (test_image, 'test.jpg')
        }
        
        response = self.client.post('/upload', 
                                   data=data,
                                   content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertTrue(json_data['success'])
        self.assertIn('image', json_data)
    
    def test_upload_no_file(self):
        response = self.client.post('/upload', data={})
        self.assertEqual(response.status_code, 400)
    
    def test_process_image(self):
        img = Image.new('RGB', (100, 100), color='blue')
        buffered = BytesIO()
        img.save(buffered, format='JPEG')
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        data = {
            'image': f'data:image/jpeg;base64,{img_str}',
            'adjustments': {
                'brightness': 1.2,
                'contrast': 1.1,
                'saturation': 1.0,
                'sharpness': 1.0,
                'temperature': 0,
                'hue': 0,
                'hsl_saturation': 0,
                'lightness': 0,
                'camera_profile': ''
            }
        }
        
        response = self.client.post('/process',
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertTrue(json_data['success'])
        self.assertIn('image', json_data)
    
    def test_process_with_camera_profile(self):
        img = Image.new('RGB', (100, 100), color='green')
        buffered = BytesIO()
        img.save(buffered, format='JPEG')
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        data = {
            'image': f'data:image/jpeg;base64,{img_str}',
            'adjustments': {
                'brightness': 1.0,
                'contrast': 1.0,
                'saturation': 1.0,
                'sharpness': 1.0,
                'temperature': 0,
                'hue': 0,
                'hsl_saturation': 0,
                'lightness': 0,
                'camera_profile': 'arri'
            }
        }
        
        response = self.client.post('/process',
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertTrue(json_data['success'])
    
    def test_download_image(self):
        img = Image.new('RGB', (100, 100), color='yellow')
        buffered = BytesIO()
        img.save(buffered, format='JPEG')
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        data = {
            'image': f'data:image/jpeg;base64,{img_str}'
        }
        
        response = self.client.post('/download',
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'image/jpeg')


if __name__ == '__main__':
    unittest.main()
