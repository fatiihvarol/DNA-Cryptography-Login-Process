from flask import Flask, request, render_template, redirect, url_for, flash
import itertools
from PIL import Image
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # flash messages için gereklidir

# DNA combinations generation
def generate_dna_combinations():
    bases = ['A', 'C', 'G', 'T']
    return [''.join(comb) for comb in itertools.product(bases, repeat=4)]

dna_combinations = generate_dna_combinations()

# In-memory user storage
users = {}

# Function to convert image to DNA sequences
def image_to_dna(image_path):
    img = Image.open(image_path)
    img = img.convert('RGB')
    dna_sequence = []

    for pixel in img.getdata():
        r, g, b = pixel
        dna_sequence.append(dna_combinations[r])
        dna_sequence.append(dna_combinations[g])
        dna_sequence.append(dna_combinations[b])

    return dna_sequence

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        photo = request.files['photo']

        # Save photo
        photo_path = f'static/photos/{username}.png'
        photo.save(photo_path)
        print(f"Photo saved at: {photo_path}")

        # Convert photo to DNA sequence
        dna_sequence = image_to_dna(photo_path)

        # Store user data
        users[username] = {
            'dna_sequence': dna_sequence
        }
        print(f"User {username} registered with DNA sequence.")

        flash('Registration successful!', 'success')
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    photo = request.files['photo']

    if username in users:
        # Save the uploaded photo
        photo_path = f'static/photos/{username}_login.png'
        photo.save(photo_path)
        print(f"Photo saved at: {photo_path}")

        # Convert photo to DNA sequence
        dna_sequence = image_to_dna(photo_path)
        print(f"Generated DNA sequence for login: {dna_sequence}")

        # Check if the DNA sequence matches
        if dna_sequence == users[username]['dna_sequence']:
            print(f"Login successful for user: {username}")
            flash('Login successful!', 'success')
            return redirect(url_for('welcome', username=username))
        else:
            print(f"Login failed for user: {username}, DNA sequence does not match.")
            flash('Login failed, DNA sequence does not match.', 'error')
            return redirect(url_for('index'))
    else:
        print(f"User {username} does not exist.")
        flash('User does not exist.', 'error')
        return redirect(url_for('index'))

@app.route('/welcome/<username>')
def welcome(username):
    return render_template('welcome.html', username=username)

if __name__ == '__main__':
    if not os.path.exists('static/photos'):
        os.makedirs('static/photos')
    app.run(debug=True)
