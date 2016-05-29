from flask import Flask, request, jsonify, json
from mod_register import register
from logging.handlers import RotatingFileHandler
import logging

app = Flask(__name__)


@app.route('/register', methods=['POST'])
def register():
    try:
        project_id = request.args.get("project_id")
        project_env = request.args.get("project_env")
        instance_id = request.args.get("instance_id")
        mac_addr = request.args.get("mac_addr")

        if register.is_valid(project_id) and register.is_valid(instance_id) and register.is_valid(mac_addr) and register.is_valid(project_env):
            return register.register_on_consul(project_id, project_env, instance_id, mac_addr)
        else:
            raise ValueError("You need to have project_id, instance_id and mac_addr to register")

    except ValueError as e:
        return jsonify(
            {
                "error": e.message
            }
        )

@app.route('/health', methods=['GET'])
def health():
    return json.dumps(dict(status="OK"))


if __name__ == '__main__':
    handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run()
