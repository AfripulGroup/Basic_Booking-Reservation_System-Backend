import mongoengine


class Resource( mongoengine.Document ):
    """ Resource document definition"""
    type = mongoengine.StringField( required = True, choices = [ 'room', 'hall' ] )
    number = mongoengine.StringField( required = True )
    description = mongoengine.StringField( required = False )
    capacity = mongoengine.DecimalField( required = False )

    meta = {
        'db_alias': 'core',
        'collection': 'resources',
    }


class User( mongoengine.Document ):
    """ User document definition """
    role = mongoengine.StringField( required = True, choices = [ 'admin', 'user' ], default = 'user' )
    email = mongoengine.StringField( required = True, unique = True )
    password = mongoengine.StringField( required = True, db_field = 'pwd' )
    first_name = mongoengine.StringField( required = True )
    last_name = mongoengine.StringField( required = True )
    bookings = mongoengine.ListField( mongoengine.ReferenceField( 'Booking' ) )

    meta = {
        'db_alias': 'core',
        'collection': 'users',
    }


class Booking( mongoengine.Document ):
    """ Resource Booking document definition """
    user = mongoengine.ReferenceField( 'User' )
    resource = mongoengine.ReferenceField( 'Resource' )
    start_date = mongoengine.DateField( required = True )
    end_date = mongoengine.DateField( required = True )  # format "%Y-%m-%d"

    meta = {
        'db_alias': 'core',
        'collection': 'bookings',
    }
