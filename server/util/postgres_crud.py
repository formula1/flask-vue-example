"""A basic class to perform postgres operations."""

from string import Template
from .postgres_runner import sanitize_value

create_template = Template(
    """
        INSERT INTO $tablename($columns) values($values) RETURNING _id;
    """
)

pagination_template = Template(
    """
        SELECT * FROM $tablename
        WHERE $comparison
        ORDER BY $sortKey $asc
        LIMIT $limit
    """
)

request_template = Template(
    """
        SELECT * FROM $tablename WHERE _id=($targetID);
    """
)

update_template = Template(
    """
        UPDATE $tablename
        SET ($columns) = ($values)
        WHERE _id=($targetID)
        RETURNING id;
    """
)

delete_template = Template(
    """
        DELETE FROM $tablename WHERE _id=($targetID)
    """
)


class PostgresCrud:
    """Crud class for easy creates, retrieves, updates and deletes."""

    def __init__(self, postgresRunner, tablename, table_columns):
        """Crud router meant to reduce your cruding work.

        Requires as arguments
            1. PostgresRunner
            2. tablename
            3. table columns in the format of
                {
                    name: column_name,
                    type: a_postgres_type,
                    morestuff: [strings]
                }
        """
        self.postgresRunner = postgresRunner
        self.tablename = tablename
        self.table_config = table_columns
        self.table_keys = [column.get("name") for column in table_columns]
        self.__run(
            _PostgresCrud__create_table_command(tablename, table_columns)
        )

    def __run(self, command):
        return self.postgresRunner.runCommands(
            [command]
        )[0]

    def where(self, key, value):
        """Get retrieve lists of items where a key is equal to a value."""
        comparison = key + " = " + sanitize_value(value)
        results = self.__run(
            pagination_template.substitute(
                tablename=self.tablename,
                comparison=comparison,
                sortKey=key,
                asc="ASC",
                limit=1
            ),
        )
        return results

    def pagination(self, lastValue=None, sortKey="_id", limit=10, asc="ASC"):
        """Method to retrieve lists of values as necessary."""
        comparison = ""
        if lastValue is not None:
            comparison = sortKey + " > " + sanitize_value(lastValue)
        limit = int(limit)
        if asc != "ASC" and asc != "DESC":
            asc = "ASC"
        results = self.__run(
            pagination_template.substitute(
                tablename=self.tablename,
                comparison=comparison,
                sortKey=sortKey,
                asc=asc,
                limit=limit
            ),
        )
        return results

    def create(self, values):
        """Create an item."""
        dic = _PostgresCrud__parseColumnsAndValues(values)
        results = self.__run(
            create_template.substitute(
                tablename=self.tablename,
                columns=dic["columns"],
                values=dic["values"]
            ),
        )
        return results[0][0]

    def request(self, targetID):
        """Request an item."""
        results = self.__run(
            request_template.substitute(
                tablename=self.tablename,
                targetID=targetID,
            ),
        )
        print str(results)
        return results[0]

    def update(self, targetID, values):
        """Update an item."""
        dic = _PostgresCrud__parseColumnsAndValues(values)
        results = self.__run(
            update_template.substitute(
                tablename=self.tablename,
                targetID=targetID,
                columns=dic.columns,
                values=dic.values
            ),
        )
        return results[0]

    def delete(self, targetID):
        """Delete an item."""
        results = self.__run(
            delete_template.substitute(
                tablename=self.tablename,
                targetID=targetID,
            ),
        )
        return results[0]


def _PostgresCrud__parseColumnsAndValues(dic):
    keys = dic.keys()
    values = [sanitize_value(dic[key]) for key in keys]
    return {
        "columns": ", ".join(keys),
        "values": ", ".join(values)
    }


table_template = Template(
  """
    CREATE TABLE IF NOT EXISTS $tablename (
      _id SERIAL PRIMARY KEY,
      $table_columns
    )
  """
)

column_template = Template("""$name $type $extras""")


def _PostgresCrud__create_table_command(tablename, table_columns):
    table_columns = [
        column_template.substitute(
            name=column.get("name"),
            type=column.get("type", "VARCHAR(255)"),
            extras=" ".join(column.get("extras", []))
        ) for column in table_columns
    ]
    return table_template.substitute(
        tablename=tablename,
        table_columns=",\n".join(table_columns)
    )
