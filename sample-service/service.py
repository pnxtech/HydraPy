from flask import Flask, request, jsonify, make_response
from hydra import Hydra

app = Flask(__name__)
server_version = '1.0.0'


@app.route('/', methods=['GET'])
def home():
    return 'HydraPy Sample Service version ' + server_version


@app.route('/v1/hydrapy/version', methods=['GET'])
def version():
    return make_response(jsonify({"version": server_version}), 200)


if __name__ == '__main__':
    Hydra.version()
    app.run(debug=False, host='0.0.0.0', port=15000)
