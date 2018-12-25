import pyodbc
from additions.classes import *
from additions.ms_sql_requests import *

class MSSQL_RAM():
    driver = 'DRIVER={SQL Server}'
    server = 'SERVER=FLOSTON\SQLEXPRESS'
    port = 'PORT=1433'
    db = 'DATABASE=Northwind'
    user = 'UID=sa'
    pw = 'PWD=1'
    conn_str = ";".join([driver, server, port, db, user, pw])
    object_tables = []

    def __init__(self):
        self.conn = pyodbc.connect(MSSQL_RAM.conn_str)
        self.cursor = self.conn.cursor()

    def ram_create(self):
        self._ram_schema()
        self._ram_domains()
        self._ram_tables()
        self._ram_fields()
        self._ram_indexes()
        self._ram_constrains()
        self._index()
        self.conn.close()

    # Создание схемы
    def _ram_schema(self):
        self.schema = Schema()
        self.cursor.execute(SELECT_SYS_SCHEMA)
        schema = self.cursor.fetchone()
        self.schema_id = schema[1]
        self.schema.name = schema[0]

    # Создание именованных доменов
    def _ram_domains(self):
        temp_domain = self.cursor.execute(SELECT_SYS_DOMAIN).fetchall()

        for temp in temp_domain:
            domain = Domain()
            domain.unnamed = not temp[6]
            if domain.unnamed:
                continue
            domain.name = empty(temp[0])
            domain.align = "L"
            domain.char_length = empty(temp[3])
            domain.precision = none(temp[4])
            domain.scale = none(temp[5])
            type = self.cursor.execute(SELECT_SYS_TYPE_DIFF.format(temp[1], temp[2]))
            domain.type = type.fetchone()[0]

            self.schema.domains.append(domain)

    # Создание таблиц
    def _ram_tables(self):
        SEL_TABLE = SELECT_SYS_TABLE.format(self.schema_id)
        for temp_table in self.cursor.execute(SEL_TABLE):
            MSSQL_RAM.object_tables += [temp_table[1]]
            table = Table()
            table.schema_id = self.schema_id
            table.name = empty(temp_table[0])
            table.temporal_mode = true(temp_table[2])
            if table.name != "sysdiagrams":
                self.schema.tables.append(table)

    # Создание полей
    def _ram_fields(self):
        for id in MSSQL_RAM.object_tables:

            SEL_TABLE = SELECT_SYS_TABLE_NAME.format(id)  # Извлекаем имя таблицы
            SEL_COLUMN = SELECT_SYS_COLUMN.format(id)   # Извлекаем столбцы
            table_name = self.cursor.execute(SEL_TABLE).fetchone()
            temp = self.cursor.execute(SEL_COLUMN).fetchall()

            for temp_field in temp:
                field = Field()
                field.name = temp_field[0]
                type = temp_field[1]
                SEL_TYPE = SELECT_SYS_TYPE_EQ.format(type, temp_field[2])
                temp_domain = self.cursor.execute(SEL_TYPE).fetchone()
                domain = Domain()
                domain.name = empty(temp_domain[0])

                # Создаём новый домен, если он неименованный
                if temp_domain[6] == 0:
                    domain.align = "L"
                    domain.char_length = empty(temp_field[3])
                    domain.precision = none(temp_field[4])
                    domain.scale = none(temp_field[5])

                    SEL_TYPE = SELECT_SYS_TYPE_EQ\
                        .format(temp_domain[1], temp_domain[2])

                    type = self.cursor.execute(SEL_TYPE)
                    domain.type = type.fetchone()[0]
                    domain.unnamed = True
                    self.schema.domains.append(domain)
                    field.domain = domain
                else:  # В противном случае ищем из именованных
                    for i in range(0, len(self.schema.domains)):
                        if domain.name == self.schema.domains[i].name:
                            field.domain = self.schema.domains[i]

                # Добавляем поле в ram память
                for i in range(0, len(self.schema.tables)):
                    if self.schema.tables[i].name == table_name[0]:
                        self.schema.tables[i].fields.append(field)
        self._distinct_domain()

    # Удаление повторяющихся доменов
    def _distinct_domain(self):
        d = self.schema.domains
        t = self.schema.domains
        for domain in self.schema.domains:
            k = 0
            for dom in d:
                if k == 0:
                    k += 1
                    continue
                if dom == domain:
                    t.remove(dom)
        self.schema.domains = t

        t = self.schema.domains
        for domain in self.schema.domains:
            k = 0
            for dom in d:
                if k == 0:
                    k += 1
                    continue
                if dom == domain:
                    t.remove(dom)
        self.schema.domains = t

    # Создание индексов
    def _ram_indexes(self):
        idx = 0
        for id in MSSQL_RAM.object_tables:
            SEL_INDEX = SELECT_SYS_INDEX.format(id)
            SEL_TABLE = SELECT_SYS_TABLE_NAME.format(id)
            table_name = self.cursor.execute(SEL_TABLE).fetchone()
            temp = self.cursor.execute(SEL_INDEX).fetchall()

            for temp_index in temp:
                SEL_POSITION = SELECT_SYS_POSITION.format(id, temp_index[2])
                position = self.cursor.execute(SEL_POSITION).fetchall()

                for pos in position:
                    idx += 1
                    if temp_index[2] == 0:  # Если индекс не применяется к столбцу
                        continue

                    SEL_FIELD = SELECT_SYS_COLUMN_NAME.format(id, pos[0])
                    field_name = self.cursor.execute(SEL_FIELD).fetchone()
                    index = Index()
                    index.name = "{1}_{0}".format(idx, temp_index[0])
                    index.field = field_name[0]
                    index.uniqueness = true(temp_index[3])

                    # Добавляем индекс в ram память
                    for i in range(0, len(self.schema.tables)):
                        if table_name[0] == self.schema.tables[i].name:
                            for j in range(0, len(self.schema.tables[i].fields)):
                                if field_name[0] == self.schema.tables[i].fields[j].name:
                                    self.schema.tables[i].indexes.append(index)

    # Создание ограничений
    def _ram_constrains(self):
        for id in MSSQL_RAM.object_tables:
            SEL_TABLE = SELECT_SYS_TABLE_NAME.format(id)
            table_name = self.cursor.execute(SEL_TABLE).fetchone()
            SEL_PK = SELECT_SYS_PK.format(id)
            temp = self.cursor.execute(SEL_PK).fetchall()
            #last = len(temp) - 1
            #k = 0

            # Создание ограничений
            for temp_constraint in temp:
                #if k < last:
                   # k += 1
                    #continue
                constraint = Constraint()
                constraint.name = temp_constraint[0]
                SEL_FIELD = SELECT_SYS_COLUMN_NAME.format(id, temp_constraint[2])
                field_name = self.cursor.execute(SEL_FIELD).fetchone()
                constraint.items = field_name[0]
                if temp_constraint[1] == "PK":
                    constraint.kind = "PRIMARY"
                    primary = True
                elif temp_constraint[1] == "UQ":
                    constraint.kind = "UNIQUE"

                # Добавляем ограничение в ram память
                for i in range(0, len(self.schema.tables)):
                    if table_name[0] == self.schema.tables[i].name:
                        for j in range(0, len(self.schema.tables[i].fields)):
                            if field_name[0] == self.schema.tables[i].fields[j].name:
                                self.schema.tables[i].constraints.append(constraint)

        for id in MSSQL_RAM.object_tables:
            SEL_TABLE = SELECT_SYS_TABLE_NAME.format(id)
            table_name = self.cursor.execute(SEL_TABLE).fetchone()
            SEL_FK = SELECT_SYS_FK.format(id)
            temp = self.cursor.execute(SEL_FK).fetchall()

            # Создание ограничений (внешних ключей)
            for temp_constraint in temp:
                constraint = Constraint()
                constraint.name = temp_constraint[0]
                SEL_TABLE = SELECT_SYS_TABLE_NAME.format(temp_constraint[1])
                table_reference = self.cursor.execute(SEL_TABLE).fetchone()
                SEL_FIELD = SELECT_SYS_COLUMN_NAME\
                    .format(temp_constraint[1], temp_constraint[3])

                field_name = self.cursor.execute(SEL_FIELD).fetchone()
                constraint.items = field_name[0]
                constraint.kind = "FOREIGN"
                constraint.reference = table_reference[0]
                SEL_TABLE = SELECT_SYS_TABLE_NAME.format(id)
                table_name = self.cursor.execute(SEL_TABLE).fetchone()
                if temp_constraint[4] == 1:
                    constraint.cascading_delete = True

                # Добавляем ограничение в ram память
                for i in range(0, len(self.schema.tables)):
                    if table_name[0] == self.schema.tables[i].name:
                        for j in range(0, len(self.schema.tables[i].fields)):
                            if field_name[0] == self.schema.tables[i].fields[j].name:
                                self.schema.tables[i].constraints.append(constraint)

    # Если первичный ключ - составной
    def _index(self):
        for table in self.schema.tables:
            pk = ""
            pk_count = 0
            for constraint in table.constraints:
                if constraint.kind == "PRIMARY":
                    pk_count += 1
            if pk_count > 1:
                for index in table.indexes:
                    for constraint in table.constraints:
                        if index.field == constraint.items:
                            if constraint.kind == "PRIMARY":
                                index.uniqueness = False


def none(value):
    return None if not value else value


def empty(value):
    return value if value is not "" else None


def true(value):
    return True if value else False
