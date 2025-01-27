"""
Basic Booking-Reservation System Backend
----------------------------------------
This script initializes the Flask application and serves as the entry point to the backend system.
It provides:
- A welcome route for testing connectivity
- Blueprint registration for versioned API routes
"""


from dotenv import load_dotenv
from flask import Flask

from api.v1.app.routes import v1

load_dotenv( )


def create_app( ):
    """
        Create and configure the Flask application.

        Returns:
            Flask: Configured Flask app instance.
    """

    app = Flask( __name__ )

    @app.route( '/' )
    def hello_world( ):
        """
                Default route to confirm server status.
                Returns:
                    str: HTML response with server info.
        """

        return """
        <h1>Basic Booking-Reservation System Backend!</h1>

        <p>This is what a pretty python web looks like</p>
        """

    # Register API Blueprints
    app.register_blueprint( v1 )

    return app
