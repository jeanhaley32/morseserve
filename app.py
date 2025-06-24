from flask import Flask, request, jsonify
import csv
import io
import os
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Morse code mapping from ConfigMap
morse_mapping = {}

def load_morse_mapping():
    """Load Morse code mapping from ConfigMap CSV file"""
    config_path = "/etc/morse-code/morse.csv"
    
    # Try to load from ConfigMap path first
    if os.path.exists(config_path):
        logger.info(f"Loading Morse mapping from ConfigMap: {config_path}")
        with open(config_path, 'r') as file:
            load_from_csv(file)
    else:
        # Fallback to default mapping for development
        logger.info("ConfigMap not found, using default Morse mapping")
        default_mapping = """char,morse
A,.-
B,-...
C,-.-.
D,-..
E,.
F,..-.
G,--.
H,....
I,..
J,.---
K,-.-
L,.-..
M,--
N,-.
O,---
P,.--.
Q,--.-
R,.-.
S,...
T,-
U,..-
V,...-
W,.--
X,-..-
Y,-.--
Z,--..
0,-----
1,.----
2,..---
3,...--
4,....-
5,.....
6,-....
7,--...
8,---..
9,----.
.,.-.-.-
,,--..--
?,..--..
!,---.
/,--..-.
(,-.--.
),-.--.-
&,.-...
=,-...-
+,.-.-.
-,....-
_,..--.-
",.-..-.
:,---...
;,.-.-.-
@,.--.-.
SPACE,/"""
        
        csv_file = io.StringIO(default_mapping)
        load_from_csv(csv_file)

def load_from_csv(file):
    """Load Morse mapping from CSV file"""
    reader = csv.DictReader(file)
    for row in reader:
        char = row['char'].strip()
        morse = row['morse'].strip()
        if char == 'SPACE':
            morse_mapping[' '] = morse
        else:
            morse_mapping[char] = morse
    # Debug: print some loaded mappings
    logger.info(f"Loaded mappings: A->{morse_mapping.get('A', 'NOT FOUND')}, E->{morse_mapping.get('E', 'NOT FOUND')}, S->{morse_mapping.get('S', 'NOT FOUND')}, COLON->{morse_mapping.get(':', 'NOT FOUND')}")

def morse_to_text(morse_message):
    """Convert Morse code to text"""
    # Create reverse mapping
    reverse_mapping = {v: k for k, v in morse_mapping.items()}
    
    # Debug: print the reverse mapping to see what we have
    logger.info(f"Reverse mapping keys: {list(reverse_mapping.keys())[:10]}...")
    
    # Split by word boundaries (slashes)
    words = morse_message.split(' / ')
    
    decoded_words = []
    for word in words:
        # Split by letter boundaries (spaces)
        letters = word.split(' ')
        decoded_letters = []
        
        for letter in letters:
            if letter in reverse_mapping:
                decoded_letters.append(reverse_mapping[letter])
            else:
                # If we can't decode a letter, keep the original
                decoded_letters.append(f"[{letter}]")
        
        decoded_words.append(''.join(decoded_letters))
    
    return ' '.join(decoded_words)

def extract_flag(text):
    """Extract flag pattern from decoded text"""
    # Look for common flag patterns
    flag_patterns = [
        r'FLAG\{[^}]+\}',  # FLAG{...}
        r'flag\{[^}]+\}',  # flag{...}
        r'FLAG:[^\\s]+',   # FLAG: ...
        r'flag:[^\\s]+',   # flag: ...
        r'CTF\{[^}]+\}',   # CTF{...}
        r'ctf\{[^}]+\}',   # ctf{...}
    ]
    
    for pattern in flag_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with basic info"""
    return jsonify({
        "service": "Morse Code Decoder API",
        "endpoints": {
            "decode": "POST /decode-morse",
            "health": "GET /health"
        }
    }), 200

@app.route('/decode-morse', methods=['POST'])
def decode_morse():
    """Decode Morse code message and extract flag"""
    try:
        # Get JSON input
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "Missing 'message' field in JSON body"}), 400
        
        morse_message = data['message']
        
        if not morse_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        logger.info(f"Received Morse message: {morse_message}")
        
        # Decode Morse to text
        decoded_text = morse_to_text(morse_message)
        logger.info(f"Decoded text: {decoded_text}")
        
        # Extract flag
        flag = extract_flag(decoded_text)
        
        response = {
            "decoded_text": decoded_text,
            "flag_found": flag is not None
        }
        
        if flag:
            response["flag"] = flag
            logger.info(f"Flag found: {flag}")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    # Load Morse mapping on startup
    load_morse_mapping()
    logger.info(f"Loaded {len(morse_mapping)} Morse code mappings")
    
    # Get port from environment variable (for OpenShift)
    port = int(os.environ.get('PORT', 8080))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False) 