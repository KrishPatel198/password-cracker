from flask import Flask, render_template, request, redirect, url_for
import os
import base64
import itertools
import string

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

def brute_force_crack(password):
    """
    Attempt to crack the password using brute force.

    Args:
        password (str): The password to be cracked.

    Returns:
        str: The cracked password if found, otherwise None.
    """
    print(f"Attempting brute force crack for: {password}")
    characters = string.ascii_letters + string.digits
    for length in range(1, 4):  # Limiting to passwords of length 1 to 3 for demo purposes
        for guess in itertools.product(characters, repeat=length):
            guess = ''.join(guess)
            if guess == password:
                return guess
    return None

def dictionary_attack(password):
    """
    Attempt to crack the password using a dictionary attack.

    Args:
        password (str): The password to be cracked.

    Returns:
        str: The cracked password if found in the dictionary, otherwise None.
    """
    print(f"Attempting dictionary attack for: {password}")
    with open('dictionary.txt', 'r') as file:
        for line in file:
            if line.strip() == password:
                return password
    return None

def extract_encrypted_password(file_path):
    """
    Extract the encrypted password from the file.

    Args:
        file_path (str): The path to the file containing the encrypted password.

    Returns:
        str: The extracted encrypted password, or None if not found.
    """
    with open(file_path, 'r') as file:
        content = file.read()
    # Assuming the encrypted password is enclosed within <pwd>...</pwd>
    start = content.find('<pwd>') + len('<pwd>')
    end = content.find('</pwd>')
    if start != -1 and end != -1:
        encrypted_password = content[start:end]
        return encrypted_password
    return None

def decrypt_password(encrypted_password):
    """
    Decrypt the encrypted password using base64 decoding.

    Args:
        encrypted_password (str): The encrypted password to be decrypted.

    Returns:
        str: The decrypted password, or None if an error occurs.
    """
    try:
        decoded_bytes = base64.b64decode(encrypted_password)
        decrypted_password = decoded_bytes.decode('utf-8')
        return decrypted_password
    except Exception as e:
        print(f"Error decrypting password: {e}")
        return None

@app.route('/', methods=['GET'])
def index():
    """
    Render the main page of the application.

    Returns:
        str: The rendered HTML for the main page.
    """
    return render_template('index.html')

@app.route('/crack', methods=['POST'])
def crack():
    """
    Handle the form submission for cracking the password.

    Returns:
        str: The rendered HTML with the result of the password cracking.
    """
    result = None
    print("Form submitted")
    if 'file' not in request.files:
        print("No file part in request")
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        print("No selected file")
        return redirect(url_for('index'))
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        encrypted_password = extract_encrypted_password(file_path)
        if encrypted_password:
            print(f"Encrypted password extracted: {encrypted_password}")
            password = decrypt_password(encrypted_password)
            if password:
                print(f"Decrypted password: {password}")
                method = request.form['method']
                if method == 'brute_force':
                    result = brute_force_crack(password)
                elif method == 'dictionary':
                    result = dictionary_attack(password)
        else:
            print("No encrypted password found in the file")
    print(f"Result: {result}")
    return render_template('index.html', result=result)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True, use_reloader=False, port=5001)
