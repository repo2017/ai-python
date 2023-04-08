from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['POST'])
def add_text():
    data = request.get_json()
    input_text = data['input_text']
    data['output'] = f"The input text was: {input_text}"
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
