from weneda.database import Database, Table


class Usta(Table):
    def __init__(self, args: tuple[str]):
        super().__init__(name, columns, args, extra, db)