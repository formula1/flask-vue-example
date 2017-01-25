"""Necessities for flask_login."""

import flask_login


class User(flask_login.UserMixin):
    """User class necexxary for flask_login."""

    pass


class UserProvider:
    """To be used with flask_login and flask."""

    def __init__(self, postgresCrud):
        """Arg is a PostgresCrud instance provides a way to get the user."""
        self.postgresCrud = postgresCrud

    def validate_username(self, username):
        """Validate a username."""
        if len(username) < 5:
            raise "Username too small"
        users = self.postgresCrud.where("username", username)
        if len(users) > 0:
            raise "User already exists"
        return True

    def register_user(self, name, password):
        """Register the user."""
        print "registering user"
        self.validate_username(name)
        id = self.postgresCrud.create(
            {
                "username": name,
                "password": password
            }
        )
        print "tidype: " + str(id)
        return self.postgresCrud.request(id)

    def load_user(self, name):
        """Load a user."""
        users = self.postgresCrud.where("username", name)
        if (len(users) == 0):
            return
        user = self.userdata_to_user(users[0])
        return user

    def userdata_to_user(userdata):
        """Turn userdata into a user."""
        user = User()
        user.id = userdata._id
        return user

    def load_authenticated_user(self, name, password):
        """Load and authenticate a user."""
        users = self.postgresCrud.where("username", name)
        if (len(users) == 0):
            return
        userdata = users[0]
        if userdata.password == password:
            return userdata

    def authenticate_user(self, name, password):
        """Load and authenticate a user."""
        users = self.postgresCrud.where("username", name)
        if (len(users) == 0):
            return
        userdata = users[0]
        user = self.userdata_to_user(userdata)
        user.is_authenticated = userdata.password == password
        return user
