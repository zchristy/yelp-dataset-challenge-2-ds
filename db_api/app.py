from flask import Flask, request, jsonify
from flask import current_app, g
from flask_cors import CORS
from flask_caching import Cache
from decouple import config
from markdown2 import Markdown
import os

# Custom errors
from errors import InvalidUsage

# Logging
import logging

###########
###Setup###
###########

# Set database name
local_db_name = 'test.sqlite3'  # Change this or override with config.py file in instance/

#########################
###Application Factory###
#########################

# Create the application instance by calling create_app()
#     Example: app = create_app()

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    # If environment vairables not set, will default to development expected paths and names
    app.config.from_mapping(
        DEBUG=config('DEBUG', default=True),  # Make sure to change debug to False in production env
        SECRET_KEY=config('SECRET_KEY', default='dev'),  # CHANGE THIS!!!!
        DATABASE_URI=config('DATABASE_URI', 'sqlite:///' + os.path.join(os.getcwd(), local_db_name)),  # For in-memory db: default='sqlite:///:memory:'),
        LOGFILE=config('LOGFILE', os.path.join(app.instance_path, 'logs/debug.log')),
        CACHE_TYPE=config('CACHE_TYPE', 'simple'),  # Configure caching
        CACHE_DEFAULT_TIMEOUT=config('CACHE_DEFAULT_TIMEOUT', 300), # Long cache times probably ok for ML api
    )
    # Enable CORS extensions
    CORS(app)
    # Enable caching
    cache = Cache(app)

    #  Register database functions.  Will allow db.close() to run on instance teardown.
    import db
    db.init_app(app)

    ############
    ###Routes###
    ############
    @app.route('/')
    @cache.cached(timeout=2)  # Agressive cache timeout.
    def root():
        # Check if README.md exists and render as HTML if present
        if os.path.isfile('README.md'):
            return render_markdown('README.md')
        return "README.md Not Found.  This is API Main.  Use */api/predict/"

    @app.route('/api/query/', methods=['GET'])
    @cache.cached(timeout=10)  # Agressive cache timeout.
    def query():
        # Set Defaults
        defaults = None
        # Parse request
        if request.method == 'GET':
            if not 'search' in request.args:
                raise InvalidUsage(message="Search query not provided")

        # Check for hard-coded defaults.  Suggest loading defaults via function/env
        #   to activate/deactivate static response testing.
        if defaults is not None:
            search_request = defaults
        else:
            search_request = request.args['search']
        # Send search request to query generator, db handler
        query = NotImplemented

        return NotImplemented

    #############
    ###Logging###
    #############
    # Change logging.INFO to logging.DEBUG to get full logs.  Will be a crapload of information.
    logging.basicConfig(filename=app.config['LOGFILE'], level=logging.INFO)
    logging.getLogger('flask_cors').level = logging.INFO

    ############################
    ###Register Error Handles###
    ############################
    @app.errorhandler(InvalidUsage)
    def handle_invalid_usage(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    return app

def render_markdown(filename):
    # Convert markdown file to HTML for rendering
    with open(filename, 'rb') as f:
        html = Markdown().convert(f.read())

    return html


app = create_app()


if __name__ == "__main__":
    # Bind to PORT if defined, otherwise default to 5000.
    #  Run app.py.  Comment below out for Docker.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)