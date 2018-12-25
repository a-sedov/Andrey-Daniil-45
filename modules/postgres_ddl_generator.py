# -*- coding: utf-8 -*-

import psycopg2
from psycopg2 import sql
from additions.data_types_converting import *


class RamDdl:
    constraint_number = 0
    index_number = 0
    host = "localhost"
    port = "5432"
    database = "Northwind"
    login = "postgres"
    password = "1"
    defer = "DEFERRABLE INITIALLY DEFERRED"


    def __init__(self, file, schema):
        try:
            self.connect = psycopg2.connect(host=RamDdl.host,
                                               port=RamDdl.port,
                                               database="Northwind",
                                               user=RamDdl.login,
                                               password=RamDdl.password)
            self.cursor = self.connect.cursor()
        except (Exception) as error:
            print("Ошибка подключения к PostgreSQL", error)
            exit(1)

        self.schema = schema
        self.file = file
        self.text = ""
        self.schema_text = ""
        self.domain_text = ""
        self.table_text = ""
        self.index_text = ""
        self.primary_text = ""
        self.foreign_text = ""

        self.cursor.execute("""BEGIN TRANSACTION""")
        self._create_schemas()
        self._create_domains()
        self._create_tables()
        self._create_indexes()
        self._create_constraints()
        self._create_constraints_foreign()
        self.text = self.schema_text \
                    + self.domain_text \
                    + self.table_text \
                    + self.index_text \
                    + self.primary_text \
                    + self.foreign_text

        self._write_to_file()

        self.cursor.execute(self.schema_text)
        self.cursor.execute(self.domain_text)
        self.cursor.execute(self.table_text)
        self.cursor.execute(self.index_text)
        self.cursor.execute(self.primary_text)
        self.cursor.execute(self.foreign_text)
        self.connect.commit()
        self.connect.close()

    # Запись текста в ddl-файл
    def _write_to_file(self):
        with open(self.file, 'w', encoding='utf-8') as f:
            f.write(self.text)

    # Создание схемы
    def _create_schemas(self):
        EXISTS_SCHEMA = """
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name = '{0}'            
        """
        self.cursor.execute(sql.SQL(EXISTS_SCHEMA.format(self.schema.name.lower())))
        create = 'CREATE SCHEMA "{0}" AUTHORIZATION {1};\n'
        self.schema_text += create.format(self.schema.name, RamDdl.login)
        if self.schema.description:
            description = 'COMMENT ON SCHEMA "{0}" is '.format(self.schema.name)
            description += "'{0}';\n\n".format(self.schema.description)
            self.schema_text += description

    # Создание доменов
    def _create_domains(self):
        for domain in self.schema.domains:
            if domain.unnamed:
                continue
            query = ""
            create = 'CREATE DOMAIN "{3}".{0} {1}{2};\n'
            name = '"{0}"'.format(domain.name)
            type = type_dict[domain.type.upper()]
            length = domain.char_length
            precision = domain.precision
            scale = domain.scale
            length = '({0})'.format(str(length)) if length else ""
            precision = '({0}'.format(str(precision)) if precision else ""
            scale = ',{0})'.format(str(scale)) if scale else ")"
            if not precision:
                scale = ""

            if type == "DECIMAL":
                type = create.format(name, type, precision + scale, self.schema.name)
            elif type == 'CHAR' or type == 'VARCHAR':
                type = create.format(name, type, length, self.schema.name)
            else:
                type = create.format(name, type, "", self.schema.name)

            self.domain_text += type
        self.domain_text += "\n"

        for domain in self.schema.domains:
            description = domain.description
            if description:
                description = comment("DOMAIN", domain.name, self.schema.name, description)
            else:
                description = ""
            self.text += description

        self.domain_text += "\n"

    # Создание таблиц
    def _create_tables(self):
        for table in self.schema.tables:
            create = 'CREATE TABLE "{0}"."{1}" (\n\t'.format(self.schema.name, table.name)
            # Добавление полей
            fields = self._create_fields(table.fields)

            fields = fields[0:len(fields)-3]
            self.table_text += create + fields + "\n);\n\n"

            # Добавление описания к полям
            for field in table.fields:
                description = field.description
                name = '{0}"."{1}'.format(table.name, field.name)

                if description:
                    description = comment("COLUMN", name, self.schema.name, description)
                else:
                    description = ""

                self.table_text += description

    def _create_indexes(self):
        # Создание индексов
        for table in self.schema.tables:
            indexes = ""
            for index in table.indexes:
                create = 'CREATE{0}INDEX{1}ON "{2}"."{3}" ({4});\n'
                name = ' '
                uniq = " "
                field = '"{0}"'.format(index.field)
                if index.name:
                    name = ' "{0}" '.format(index.name)
                if index.uniqueness:
                    uniq = " UNIQUE "
                index.uniqueness = ' '
                self.index_text += create.format(uniq,
                                           name,
                                           self.schema.name,
                                           table.name,
                                           field)
        self.index_text += "\n\n"

    # Создание полей
    def _create_fields(self, table):
        fields = ""
        for field in table:
            tabs = ""
            name = '"{0}"\t'.format(field.name)

            # Выравниваем поля
            for i in range(8, 17, 3):
                if len(name) + 2 < i: tabs += "\t"

            # Если неименованный домен
            if field.domain.unnamed:
                # Конвертируем исходный тип в тип PostgreSql
                type = type_dict[field.domain.type.upper()]
                length = field.domain.char_length
                precision = field.domain.precision
                scale = field.domain.scale

                # Извлекаем длину, точность, масштаб
                length = '({0})'.format(str(length)) if length else ""
                precision = '({0}'.format(str(precision)) if precision else ""
                scale = ',{0})'.format(str(scale)) if scale else ")"

                # Если точности нет
                if not precision:
                    scale = ""

                # Смотрим тип переменной
                if type == "DECIMAL":
                    type = '{0}{1}{2},\n\t'.format(type, precision, scale)
                elif type == 'CHAR' or type == 'VARCHAR':
                    type = '{0}{1},\n\t'.format(type, length)
                else:
                    type ='{0},\n\t'.format(type)

            else:
                type = '"{0}",\n\t'.format(field.domain.name)
                type = '"{0}".'.format(self.schema.name) + type

            fields += name + tabs + type
        return fields

    # Создание ограничений
    def _create_constraints(self):
        for table in self.schema.tables:
            pkeys = ""
            pk_count = 0
            for constraint in table.constraints:
                if constraint.kind == "PRIMARY":
                    pk_count += 1
            if pk_count > 1:
                constr = ""
                query = 'ALTER TABLE "{0}"."{1}" ' \
                        'ADD CONSTRAINT "{2}" PRIMARY KEY({3}) {4};\n'

                for constraint in table.constraints:
                    if constraint.kind != "PRIMARY":
                        continue

                    if constraint.name:
                        name = '{0}'.format(constraint.name)
                    else:
                        name = '{0}'.format("Constrain_" + str(RamDdl.constraint_number))
                        RamDdl.constraint_number += 1

                    pkeys += '"{0}",'.format(constraint.items)

                pkeys = pkeys[0:len(pkeys)-1]
                constr = query.format(self.schema.name,
                                       table.name,
                                       name,
                                       pkeys,
                                       RamDdl.defer
                                    )
                self.primary_text += constr
            else:
                for constraint in table.constraints:
                    constr = ""
                    if constraint.kind != "PRIMARY":
                        continue

                    query = 'ALTER TABLE "{0}"."{1}" ' \
                            'ADD CONSTRAINT "{2}" PRIMARY KEY("{3}") {4};\n'

                    if constraint.name:
                        name = '{0}'.format(constraint.name)
                    else:
                        name = '{0}'.format("Constrain_" + str(RamDdl.constraint_number))
                        RamDdl.constraint_number += 1

                    constr += query.format(self.schema.name,
                                           table.name,
                                           name,
                                           constraint.items,
                                           RamDdl.defer
                                           )
                    self.primary_text += constr
        self.primary_text += "\n\n"

    # Создание ограничений (внешних ключей)
    def _create_constraints_foreign(self):
        for table in self.schema.tables:
            for constraint in table.constraints:
                if constraint.kind == "PRIMARY":
                    continue
                query = 'ALTER TABLE "{0}"."{1}" ' \
                        'ADD CONSTRAINT "{2}" FOREIGN KEY("{3}")'
                if constraint.name:
                    name = '{0}'.format(constraint.name)
                else:
                    name = '{0}'.format("Constrain_" + str(RamDdl.constraint_number))
                    RamDdl.constraint_number += 1
                query = query.format(self.schema.name, table.name, name, constraint.items)

                reference = constraint.reference
                ref_key = self._reference_key(reference)
                query += ' REFERENCES "{0}"."{1}"("{2}")'.format(self.schema.name,
                                                            reference,
                                                            ref_key)
                if true(constraint.full_cascading_delete) \
                    or true(constraint.cascading_delete):
                    query += " ON DELETE CASCADE"
                self.foreign_text += query +  RamDdl.defer + ";\n"

    # Поиск первичного ключа для внешнего
    def _reference_key(self, name):
        for table in self.schema.tables:
            if table.name == name:
                for constr in table.constraints:
                    if constr.kind == "PRIMARY":
                        return constr.items
                print("Таблица {0} не имеет первичного ключа!".format(name))
                exit(1)
        print("Таблица {0} не существует.".format(name))
        exit(1)


def comment(type, name, schema_name, value):
    return "COMMENT ON {0} {1}.{2} is '{3}';\n".format(type, '"'+schema_name+'"', '"'+name+'"', value)


def true(value):
    return True if value else False

