from xml.dom.minidom import parse  # Загружаем модуль minidom - встроенный инструмент XML парсинга
from additions.classes import *  # Загружаем классы метаданных


class XmlParser:
    def __init__(self, file):  # На вход подаем путь к конвертируемому файлу
        self.parser = parse(file)
        self.schema = Schema()  # Загружаем в парсер атрибуты класса schema

    # Основной метод (парсинга загруженного файла XML)
    def make_ram(self):
        self.get_schema_data()
        return self.schema

    # Метод получения данных для главного класса схемы
    def get_schema_data(self):
        try:  # Пробуем получить атрибуты, списки доменов и таблиц схемы
            self.get_schema_attributes()
            self.get_domains()
            self.get_tables()
        except ValueError:
            print("Ошибка обработки файла.")
            exit(-1)

    # Метод записи в память атрибутов схемы
    def get_schema_attributes(self):
        dbd_schema = self.parser.getElementsByTagName("dbd_schema")[0]

        # Инициализируем список атрибутов
        attribs = dbd_schema.attributes
        # Проходим по списку атрибутов главной схемы XML, записывая их в память
        for i in range(attribs.length):  # Проходим по атрибутам xdb-файла
            attrib = attribs.item(i)
            for attr in Schema.schema_attr:  # Проходим по атрибутам класса Schema
                if attrib.name == attr:  # Если они равны, то записываем в ram-представление
                    setattr(self.schema, attr, attrib.value)

    # Метод записи в память атрибутов доменов
    def get_domains(self):
        for domain_element in self.parser.getElementsByTagName("domain"):
            domain = Domain()  # Загружаем атрибуты класса Domain

            attribs = domain_element.attributes  # Инициализируем список атрибутов
            for i in range(attribs.length):
                attrib = attribs.item(i)
                for attr in Domain.domain_attr:
                    if attrib.name == attr:
                        setattr(domain, attr, attrib.value)
                # Обработка списка props
                for p in attrib.value.split(","):
                    p = p.strip()
                    for pi in Domain.domain_props:  # Проходим по перечню props
                        if p == pi:
                            setattr(domain, pi, True)  # Если найден существующий элемент props, заносим его в список

            self.schema.domains.append(domain)  # Помещаем домен в схему

    # Метод записи в память атрибутов таблиц
    def get_tables(self):
        # Сохраняем атрибуты таблиц в тег table
        for table_element in self.parser.getElementsByTagName("table"):
            table = Table()  # Загружаем атрибуты класса Table

            # Запись атрибутов в таблицу
            attribs = table_element.attributes
            for i in range(attribs.length):
                attrib = attribs.item(i)
                for attr in Table.table_attr:
                    if attrib.name == attr:
                        setattr(table, attr, attrib.value)
                for p in attrib.value.split(","):
                    p = p.strip()
                    for pi in Table.table_props:
                        if p == pi:
                            setattr(table, pi, True)

            # Заполнение полей, ограничений и индексов таблицы
            for field_element in table_element.getElementsByTagName("field"):
                table.fields.append(self.get_field(field_element, table.name))

            for constraint_element in table_element.getElementsByTagName("constraint"):
                table.constraints.append(self.get_constraint(constraint_element, table.name))

            for index_element in table_element.getElementsByTagName("index"):
                table.indexes.append(self.get_index(index_element, table.name))

            self.schema.tables.append(table)  # Помещаем таблицу в схему

    # Метод записи в память атрибутов полей
    def get_field(self, field_element, table_name):
        field = Field()  # Загружаем атрибуты класса Field
        domain = Domain()  # Загружаем атрибуты класса Domain в составе Field

        attribs = field_element.attributes
        for i in range(attribs.length):
            attrib = attribs.item(i)
            for attr in Domain.domain_attr:
                if attrib.name == 'domain.'+attr:
                    setattr(domain, attr, attrib.value)
                    if attrib.name == 'domain.type':
                        setattr(domain, "name", "")
                        setattr(domain, "unnamed", True)
            # Обработка списка props полей
            for p in attrib.value.split(","):
                p = p.strip()
                for pi in Domain.domain_props:  # Проходим по перечню props
                    if p == pi:
                        setattr(domain, pi,True)
            for attr in Field.field_attr:
                if attrib.name == attr:
                    if attr != "domain":
                        setattr(field, attr, attrib.value)
                    else:
                        taken_domain = self.schema.domain_exists(attrib.value)
                        if taken_domain is not None:
                            domain = taken_domain
                        else:
                            raise ValueError("Ошибка: домен не найден.")
            # Обработка списка props доменов
            for p in attrib.value.split(","):
                p = p.strip()
                for pi in Field.field_props:
                    if p == pi:
                        setattr(field, pi, True)

        field.domain = domain   # Помещаем домен в поле

        return field

    # Метод записи в память атрибутов ограничений
    @staticmethod  # Объявляем метод статическим
    def get_constraint(constraint_element, table_name):
        constraint = Constraint()  # Загружаем атрибуты класса Constraint

        attribs = constraint_element.attributes
        for i in range(attribs.length):
            attrib = attribs.item(i)
            for attr in Constraint.constraint_attr:
                if attrib.name == attr:
                    setattr(constraint, attr, attrib.value)
            for p in attrib.value.split(","):
                p = p.strip()
                for pi in Constraint.constraint_props:
                    if p == pi:
                        setattr(constraint, pi, True)

        return constraint

    # Метод записи в память атрибутов индексов
    @staticmethod   # Объявляем метод статическим
    def get_index(index_element, table_name):
        index = Index()  # Загружаем атрибуты класса Index

        attribs = index_element.attributes
        for i in range(attribs.length):
            attrib = attribs.item(i)
            for attr in Index.index_attr:
                if attrib.name == attr:
                    setattr(index, attr, attrib.value)
            for p in attrib.value.split(","):
                p = p.strip()
                for pi in Index.index_props:
                    if p == pi:
                        setattr(index, pi, True)

        return index
