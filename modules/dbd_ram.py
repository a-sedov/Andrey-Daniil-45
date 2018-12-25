from additions.classes import *
import sqlite3  # Библиотека для работы с SQL
import os.path  # Модуль для работы с путями
from additions.sql_requests import *  # Модуль с sql-запросами


class DbdRam:
    def __init__(self, file):
        if not os.path.exists(file):
            print("Файл " + file + " не существует!")
            exit(1)

        self.connect = sqlite3.connect(file)
        self.cursor = self.connect.cursor()

        self._ram_schema()
        self._ram_domains()
        self._ram_tables()
        self._ram_fields()
        self._ram_indexes()
        self._ram_constrains()

    # Создание схемы
    def _ram_schema(self):
        self.schema = Schema()
        temp_schema = self.cursor.execute(SELECT_SCHEMA).fetchall()

        self.schema.fulltext_engine = temp_schema[0][3]
        self.schema.version = temp_schema[0][2]
        self.schema.name = temp_schema[0][1]
        self.schema.description = temp_schema[0][4]

    # Создание доменов
    def _ram_domains(self):
        # Выбираем необходимый порядок нужных столбцов
        num = [1, 2, 17, 9, 4, 8, 6, 5, 7, 10, 11, 12, 13, 14]
        uid = 15
        for temp_domain in self.cursor.execute(SELECT_DOMAIN):
            domain = Domain()
            k = 0
            for attr in domain.domain_attr:
                domain.__setattr__(attr, empty(temp_domain[num[k]]))
                k += 1

            if temp_domain[uid][0] == "U":
                domain.__setattr__("unnamed", True)
            else:
                domain.__setattr__("unnamed", False)

            # Свойства домена
            for props in domain.domain_props:  # заполняем свойства
                domain.__setattr__(props, true(temp_domain[num[k]]))
                k += 1

            self.schema.domains.append(domain)

    # Создание таблиц
    def _ram_tables(self):
        # Выбираем необходимый порядок нужных столбцов
        num = [i for i in range(1, 11)]
        for temp_table in self.cursor.execute(SELECT_TABLE):
            table = Table()
            k = 0
            for attr in table.table_attr:
                table.__setattr__(attr, empty(temp_table[num[k]]))
                k += 1

            # Свойства таблицы
            for props in table.table_props:  # заполняем свойства
                table.__setattr__(props, true(temp_table[num[k]]))
                k += 1

            self.schema.tables.append(table)

    # Создание полей
    def _ram_fields(self):
        # Выбираем необходимый порядок нужных столбцов
        num = [i for i in range(3, 14)]
        for temp_field in self.cursor.execute(SELECT_FIELD):
            field = Field()
            k = 0
            for attr in field.field_attr:
                field.__setattr__(attr, empty(temp_field[num[k]]))
                k += 1

            field.domain = self.schema.domains[temp_field[5] - 1]

            # Свойства поля
            for props in field.field_props:  # заполняем свойства
                field.__setattr__(props, true(temp_field[num[k]]))
                k += 1

            self.schema.tables[temp_field[1] - 1].fields.append(field)

    # Создание индексов
    def _ram_indexes(self):
        for temp_index in self.cursor.execute(SELECT_INDEX):
            index = Index()
            index.name = empty(temp_index[2])
            index.field = empty(temp_index[12])
            index.expression = empty(temp_index[10])

            # Свойства индекса
            index.local = true(temp_index[3])
            index.uniqueness = True if temp_index[4] == 'U' else None
            index.fulltext = True if temp_index[4] == 'T' else None
            index.descend = true(temp_index[11])

            self.schema.tables[temp_index[1] - 1].indexes.append(index)

    # Создание ограничений
    def _ram_constrains(self):
        # Выбираем необходимый порядок нужных столбцов
        num = [2, 3, 15, 17, 5]
        for temp_constrain in self.cursor.execute(SELECT_CONSTRAIN):
            constrain = Constraint()
            k = 0
            for attr in constrain.constraint_attr:
                constrain.__setattr__(attr, empty(temp_constrain[num[k]]))
                k += 1

            constrain.kind = "PRIMARY" if temp_constrain[3] == 'P' else 'FOREIGN'

            # Свойства ограничения
            constrain.has_value_edit = true(temp_constrain[7])
            constrain.full_cascading_delete = True if temp_constrain[8] == 'TRUE' else None
            constrain.cascading_delete = True if temp_constrain[8] == 'FALSE' else None

            self.schema.tables[temp_constrain[1] - 1].constraints.append(constrain)


def none(value):
    return None if not value else value


def empty(value):
    return value if value is not "" else None


def true(value):
    return True if value else False
