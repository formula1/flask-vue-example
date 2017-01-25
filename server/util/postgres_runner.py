"""A helper to make running postgres comands simpler."""
import psycopg2


class PostgresRunner:
    """A helper to make running postgres comands simpler."""

    def __init__(self, connectionConfig):
        """Require a valid psycopg2 connection config."""
        self.connectionConfig = connectionConfig

    def runCommands(self, commands):
        """Run all of the given commands and returns the values."""
        connectionConfig = self.connectionConfig
        results = []
        error = None
        conn = None
        try:
            params = connectionConfig
            conn = psycopg2.connect(params)
            cur = conn.cursor()
            for command in commands:
                cur.execute(command)
                try:
                    results.append(cur.fetchall())
                except psycopg2.ProgrammingError as fetchError:
                    print("error: " + str(fetchError))
                    if str(fetchError) == "no results to fetch":
                        results.append(None)
                    else:
                        raise fetchError
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as databaseError:
            error = databaseError
        finally:
            if conn is not None:
                conn.close()
        if error is None:
            return results
        for command in commands:
            print(command)
        print(error)
        raise error


def sanitize_value(value):
    """Sanitize a value for storage into postgres."""
    if value.lower() == "true":
        return value.lower()
    if value.lower() == "false":
        return value.lower()
    try:
        return str(float(value))
    except ValueError:
        return "\'"+value.replace("\\", "\\\\").replace("\'", "\\\'")+"\'"
