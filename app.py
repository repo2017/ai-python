from flask import Flask, render_template
import requests

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    # Call mock API endpoint and get the response
    response = requests.get('https://jsonplaceholder.typicode.com/posts/1')

    # Parse response JSON and get the 'title' field value
    title = response.json()['title']

    # Pass title value to the index.html template
    return render_template('index.html', title=title)
