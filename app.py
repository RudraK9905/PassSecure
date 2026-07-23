import math
import secrets
import string
from flask import Flask, jsonify, render_template, request

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
        password = ''.join(
            secrets.choice(string.ascii_letters + string.digits + string.punctuation)
            for _ in range(length)
        )
        entropy = calculate_entropy(password)
        if (
            any(c in string.ascii_lowercase for c in password)
            and any(c in string.ascii_uppercase for c in password)
            and any(c in string.digits for c in password)
            and any(c in string.punctuation for c in password)
            and entropy >= 80
        ):
            return password


def analyze_password(password: str):
    if not password:
        return {
            "score": 0,
            "strength": "Very Weak",
            "feedback": "Enter a password to analyze it.",
            "entropy": 0,
            "criteria": [],
        }

    criteria = []
    if len(password) >= 12:
        criteria.append("Long enough")
    if any(c.islower() for c in password):
        criteria.append("Lowercase")
    if any(c.isupper() for c in password):
        criteria.append("Uppercase")
    if any(c.isdigit() for c in password):
        criteria.append("Number")
    if any(c in string.punctuation for c in password):
        criteria.append("Special character")

    repeated = len(set(password)) <= 2
    sequential = any(password[i:i + 3] == password[i + 1:i + 4] for i in range(len(password) - 3))
    common_pattern = password.lower() in {"password", "qwerty", "123456", "letmein", "admin"}
    has_all_types = all([
        any(c.islower() for c in password),
        any(c.isupper() for c in password),
        any(c.isdigit() for c in password),
        any(c in string.punctuation for c in password),
    ])
    unique_chars = len(set(password)) >= 8

    score = min(100, len(password) * 4 + len(criteria) * 10)
    if repeated:
        score -= 40
    if sequential:
        score -= 20
    if common_pattern:
        score -= 25
    if not has_all_types:
        score -= 10
    if not unique_chars:
        score -= 10

    if len(password) >= 16 and has_all_types and unique_chars and not repeated and not sequential and not common_pattern:
        score = 100
    elif len(password) >= 14 and has_all_types and unique_chars and not repeated and not sequential and not common_pattern:
        score = max(score, 90)
    elif len(password) >= 12 and has_all_types and unique_chars and not repeated and not sequential and not common_pattern:
        score = max(score, 80)

    score = max(0, min(100, score))

    if score < 20:
        strength = "Very Weak"
    elif score < 40:
        strength = "Weak"
    elif score < 60:
        strength = "Moderate"
    elif score < 80:
        strength = "Strong"
    else:
        strength = "Excellent"

    entropy = round(len(password) * (math.log2(26 + 26 + 10 + 32) if 26 + 26 + 10 + 32 > 0 else 0), 1)
    feedback = "This password is predictable and easy to crack." if score < 50 else "This password looks strong and resilient."

    return {
        "score": score,
        "strength": strength,
        "feedback": feedback,
        "entropy": entropy,
        "criteria": criteria,
    }


@app.route('/', methods=['GET', 'POST'])
def index():
    analysis = None
    if request.method == 'POST':
        analysis = analyze_password(request.form.get('password', ''))
    return render_template('index.html', analysis=analysis)


@app.route('/check_password', methods=['POST'])
def check_password():
    password = request.form.get('password')
    if not password:
        return jsonify({'error': 'Password cannot be empty'}), 400

    analysis = analyze_password(password)
    return jsonify(analysis)


@app.route('/generate_password')
def generate_password():
    password = generate_strong_password()
    return jsonify({'password': password})


@app.route('/generate', methods=['GET', 'POST'])
def generate():
    generated_password = None
    generated_analysis = None
    if request.method == 'POST':
        length = int(request.form.get('length', 16) or 16)
        length = max(8, min(32, length))
        lower = string.ascii_lowercase
        upper = string.ascii_uppercase
        digits = string.digits
        specials = string.punctuation
        alphabet = lower + upper + digits + specials

        while True:
            password_chars = [
                secrets.choice(lower),
                secrets.choice(upper),
                secrets.choice(digits),
                secrets.choice(specials),
            ]
            password_chars.extend(secrets.choice(alphabet) for _ in range(length - 4))
            generated_password = ''.join(password_chars)
            generated_analysis = analyze_password(generated_password)
            if generated_analysis['score'] >= 90:
                break

    return render_template(
        'index.html',
        generated_password=generated_password,
        generated_analysis=generated_analysis,
    )


if __name__ == '__main__':
    app.run(debug=True)
