import sqlite3
import json


class Database:
    """
    Class representing a Database.

    Attributes
    ----------
    path: `str`
        Path to database file.
    """
    def __init__(self, path: str):
        self.path = path
        self.tables: dict[str, "Table"] = {}

    def _connect(self):
        return sqlite3.connect(self.path)

    def _fetch(self, cursor: sqlite3.Cursor, mode: str):
        if mode == "one":
            return cursor.fetchone()
        if mode == "many":
            return cursor.fetchmany()
        if mode == "all":
            return cursor.fetchall()

        return None
    
    def execute(self, query: str, values: tuple = (), *, fetch: str | None = None):
        db = self._connect()
        cursor = db.cursor()

        cursor.execute(query, values)
        data = self._fetch(cursor, fetch)
        db.commit()

        cursor.close()
        db.close()

        return data
    
    def table(self, name: str, columns: tuple[str], extra: str):
        """
        Create new Table object.

        Attributes
        ----------
        name: `str`
            Name of the table.

        columns: `list[str]`
            List of columns in the table.

        extra: `str`
            Extra conditions which will be executed in the end of query.
        """
        return Table(name, columns, extra, self)
    

class Table:
    """
    Class representing database table.
    """
    __slots__ = (
        'db',
        'name',
        'columns',
        'where'
    )

    def __init__(self, 
                 db: Database,
                 name: str, 
                 columns: tuple[str], 
                 where: dict):
        self.db: Database = db
        self.name: str = name
        self.columns: tuple = columns
        self.where: dict = where
        self.extra: str = f"WHERE {' AND '.join((f'`{k}` = {v}' for k, v in where.items()))}"

        db.tables[name] = self

        self.create()
    
    def create(self) -> None:
        self.db.execute(f"CREATE TABLE IF NOT EXISTS `{self.name}`({', '.join(self.columns)})")

        for num, col in enumerate(self.columns):
            try:
                t = "BIGINT" if num > 0 else "INTEGER PRIMARY KEY"
                self.db.execute(f"ALTER TABLE `{self.name}` ADD COLUMN `{col}` {t}")
            except sqlite3.OperationalError: pass

    def insert(self, **kwargs) -> bool:
        """
        Inserts new row if not exists.

        Attributes
        ----------
        kwargs
            Key for column name and value for data.
        """        
        if self.exists(): 
            return False
        
        columns = list(self.where.keys()) + list(kwargs.keys())
        values = list(self.where.values()) + list(kwargs.values())
        placeholders = ', '.join(['?'] * len(columns))

        self.db.execute(
            f"INSERT INTO `{self.name}`({', '.join(columns)}) VALUES({placeholders})", 
            tuple(values)
        )

        return True

    def exists(self):
        """
        Check if row exists.

        Attributes
        ----------
        args: `list`
            Arguments for the extra query.

        extra: `str`:
            Extra query. Use {n} to get element from args.
        """
        data = self.db.execute(f"SELECT * FROM `{self.name}` {self.extra}", fetch="one")
        
        return bool(data)

    def get(self, key: str, default = None):
        """
        Get value from the table.

        Attributes
        ----------
        key: `str`
            Column name to get data from.
        
        default
            Value to return if None.
        """
        data = self.db.execute(f"SELECT {key} FROM `{self.name}` {self.extra}", fetch="one")

        if not data: return default

        return data[0] or default
    
    def getmany(self, keys: tuple[str]):
        """
        Get all specified values from the table (first matched).

        Attributes
        ----------
        keys: `list[str]`
            List of column names to get data from.
        """
        return self.db.execute(
            f"SELECT {', '.join([f'`{i}`' for i in keys])} FROM `{self.name}` {self.extra}", 
            fetch="one"
        )
    
    def getjson(self, key: str, default = None):
        """
        Same as get() but wrapped in json.loads()

        Attributes
        ----------
        key: `str`
            Column name to get data from.

        default
            Value to return if None.
        """
        try:
            return json.loads(self.get(key, default=default))
        except: 
            return default
        
    def getnested(self, path: str, default = None):
        """
        Get value from the dict or list.

        Attributes
        ----------
        path: `str`
            Dot-separated path to value, where first arg is column name.
        
        default
            Value to return if None.
        """
        splitted = path.split('.')

        result = self.getjson(splitted[0])

        if not result or not isinstance(result, (dict, list)):
            result = {}

        current = result
        for a in splitted[1:-1]:
            if a not in current:
                current[a] = {}
            current = current[a]

        try:
            return current[splitted[-1]]
        except: 
            return default

    def set(self, key: str, value):
        """
        Set value in the table.

        Attributes
        ----------
        key: `str`
            Column name to set data to.

        value: Any
            Value to set into field.
        """
        self.insert()

        self.db.execute(f"UPDATE `{self.name}` SET `{key}` = ? {self.extra}", (value,))
    
    def setmany(self, **kwargs):
        """
        Set all specified values in the table.

        Attributes
        ----------
        kwargs:
            Key - column name, value - value to set. 
        """
        self.insert()

        self.db.execute(
            f"UPDATE `{self.name}` SET {', '.join((f'`{key}` = ?' for key in kwargs))} {self.extra}", 
            kwargs.values()
        )

    def setjson(self, key: str, value):
        """
        Same as set() but wrapped in json.dumps()

        Attributes
        ----------
        key: `str`
            Column name to set data to.

        value: Any
            Value to set into field.
        """
        self.set(key, json.dumps(value))

    def setnested(self, path: str, value):
        """
        Set value in the dict or list.

        Attributes
        ----------
        path: `str`
            Dot-separated path to value, where the first arg is the column name.

        value: Any
            Value to set into the field.
        """
        self.insert()

        splitted = path.split('.')

        if isinstance(value, str):
            value = json.loads(value)
        
        if len(splitted) == 1:
            self.setjson(splitted[0], value)
            return

        result = self.getjson(splitted[0])

        if result is None or not isinstance(result, dict):
            result = {}

        current = result
        for a in splitted[1:-1]:
            if a not in current:
                current[a] = {}
            current = current[a]

        current[splitted[-1]] = value

        self.setjson(splitted[0], result)

        return

    def update(self, key: str, value: int):
        """
        Update int value in the table.

        Attributes
        ----------
        key: `str`
            Column name to update data in.

        value: `int`
            Value to update field. Can be < 0.
        """
        self.insert()

        v = self.get(key)

        try: 
            v = int(v)
        except: 
            return 

        new = max(v + value, 0)
        
        self.db.execute(f"UPDATE `{self.name}` SET `{key}` = ? {self.extra}", (new,))

    def updatenested(self, path: str, value):
        """
        Update value in the dict or list.

        Attributes
        ----------
        path: `str`
            Dot-separated path to value, where the first arg is the column name.

        value: Any
            Value to update the field.
        """
        self.insert()

        splitted = path.split('.')
        
        if len(splitted) == 1:
            self.setjson(splitted[0], value)
            return True

        result = self.getjson(splitted[0])

        if result is None or not isinstance(result, dict):
            result = {}

        current = result
        for a in splitted[1:-1]:
            if a not in current:
                current[a] = {}
            current = current[a]

        old_v = 0
        try: old_v = current[splitted[-1]]
        except: pass

        current[splitted[-1]] = value + old_v

        self.setjson(splitted[0], result)

        return True

    def remove(self):
        """
        Remove row from the table.

        Attributes
        ----------
        args: `list`
            Arguments for the extra query.

        extra: `str`:
            Extra query. Use {n} to get element from args.
        """
        self.db.execute(f"DELETE FROM `{self.name}` {self.extra}")



class Users(Table):
    def __init__(self, user_id):
        super().__init__(
            Database("test.db"), 
            "users", 
            ("user_id", "data"), 
            {"user_id": user_id}
        )   