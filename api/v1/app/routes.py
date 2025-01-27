import base64
from functools import wraps

from flask import request, jsonify, Blueprint

from api.v1.app.services import service

v1 = Blueprint( 'v1', __name__ )


def role_required( role ):
    """ Role-based access decorator """

    def decorator( f ):
        @wraps( f )
        def decorated_function( *args, **kwargs ):
            session_id = request.headers.get( "X-Token" )
            if not session_id:
                return jsonify( { "error": "Kindly Provide Your Access Token" } ), 401
                # Unauthorized if no session_id found

            user = service.get_user_from_session_id( session_id )
            if not user:
                return jsonify( { "error": "Access Token Not Found or Expired" } ), 404

            if user.role != role:
                return jsonify( { "error": "Authorized access only" } ), 401

            return f( *args, **kwargs )  # Call the original function

        return decorated_function

    return decorator


@v1.route( '/register', methods = [ 'POST' ], strict_slashes = False )
def signup( ):
    """
    Register a new user.
    :return: JSON response indicating success or failure of user registration.
    """

    try:
        data =request.form.to_dict() or request.get_json( )
        required_fields = { 'first_name', 'last_name', 'email', 'password' }
        if not all( field in data and data[ field ] for field in required_fields ):
            return jsonify( { 'error': 'Missing required fields' } ), 400

        user_id, email = service.create_user( data )
        return jsonify( { 'message': 'User created', 'id': user_id, 'email': email } ), 201
    except Exception as e:
        return jsonify( { 'error': str( e ) } ), 400


@v1.route( '/login', methods = [ 'POST' ], strict_slashes = False )
def login( ):
    """
    Log in a user and return an access token.
    :return: JSON response with the access token or error message.
    """
    try:
        auth_header = request.headers.get( 'Authorization' )
        if auth_header and auth_header.startswith( 'Basic ' ):
            credentials = base64.b64decode( auth_header.split( " " )[ 1 ] ).decode( 'utf-8' )
            email, password = credentials.split( ':' )
        else:
            # Fall back to form data if Authorization header is not present
            email = request.form.get( "email" )
            password = request.form.get( "password" )

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        token = service.login( email, password )

        return jsonify( { 'message': 'Login successful', 'token': token } ), 200
    except (TypeError, ValueError, base64.binascii.Error):
        return jsonify( { "error": "Invalid authorization format" } ), 401
    except Exception as e:
        return jsonify( { 'error': str( e ) } ), 500


@v1.route( '/resources', methods = [ 'GET' ], strict_slashes = False )
@role_required( 'user' )
def all_resources( ):
    """
    Fetch all available resources.
    :return: JSON response with the list of resources.
    """
    try:
        resources = service.list_resources( )
        return jsonify( { 'resources': resources } ), 200
    except Exception as e:
        return jsonify( { 'error': str( e ) } ), 500


@v1.route( '/resources', methods = [ 'POST' ], strict_slashes = False )
@role_required( 'admin' )
def new_resource( ):
    """
    Create a new resource.
    :return: JSON response with the new resource ID or error message.
    """
    try:
        data = request.form.to_dict( ) or request.get_json( )
        required_fields = { 'type', 'number' }

        if not all( field in data and data[ field ] for field in required_fields ):
            return jsonify( { "error": "Missing required fields" } ), 400

        resource_id = service.create_resource( data )
        return jsonify( { 'message': 'Resource created', 'id': resource_id } ), 201
    except Exception as e:
        return jsonify( { 'error': str( e ) } ), 500


@v1.route( '/booking', methods = [ 'POST' ], strict_slashes = False )
@v1.route( '/booking/<resource_id>', methods = [ 'POST' ], strict_slashes = False )
@role_required( 'user' )
def booking( resource_id = None ):
    """
    Book a resource.
    :param resource_id: ID of the resource to book.
    :return: JSON response indicating the status of the booking.
    """
    try:
        data = request.form.to_dict( ) or request.get_json( )
        if not data.get( 'resource' ):
            data[ 'resource' ] = resource_id

        required_fields = { 'resource_id', 'start_date', 'end_date' }

        if not all( field in data and data[ field ] for field in required_fields ):
            return jsonify( { "error": "Missing required fields" } ), 400

        status = service.book_resource( data )
        return jsonify( status ), 201

    except Exception as e:
        return jsonify( { "error": str( e ) } ), 400


@v1.route( '/booking', methods = [ 'GET' ], strict_slashes = False )
@role_required( 'user' )
def list_booking( ):
    """
    List all bookings for the logged-in user.
    :return: JSON response with the list of bookings.
    """
    try:
        bookings = service.list_bookings( )
        return jsonify( { 'bookings': bookings } ), 200
    except Exception as e:
        return jsonify( { 'error': str( e ) } ), 500
