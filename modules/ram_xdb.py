from additions.order_plugin import *  # minidom и отредактированные средства для записи в нужном порядке
from additions.classes import *  # Загружаем классы метаданных

class XmlMaker:
    def __init__(self, ram):
        self.ram = ram  # Подаем ram-представление
        # Создаем xml-документ
        self.root = minidom.Document()

    def make_xdb(self):
        # Переопределение методов класса minidom.Element.
        minidom.Element.writexml = new_writexml
        minidom.Element._ensure_attributes = new_ensure_attributes
        # Создаем главный узел схемы
        schema_node = self.root.createElement("dbd_schema")
        # Заполняем атрибуты схемы
        for attr in Schema.schema_attr:
            if getattr(self.ram, attr) is not None:
                schema_node.setAttribute(attr, str(getattr(self.ram, attr)))

        self.root.appendChild(schema_node)  # Добавляем главный узел в документ
        schema_node.appendChild(self.root.createElement("custom"))  # Тег custom в xml таблице
        # Добавляем в главный узел списки доменов и таблиц
        schema_node.appendChild(self.fill_in_domains())
        schema_node.appendChild(self.fill_in_tables())

        return self.root

    def fill_in_domains(self):
        main_domain_node = self.root.createElement("domains")  # Создаем узел-контейнер доменов
        # Проходим по данным доменов в памяти и заполняем узлы
        for domain in self.ram.domains:
            if not domain.unnamed:
                domain_node = self.root.createElement("domain")

                for attr in Domain.domain_attr:
                    if getattr(domain, attr) is not None:
                        domain_node.setAttribute(attr, str(getattr(domain, attr)))
                    if attr == "precision":
                        props = list()  # Создаем список props домена
                        for prop in Domain.domain_props:  # Смотрим какие props имеют значение True
                            if getattr(domain, prop):
                                props.append(prop)
                        if props:  # Заполняем список
                            domain_node.setAttribute("props", ", ".join(props))

                main_domain_node.appendChild(domain_node)  # Добавляем готовый узел в список доменов
        return main_domain_node  # Возвращаем узел контейнер

    def fill_in_tables(self):
        main_table_node = self.root.createElement("tables")
        for table in self.ram.tables:
            table_node = self.root.createElement("table")

            for attr in Table.table_attr:
                if getattr(table, attr) is not None:
                    table_node.setAttribute(attr, str(getattr(table, attr)))
                if attr == "description":
                    props = list()  # Создаем список props таблицы
                    for prop in Table.table_props:  # Смотрим какие props имеют значение True
                        if getattr(table, prop):
                            props.append(prop)
                    if props:  # Заполняем список
                        table_node.setAttribute("props", ", ".join(props))

            # Создаем и заполняем узлы контейнеры fields, constraints, indexes данными из памяти
            fields = self.fill_in_fields(table)
            constraints = self.fill_in_constraints(table)
            indexes = self.fill_in_indexes(table)

            # Каждый из узлов в контейнере добавляем к текущей таблице
            for field in fields:
                table_node.appendChild(field)
            for constraint in constraints:
                table_node.appendChild(constraint)
            for index in indexes:
                table_node.appendChild(index)

            main_table_node.appendChild(table_node)
        return main_table_node

    def fill_in_fields(self, table):
        fields = []
        for field in table.fields:
            # Создаём дочерний узел
            field_node = self.root.createElement("field")
            if not field.domain.unnamed:
                for attr in Field.field_attr:
                    if attr == "domain":
                        field_node.setAttribute(attr, str(field.domain.name))
                    elif getattr(field, attr) is not None:
                        field_node.setAttribute(attr, str(getattr(field, attr)))
                    if attr == "description":
                        props = list()  # Создаем список props поля
                        for prop in Field.field_props:  # Смотрим какие props имеют значение True
                            if getattr(field, prop):
                                props.append(prop)
                        if props:  # Заполняем список
                            field_node.setAttribute("props", ", ".join(props))
            else:

                for attr in Field.field_attr:
                    if (getattr(field, attr) is not None) and (attr != "domain"):
                        field_node.setAttribute(attr, str(getattr(field, attr)))
                    if (attr == "domain"):
                        for dom_attr in Domain.domain_attr:
                            if getattr(field.domain, dom_attr) is not None:
                                field_node.setAttribute("domain." + dom_attr, str(getattr(field.domain, dom_attr)))
                            if dom_attr == "precision":
                                props = list()  # Создаем список props поля
                                for prop in Domain.domain_props:  # Смотрим какие props имеют значение True
                                    if getattr(field.domain, prop):
                                        props.append(prop)
                                if props:  # Заполняем список
                                    field_node.setAttribute("domain.props", ", ".join(props))
                    if attr == "description":
                        props = list()  # Создаем список props поля
                        for prop in Field.field_props:  # Смотрим какие props имеют значение True
                            if getattr(field, prop):
                                props.append(prop)
                        if props:  # Заполняем список
                            field_node.setAttribute("props", ", ".join(props))

            fields.append(field_node)
        return fields

    def fill_in_indexes(self, table):
        indexes = []

        for index in table.indexes:
            index_node = self.root.createElement("index")

            for attr in Index.index_attr:
                if getattr(index, attr) is not None:
                    index_node.setAttribute(attr, str(getattr(index, attr)))
                if attr == "field":
                    props = list()  # Создаем список props индекса
                    for prop in Index.index_props:  # Смотрим какие props имеют значение True
                        if getattr(index, prop):
                            props.append(prop)
                    if props:  # Заполняем список
                        index_node.setAttribute("props", ", ".join(props))

            indexes.append(index_node)
        return indexes

    def fill_in_constraints(self, table):
        constraints = []

        for constraint in table.constraints:
            constraint_node = self.root.createElement("constraint")

            for attr in Constraint.constraint_attr:
                if getattr(constraint, attr) is not None:
                    constraint_node.setAttribute(attr, str(getattr(constraint, attr)))
                if attr == "expression":
                    props = list()  # Создаем список props ограничения
                    for prop in Constraint.constraint_props:  # Смотрим какие props имеют значение True
                        if getattr(constraint, prop):
                            props.append(prop)
                    if props:  # Заполняем список
                        constraint_node.setAttribute("props", ", ".join(props))

            constraints.append(constraint_node)
        return constraints
