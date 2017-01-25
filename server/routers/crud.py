"""CrudRouter available for flask inorder to reduce work.

NOTES:
- only works with postgres.
- barely sanitizes
"""

from server.util.postgres_crud import PostgresCrud
from server.util.postgres_runner import sanitize_value


class CrudRouter:
    """Crud Router to make everything easier."""

    def __init__(
        self, postgresCrud, methods=None
    ):
        """Crud router meant to reduce your cruding work.

        Requires as arguments
            1. a PostgresCrud instance available from server.util.postgres_crud
            2. optional { valuesFromForm : function }
                but this is only used with custom form parsing
        """
        self.methods = methods
        if not isinstance(postgresCrud, PostgresCrud):
            raise ValueError(
                "needs a postgres crud interface as its first argument"
            )

    def handleRequest(self, request, targetID=None):
        """The app should call this method to handle httpRequests."""
        method = request.method
        if method == "post":  # create
            return self.__create(
                __retrieveValuesFromForm(
                    self.methods,
                    self.table_keys,
                    request.form
                )
            )

        if method == "get":  # request
            if targetID is None:
                return self.__pagination(request.args)
            return self.__request(targetID)

        if method == "put":  # update
            if targetID is None:
                raise ValueError('A targetID is required')
            return self.__update(
                targetID,
                __retrieveValuesFromForm(
                    self.methods,
                    self.table_keys,
                    request.form
                )
            )

        if method == "delete":  # delete
            if targetID is None:
                raise ValueError('A targetID is required')
            return self.__delete(targetID)

        raise ValueError('Invalid Method')


def __retrieveValuesFromForm(methods, table_keys, form):
    fn = methods.get("valuesFromForm", None)
    if fn is not None:
        return fn(form)
    dic = {}
    for key in table_keys:
        if key in form:
            dic[key] = sanitize_value(form[key])
    return dic
