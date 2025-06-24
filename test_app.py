import unittest
import json
import tempfile
import os
import sys
from unittest.mock import patch, mock_open
from io import StringIO

# Import the app
from app import app, load_morse_mapping, morse_to_text, extract_flag, load_from_csv

class TestMorseDecoder(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and clear morse_mapping before each test"""
        self.app = app.test_client()
        self.app.testing = True
        
        # Clear morse_mapping before each test
        from app import morse_mapping
        morse_mapping.clear()
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['service'], 'Morse Code Decoder API')
        self.assertIn('decode', data['endpoints'])
        self.assertIn('health', data['endpoints'])
    
    def test_decode_morse_success(self):
        """Test successful Morse code decoding"""
        # Test message: "SOS DECODE CHALLENGE"
        morse_message = "... --- ... -.. . -.-. --- -.. . -.-. .... .- .-.. .-.. . -. --. ."
        
        response = self.app.post('/decode-morse',
                               data=json.dumps({'message': morse_message}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['decoded_text'], 'SOS DECODE CHALLENGE')
        self.assertFalse(data['flag_found'])
    
    def test_decode_morse_with_flag(self):
        """Test Morse code decoding with a hidden flag"""
        # Test message: "FLAG{test_flag_123}"
        morse_message = "..-. .-.. .- --. { - . ... - ..-. .-.. .- --. .---- ..--- ...-- }"
        
        response = self.app.post('/decode-morse',
                               data=json.dumps({'message': morse_message}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['flag_found'])
        self.assertIn('flag', data)
    
    def test_decode_morse_with_word_boundaries(self):
        """Test Morse code decoding with word boundaries (slashes)"""
        # Test message: "HELLO WORLD"
        morse_message = ".... . .-.. .-.. --- / .-- --- .-. .-.. -.."
        
        response = self.app.post('/decode-morse',
                               data=json.dumps({'message': morse_message}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['decoded_text'], 'HELLO WORLD')
    
    def test_decode_morse_numbers(self):
        """Test Morse code decoding with numbers"""
        # Test message: "12345"
        morse_message = ".---- ..--- ...-- ....- ....."
        
        response = self.app.post('/decode-morse',
                               data=json.dumps({'message': morse_message}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['decoded_text'], '12345')
    
    def test_decode_morse_special_characters(self):
        """Test Morse code decoding with special characters"""
        # Test message: "HELLO, WORLD!"
        morse_message = ".... . .-.. .-.. --- --..-- / .-- --- .-. .-.. -.. ---."
        
        response = self.app.post('/decode-morse',
                               data=json.dumps({'message': morse_message}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['decoded_text'], 'HELLO, WORLD!')
    
    def test_missing_message_field(self):
        """Test error handling for missing message field"""
        response = self.app.post('/decode-morse',
                               data=json.dumps({}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Missing', data['error'])
    
    def test_empty_message(self):
        """Test error handling for empty message"""
        response = self.app.post('/decode-morse',
                               data=json.dumps({'message': ''}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('empty', data['error'])
    
    def test_invalid_json(self):
        """Test error handling for invalid JSON"""
        response = self.app.post('/decode-morse',
                               data='invalid json',
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
    
    def test_unknown_morse_sequence(self):
        """Test handling of unknown Morse sequences"""
        # Test with an invalid Morse sequence
        morse_message = "... --- ... ... ... ... ..."  # Last sequence is invalid
        
        response = self.app.post('/decode-morse',
                               data=json.dumps({'message': morse_message}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('[', data['decoded_text'])  # Should contain brackets for unknown sequences
    
    def test_flag_patterns(self):
        """Test all flag pattern variations"""
        flag_patterns = [
            "FLAG{test_flag}",
            "flag{test_flag}",
            "CTF{test_flag}",
            "ctf{test_flag}",
            "FLAG:test_flag",
            "flag:test_flag"
        ]
        
        for flag in flag_patterns:
            with self.subTest(flag=flag):
                result = extract_flag(flag)
                self.assertEqual(result, flag)
    
    def test_no_flag_in_text(self):
        """Test text without flag patterns"""
        text = "This is just a normal message without any flags"
        result = extract_flag(text)
        self.assertIsNone(result)
    
    def test_load_from_csv(self):
        """Test loading Morse mapping from CSV"""
        csv_data = """char,morse
A,.-
B,-...
SPACE,/"""
        
        with patch('builtins.open', mock_open(read_data=csv_data)):
            load_from_csv(StringIO(csv_data))
            from app import morse_mapping
            self.assertEqual(morse_mapping['A'], '.-')
            self.assertEqual(morse_mapping['B'], '-...')
            self.assertEqual(morse_mapping[' '], '/')
    
    def test_morse_to_text_function(self):
        """Test the morse_to_text function directly"""
        # Load default mapping first
        load_morse_mapping()
        
        # Test simple word
        result = morse_to_text(".... . .-.. .-.. ---")
        self.assertEqual(result, "HELLO")
        
        # Test with word boundaries
        result = morse_to_text(".... . .-.. .-.. --- / .-- --- .-. .-.. -..")
        self.assertEqual(result, "HELLO WORLD")
    
    def test_configmap_loading(self):
        """Test loading from ConfigMap path"""
        csv_data = """char,morse
A,.-
B,-...
SPACE,/"""
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=csv_data)):
                load_morse_mapping()
                from app import morse_mapping
                self.assertIn('A', morse_mapping)
                self.assertIn('B', morse_mapping)
    
    def test_fallback_to_default_mapping(self):
        """Test fallback to default mapping when ConfigMap not found"""
        with patch('os.path.exists', return_value=False):
            load_morse_mapping()
            from app import morse_mapping
            # Should have loaded default mapping
            self.assertGreater(len(morse_mapping), 0)
            self.assertIn('A', morse_mapping)
            self.assertIn('Z', morse_mapping)
    
    def test_complex_morse_message(self):
        """Test a complex Morse message with mixed content"""
        # Test message: "HELLO WORLD 123!"
        morse_message = ".... . .-.. .-.. --- / .-- --- .-. .-.. -.. / .---- ..--- ...-- ---."
        
        response = self.app.post('/decode-morse',
                               data=json.dumps({'message': morse_message}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['decoded_text'], 'HELLO WORLD 123!')
    
    def test_morse_with_multiple_spaces(self):
        """Test Morse code with multiple spaces between letters"""
        # Test message: "A B C"
        morse_message = ".-   -...   -.-."
        
        response = self.app.post('/decode-morse',
                               data=json.dumps({'message': morse_message}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['decoded_text'], 'A B C')
    
    def test_morse_with_trailing_spaces(self):
        """Test Morse code with trailing spaces"""
        morse_message = ".... . .-.. .-.. ---   "
        
        response = self.app.post('/decode-morse',
                               data=json.dumps({'message': morse_message}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['decoded_text'], 'HELLO')

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2) 