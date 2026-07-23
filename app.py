from flask import Flask, render_template, request, jsonify
import string
import math
import random

app = Flask(__name__)

MIN_LENGTH = 12
STRONG_PASSWORD_LENGTH = 16

def calculate_entropy(password):
    charset_size = 0
    if any(c in string.ascii_lowercase for c in password):
        charset_size += 26
    if any(c in string.ascii_uppercase for c in password):
        charset_size += 26
    if any(c in string.digits for c in password):
        charset_size += 10
    if any(c in string.punctuation for c in password):
        charset_size += len(string.punctuation)
    if any(c.isspace() for c in password):
        charset_size += 1
    return len(password) * math.log2(charset_size) if charset_size else 0

def generate_strong_password(length=STRONG_PASSWORD_LENGTH):
    while True:
        password = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(length))
        entropy = calculate_entropy(password)
        if (any(c in string.ascii_lowercase for c in password) and
            any(c in string.ascii_uppercase for c in password) and
            any(c in string.digits for c in password) and
            any(c in string.punctuation for c in password) and
            entropy >= 80):
            return password

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_password', methods=['POST'])
def check_password():
    password = request.form.get('password')
    if not password:
        return jsonify({'error': 'Password cannot be empty'}), 400

    entropy = calculate_entropy(password)
    strength = "Very Weak" if entropy < 28 else "Weak" if entropy < 36 else "Moderate" if entropy < 60 else "Strong" if entropy < 80 else "Very Strong"
    return jsonify({'entropy': entropy, 'strength': strength})

@app.route('/generate_password')
def generate_password():
    password = generate_strong_password()
    return jsonify({'password': password})

if __name__ == '__main__':
    app.run(debug=True)

