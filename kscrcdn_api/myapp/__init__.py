from flask import Flask


def create_app(debug=False):
    """
    Create an application
    :param debug: bool
    :return: app object
    """
    app = Flask('kscrcdn')
    app.debug = debug
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    # import blueprint
    from .system import system
    from .spec import spec
    # register blueprint
    app.register_blueprint(system, url_prefix='/v1/')
    app.register_blueprint(spec, url_prefix='/v1/spec/')
    return app
