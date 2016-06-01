from flask import Flask, request, jsonify, json
from mod_register import register
from mod_register import authenticator
from logging.handlers import RotatingFileHandler
import logging

app = Flask(__name__)


@app.route('/register-ec2', methods=['POST'])
def register_ec2():
    try:
        pkcs7_sig = request.args.get("pkcs7_sig")
        aws_identity_document = request.data
        project_id = request.args.get("project_id")
        project_env = request.args.get("project_env")

        if register.is_valid(project_id) and register.is_valid(pkcs7_sig) and register.is_valid(aws_identity_document) and register.is_valid(project_env):
            if authenticator.verify_pkcs7(pkcs7_sig, aws_identity_document):
                return register.register(pkcs7_sig, aws_identity_document, project_id, project_env)
            else:
                return ValueError("Invalid signature")
        else:
            raise ValueError("You need to have project_id, project_env, pkcs7_signature and EC2 identity document to register")

    except Exception as e:
        return jsonify(
            {
                "error": e.message
            }
        )


@app.route('/health', methods=['GET'])
def health():
    return json.dumps(dict(status="OK"))


if __name__ == '__main__':
    handler = RotatingFileHandler('avocado.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0',debug=True, port=5000)
