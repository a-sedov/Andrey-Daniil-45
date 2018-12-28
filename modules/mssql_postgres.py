import psycopg2
import pyodbc
from psycopg2 import sql


class MSSQL_PG:
    constraint_number = 0
    index_number = 0
    host = "localhost"
    pg_port = "5432"
    database = "Northwind"
    login = "postgres"
    password = "1"

    driver = 'DRIVER={SQL Server}'
    server = 'SERVER=FLOSTON\SQLEXPRESS'
    ms_port = 'PORT=1433'
    db = 'DATABASE=Northwind'
    user = 'UID=sa'
    pw = 'PWD=1'
    conn_str = ";".join([driver, server, ms_port, db, user, pw])
    object_tables = []

    def __init__(self, schema):
        try:
            self.ms_conn = pyodbc.connect(MSSQL_PG.conn_str)
            self.ms_cursor = self.ms_conn.cursor()
        except (Exception) as error:
            print("Ошибка подключения к MSSQL", error)

        try:
            self.pg_conn = psycopg2.connect(
                                            host=MSSQL_PG.host,
                                            port=MSSQL_PG.pg_port,
                                            database=MSSQL_PG.database,
                                            user=MSSQL_PG.login,
                                            password=MSSQL_PG.password
                                           )
            self.pg_cursor = self.pg_conn.cursor()
        except (Exception) as error:
            print("Ошибка подключения к PostgreSQL", error)
            exit(1)

        self.schema = schema

        self.pg_cursor.execute("START TRANSACTION DEFERRABLE")
        self.pg_cursor.execute("""SET CONSTRAINTS ALL DEFERRED""")
        self._create_tables()
        self.pg_cursor.execute("""SET CONSTRAINTS ALL DEFERRED""")
        try:
            self.pg_conn.commit()
        except (Exception) as error:
            print(error)
        self.pg_conn.close()

    def _create_tables(self):
        SELECT_FIELD = 'SELECT * FROM "{0}"'
        INSERT_FIELD = 'INSERT INTO dbo."{0}" VALUES ({1})'

        # Заполнение данными
        for table in self.schema.tables:
            SEL_FIELD = SELECT_FIELD.format(table.name)
            fields = self.ms_cursor.execute(SEL_FIELD).fetchall()

            # Перебор полей
            for field in fields:
                value = ()
                # Перебор значений поля
                for i in field:
                    if i is True:
                        value += str(1),
                        continue
                    elif i is False:
                        value += str(0),
                        continue
                    elif isinstance(i, int) \
                            or isinstance(i, float):
                        value += str(i),
                        continue
                    value += i,

                kolvo = ",".join(['%s'] * len(field))
                INS_FIELD = "{0}".format(INSERT_FIELD.format(table.name, kolvo))

                # Попытка занести данные полей в таблицу
                try:
                    self.pg_cursor.execute("""SET CONSTRAINTS ALL DEFERRED""")
                    self.pg_cursor.execute(INS_FIELD, value)
                except (Exception) as error:
                    self.pg_cursor.execute("ROLLBACK")
                    print(error)
