import sqlite3  # Библиотека для работы с SQL
from additions.dbd_const import *  # Классы
import os.path  # Модуль для работы с путями
from additions.sql_requests import *  # Модуль с sql-запросами


class RamDbd:
    def __init__(self, file, schema):
        self.schema = schema

        if not os.path.exists(file):
            self.connect = sqlite3.connect(file)
        else:
            print("'" + file + "' - файл уже существует!")
            exit(1)

        self.cursor = self.connect.cursor()

        self.cursor.executescript(SQL_DBD_INIT)
        self.cursor.execute("""BEGIN TRANSACTION""")

        self._create_schema()
        self._create_domains()
        self._create_unnamed_domains()
        self._create_tables()
        self._create_fields()
        self._create_indexes()
        self._create_constraints()

        self.connect.commit()
        self.connect.close()

    # Формирование схем таблиц
    def _create_schema(self):
        schema = ()
        self.schema.schema_id = 1
        for attr in self.schema.schema_attr:  # заполняем атрибуты
            schema += empty(self.schema.__getattribute__(attr)),

        # Вставляем значения в dbd$schemas
        self.cursor.execute(INSERT_SCHEMA % self.schema.schema_attr, schema)

    # Формирование доменов
    def _create_domains(self):
        domain_number = 0  # Текущий порядковый номер домена
        # Добавляем в dbd$domains домены
        for domain in self.schema.domains:
            temp_domain = ()

            for attr in domain.domain_attr:  # заполняем атрибуты
                temp_domain += empty(domain.__getattribute__(attr)),

            # Свойства домена
            for props in domain.domain_props:  # заполняем свойства
                temp_domain += true(domain.__getattribute__(props)),

            domain_number += 1
            temp_domain += "D" + str(domain_number),
            # Вставляем значения в dbd$domains
            self.cursor.execute(INSERT_DOMAIN, temp_domain)

    # Создание неименованных доменов
    def _create_unnamed_domains(self):
        self.cursor.execute(CREATE_TEMP_DOMAIN)
        unname = 0
        # Добавляем в temp_domain
        for table in self.schema.tables:
            for field in table.fields:
                if field.domain.unnamed:
                    unname += 1
                    temp_unnamed_domain = ()
                    print(field.domain.type)
                    if field.domain.name == "":
                        field.domain.name = "temp_unname_" + str(unname)

                    for attr in field.domain.domain_attr:
                        temp_unnamed_domain += empty(field.domain.__getattribute__(attr)),

                    # Свойства домена
                    for props in field.domain.domain_props:
                        temp_unnamed_domain +=  true(field.domain.__getattribute__(props)),

                    self.cursor.execute(INSERT_TEMP_DOMAIN, temp_unnamed_domain)

        unnamed_number = 0
        for temp_unnamed_domain in self.cursor.execute(ORDERBY_TEMP_DOMAIN):
            temp_unnamed = ()
            unnamed_number += 1
            uuid = "U" + str(unnamed_number)
            for temp in temp_unnamed_domain:
                temp_unnamed += temp,
            temp_unnamed += uuid,
            self.cursor.execute(INSERT_DOMAIN, temp_unnamed)

    # Формирование таблиц
    def _create_tables(self):
        table_number = 0  # Текущий порядковый номер таблицы
        for table in self.schema.tables:
            temp_table = ()
            for attr in table.table_attr:  # заполняем атрибуты
                temp_table += empty(table.__getattribute__(attr)),

            # Свойства таблицы
            for props in table.table_props:  # заполняем свойства
                temp_table += true(table.__getattribute__(props)),

            table_number += 1
            temp_table += "T" + str(table_number),
            # Вставляем значения в dbd$tables
            self.cursor.execute(INSERT_TABLE, temp_table)

    # Формирование полей
    def _create_fields(self):
        field_number = 0  # Текущий порядковый номер поля
        for table in self.schema.tables:
            for field in table.fields:
                temp_field = ()
                temp_field += empty(table.name),
                temp_field += table.fields.index(field) + 1,
                for attr in field.field_attr:
                    if attr == 'domain':  # заполняем атрибуты
                        domain_name = field.__getattribute__(attr).name
                        temp_field += domain_name,
                        continue
                    temp_field += empty(field.__getattribute__(attr)),

                # Свойства поля
                for props in field.field_props:  # заполняем свойства
                    temp_field += true(field.__getattribute__(props)),

                field_number += 1
                temp_field += "F" + str(field_number),
                # Вставляем значения в dbd$fields
                self.cursor.execute(INSERT_FIELD, temp_field)
        self.cursor.execute(SET_NAME_DOMAIN)
    # Формирование индексов
    def _create_indexes(self):
        index_number = 0  # Текущий порядковый номер индекса
        for table in self.schema.tables:
            position = 0
            for index in table.indexes:
                temp_index, temp_index_detail = (), ()
                # Получаем имя индекса, либо создаём временное,
                # чтобы корректно заполнить таблицу dbd$index_details
                index_number += 1
                name = index.name
                if name is None or name == "":
                    name = "temp_" + str(index_number)

                temp_index += empty(table.name),
                temp_index += name,
                temp_index += true(index.local),

                # Свойства индекса
                if true(index.uniqueness):
                    temp_index += 'U',
                elif true(index.fulltext):
                    temp_index += 'T',
                else:
                    temp_index += None,

                temp_index += "I" + str(index_number),
                # Вставляем значения в dbd$indexes
                self.cursor.execute(INSERT_INDEXES, temp_index)
                position += 1
                temp_index_detail += empty(name),
                temp_index_detail += position,  # Позиция индекса
                temp_index_detail += empty(index.field),
                temp_index_detail += empty(index.expression),
                temp_index_detail += true(index.descend),
                # Вставляем значения в dbd$index_details
                self.cursor.execute(INSERT_INDEXES_DETAILS, temp_index_detail)

        self.cursor.execute(DELETE_INDEXES_TEMP_NAME)

    # Формируем таблицу ограничений
    def _create_constraints(self):
        constraint_number = 0  # Текущий порядковый номер ограничений
        for table in self.schema.tables:
            position = 0
            for constraint in table.constraints:
                temp_constraint, temp_constraint_detail = (), ()
                # Получаем имя ограничения, либо создаём временное,
                # чтобы корректно заполить таблицу dbd$constraint_details
                constraint_number += 1
                name = constraint.name
                if name is None or name == "":
                    name = "temp_" + str(constraint_number)

                temp_constraint += table.name,
                temp_constraint += name,
                temp_constraint += constraint.kind[0],
                temp_constraint += empty(constraint.reference),
                temp_constraint += empty(constraint.expression),
                temp_constraint += "",

                # Свойства ограничения
                temp_constraint += true(constraint.has_value_edit),

                if true(constraint.full_cascading_delete):
                    temp_constraint += 'TRUE',
                elif true(constraint.cascading_delete):
                    temp_constraint += 'FALSE',
                else:
                    temp_constraint += None,

                temp_constraint += "C" + str(constraint_number),
                # Вставляем значения в dbd$constraints
                self.cursor.execute(INSERT_CONSTRAINTS, temp_constraint)

                position += 1
                temp_constraint_detail += empty(name),
                temp_constraint_detail += position,  # Позиция ограничения
                temp_constraint_detail += empty(constraint.items),
                # Вставляем значения в dbd$constrain_details
                self.cursor.execute(INSERT_CONSTRAINT_DETAILS, temp_constraint_detail)

        self.cursor.execute(DELETE_CONSTRAINTS_TEMP_NAME)


# Проверка на отсутствие значения
def empty(value):
    return str_int(value) if value is not "" else None


def true(value):
    return True if value else False


def str_int(value):
    if isinstance(value, str):
        try:
            int(value)
        except ValueError:
            pass
    return value
