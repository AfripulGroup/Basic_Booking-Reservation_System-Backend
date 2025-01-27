"""
Service Layer for Booking-Reservation System
--------------------------------------------
This module provides business logic for handling:
- User management (creation, authentication)
- Resource management (listing, creation)
- Booking operations (reservations, conflicts, and availability)
"""
import json
from datetime import date, datetime
from os import getenv
from uuid import uuid4

import bcrypt
import mongoengine
import redis
from bson import ObjectId

from schemas import User, Booking, Resource

# Initialize Redis connection
r = redis.Redis(host=getenv("DB_HOST"))


class Services:

    def __init__( self ):
        """
        Initialize Services class, connecting to MongoDB.
        """
        mongoengine.connect(
            db = getenv( 'DB_NAME' ),
            host = getenv( 'DB_HOST' ),
            alias = getenv( 'DB_ALIAS' )
        )
        self.__user_id = None


    def create_user( self, data: dict ) -> tuple:
        """
        Create a new user.
        :param data: User data containing email, password, first_name, and last_name.
        :return: User ID and email of the newly created user.
        """

        try:
            email = data[ 'email' ]
            if self.user_exists( email ):
                raise ValueError( 'User already exists' )

            hashed_password = self._hash_password( data[ 'password' ] )

            user = User(
                email = email,
                password = hashed_password,
                first_name = data[ "first_name" ],
                last_name = data[ "last_name" ],
                role = data.get( "role" ),
            )
            user.save( )

            return str( user.id ), email
        except Exception as e:
            raise RuntimeError( f"Failed to create user: {e}" )

    def login( self, email, password ) -> str:
        """
        Authenticate a user and grant an access token
        :param email: User's email.
        :param password: User's password.
        :return: Access ID (token).
        """
        try:
            # fetch user
            user = self.find_user( email )
            if not user or not self.verify_password( user, password ):
                raise ValueError( "Invalid email or password" )

            session_id = str( uuid4( ) )
            key = f"auth_{session_id}"
            r.set( key, str( user.id ) )
            return session_id
        except Exception as e:
            raise RuntimeError( f"Login failed: {e}" )

    def get_user_from_session_id( self, session_id: str ) -> User or None:
        """
        Retrieve a user by access ID.
        :param session_id: Authentication Token.
        :return: User instance or None if not found.
        """
        try:
            # query redis database
            user_id = r.get( f"auth_{session_id}" )
            if not user_id:
                return None
            # Hold on to user id
            self.__user_id = user_id.decode( 'utf-8' )
            return User.objects( id = ObjectId( self.__user_id ) ).first( )
        except Exception as e:
            raise RuntimeError( f"Error getting user from"
                             f" session id {session_id}: {str( e )}" )

    def verify_password( self, user: User, password: str ) -> bool:
        """
        Verify if a given password matches the stored hash.
        :param user: User instance.
        :param password: Plaintext password.
        :return: True if password matches, False otherwise.
        """
        return bcrypt.checkpw( password.encode( 'utf-8' ), user.password.encode( 'utf-8' ) )

    def _hash_password( self, password: str ) -> str:
        """
        Hash a password securely.
        :param password: Plaintext password.
        :return: Hashed password.
        """
        return bcrypt.hashpw( password.encode( 'utf-8' ), bcrypt.gensalt( ) ).decode( 'utf-8' )

    def user_exists( self, email ) -> bool:
        """
        Check if a user exists by email.
        :param email: User's email.
        :return: True if user exists, False otherwise.
        """
        return User.objects( email = email ).first( ) is not None

    def find_user( self, email ) -> User:
        """
        Retrieve a user by their email.
        :param email: The user's email.
        :return: The user object or None.
        """
        return User.objects( email = email ).first( )

    def list_resources( self ) -> list[ Resource ]:
        """
        List all available resources.
        :return: A list of resources.
        """

        resources = Resource.objects.all( )
        return json.loads( resources.to_json( ) )

    def create_resource( self, data: dict ) -> str:
        """
        Create a new resource.
        :param data: Resource data.
        :return: The resource ID of the created resource.
        """

        resource = Resource( **data )
        resource.save( )
        return str( resource.id )

    def book_resource( self, data: dict ) -> dict:
        """
        Book a resource for specified dates.
        :param data: Booking details including resource ID, start date, and end date.
        :return: Booking confirmation or available dates if conflicts exist.
        """

        today = date.today( )
        # today = datetime.strptime( str( today ), '%Y-%m-%d' ).date( )

        new_start = datetime.strptime( data[ 'start_date' ], "%Y-%m-%d" ).date( )
        new_end = datetime.strptime( data[ 'end_date' ], "%Y-%m-%d" ).date( )

        if today > new_start or today > new_end:
            raise Exception( 'You cannot book a past date' )

        booking = Booking.objects( resource = data[ 'resource' ], start_date = new_start, end_date = new_end ).only(
            'start_date', 'end_date' )

        if booking:
            raise Exception( f'The resource is already booking from {new_start} to {new_end}' )

        # Fetch all open reservations
        booking = (Booking.objects( resource = data[ 'resource' ], start_date__gte = today )
                   .only( 'start_date', 'end_date' ).order_by( 'start_date' ))

        if booking:
            # Get available dates in between future reservations
            blocked = json.loads( booking.to_json( ) )
            size = len( blocked )
            available_dates = [ ]

            # To get the number of conflicting reservations:
            conflicts = 0

            for i in range( len( blocked ) ):
                # Note the start and end days of future open active reservations
                curr_start = (blocked[ i ][ "start_date" ][ '$date' ])  # 1741132800000 integer type
                curr_start = datetime.fromtimestamp( curr_start / 1000 ).date( )

                # To shorten the statements above:
                curr_end = datetime.fromtimestamp( blocked[ i ][ "end_date" ][ '$date' ] / 1000 ).date( )

                # check reservations that are active when the new starts or ends
                # This means the room or hall can not be booked for any of those days
                if curr_start <= new_start < curr_end or curr_start <= new_end < curr_end:
                    conflicts += 1

                if size - i == 1:
                    continue

                next_start = datetime.fromtimestamp( blocked[ i + 1 ][ "start_date" ][ '$date' ] / 1000 ).date( )
                # next_end = datetime.fromtimestamp(blocked[i + 1]["end_date"]['$date'] / 1000).date()

                if curr_end <= next_start:
                    available_dates.append(
                        (curr_end.strftime( '%A, %d %B, %Y' ), next_start.strftime( '%A, %d %B, %Y' )) )

            if conflicts == 0:
                booking = Booking( user = self.__user_id, **data ).save( )
                return { "message": "Booking successful", "booking_id": str( booking.id ), }
            else:
                # return available dates in between booked dates and after booked dates
                return {
                    "message": f"{conflicts} Conflicts found! These are the available timeframes. "
                               f"Beyond these, there are no open reservations.",
                    "available_dates": available_dates }

            # print(available_dates)  # print(conflicts)

            # print('Get available dates in between future reservations')  # self.get_available_dates(blocked)

        else:
            booking = Booking( user = self.__user_id, **data ).save( )
            return { "message": "Booking successful", "booking_id": str( booking.id ), }


    """
        # Optimized logic for overlapping dates
        
        overlapping_bookings = Booking.objects(
            resource = data[ 'resource' ],
            start_date__lte = new_end,
            end_date__gte = new_start
        )

        if overlapping_bookings:
            return {
                "message": "Conflicts found. Resource is unavailable during the specified dates."
            }

        booking = Booking( user = self.__user_id, **data )
        booking.save( )
        return { "message": "Booking successful.", "booking_id": str( booking.id ) }
        """

    def list_bookings( self ) -> list[Booking]:
        """
        List all future bookings for authenticated user.
        :return: A list of bookings.
        """

        today = date.today( )
        bookings = Booking.objects( user = self.__user_id, end_date__gte = today )
        return [ convert_json( booking ) for booking in bookings ]

service = Services( )


def convert_json( booking ):
    """ Convert booking object to JSON """
    booking_dict = json.loads( booking.to_json( ) )
    booking_dict[ 'start_date' ] = booking[ 'start_date' ].isoformat( )
    booking_dict[ 'end_date' ] = booking[ 'end_date' ].isoformat( )
    return booking_dict
