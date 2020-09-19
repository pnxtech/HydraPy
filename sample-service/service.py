from flask import Flask, request, jsonify, make_response

app = Flask(__name__)
server_version = '0.1.1'

@app.route('/', methods=['GET'])
def home():
  return 'HydraPy Sample Service version ' + server_version

@app.route('/v1/server/version', methods=['GET'])
def version():
  return make_response(jsonify({"version": server_version}), 200)

if __name__ == '__main__':
  app.run(debug=False, host='0.0.0.0', port=15000)
