from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

# Mock API call that returns some data
def example_api():
    return {"content": "some response"}

# Route that serves the HTML page with the text field
@app.route('/start', methods=['GET'])
def start():
    return render_template('index.html')

# Endpoint that is called when the text field is submitted
@app.route('/enrich', methods=['POST'])
def enrich():
    # Get the value of the text field
    text = request.form['text']

    # Call the mock API
    response = example_api()

    # Enrich the response and return it as JSON
    final_content = "enriched {}".format(response['content'])
    return jsonify({"finalcon": final_content})

if __name__ == '__main__':
    app.run()
