# Описание классов метаданных


class Schema:  # Основной класс-схема
    schema_attr = [
        'fulltext_engine',
        'version',
        'name',
        'description'
    ]

    schema_list = [
        'domains',  # Список вложенных доменов
        'tables'  # Список вложенных таблиц
    ]

    def __init__(self):  # Конструктор класса
        # Атрибуты класса перечисляются в соответствии с tasks.xdb
        for attr in Schema.schema_attr:
            self.__setattr__(attr, None)

        for lists in Schema.schema_list:
            self.__setattr__(lists, [])

    def domain_exists(self, name):
        for domain in self.domains:
            if domain.name == name:
                return domain
        return None

    def __eq__(self, other):
        true = True

        for val in Schema.schema_attr:
            true = true and eql(self.__getattribute__(val), other.__getattribute__(val))

        for val in Schema.schema_list:
            true = true and self.__getattribute__(val) == other.__getattribute__(val)

        return true


class Domain:  # Класс доменов базы данных
    domain_attr = [
        'name',
        'description',
        'type',
        'align',
        'length',
        'width',
        'precision',
        'char_length',
        'scale'
    ]

    domain_props = [
        'show_null',
        'show_lead_nulls',
        'thousands_separator',
        'summable',
        'case_sensitive'
    ]

    def __init__(self):

        # Перечисление встречающихся в tasks.xdb атрибутов класса доменов
        for attr in Domain.domain_attr:
            self.__setattr__(attr, None)
        self.__setattr__("unnamed", False)
		
        # В составе props
        for props in Domain.domain_props:
            self.__setattr__(props, None)

    def __eq__(self, other):
        true = True

        for val in Domain.domain_attr:
            true = true and eql(self.__getattribute__(val), other.__getattribute__(val))

        for val in Domain.domain_props:
            true = true and eql(self.__getattribute__(val), other.__getattribute__(val))

        return true


class Table:  # Класс таблиц базы данных
    table_attr = [
        'schema_id',
        'name',
        'description',
        'ht_table_flags',
        'access_level',
        'temporal_mode',
        'means'
    ]

    table_props = [
        'add',
        'edit',
        'delete'
    ]

    table_list = [
        'fields',  # Список вложенных полей
        'constraints',  # Список вложенных ограничений
        'indexes'  # Список вложенных индексов
    ]

    def __init__(self):

        # Перечисление встречающихся в tasks.xdb атрибутов класса таблиц
        for attr in Table.table_attr:
            self.__setattr__(attr, None)

        # В составе props
        for props in Table.table_props:
            self.__setattr__(props, None)

        for lists in Table.table_list:
            self.__setattr__(lists, [])

    def __eq__(self, other):
        true = True

        for val in Table.table_attr:
            true = true and eql(self.__getattribute__(val), other.__getattribute__(val))

        for val in Table.table_props:
            true = true and eql(self.__getattribute__(val), other.__getattribute__(val))

        for val in Table.table_list:
            true = true and eql(self.__getattribute__(val), other.__getattribute__(val))

        return true


class Field:
    field_attr = [
        'name',
        'rname',
        'domain',
        'description'
    ]

    field_props = [
        'input',
        'edit',
        'show_in_grid',
        'show_in_details',
        'is_mean',
        'autocalculated',
        'required'
    ]

    def __init__(self):

        # Перечисление встречающихся в tasks.xdb атрибутов класса полей
        for attr in Field.field_attr:
            self.__setattr__(attr, None)

        # В составе props
        for props in Field.field_props:
            self.__setattr__(props, None)

    def __eq__(self, other):
        true = True

        for val in Field.field_attr:
            true = true and eql(self.__getattribute__(val), other.__getattribute__(val))

        for val in Field.field_props:
            true = true and eql(self.__getattribute__(val), other.__getattribute__(val))

        return true


class Constraint:
    constraint_attr = [
        'name',
        'kind',
        'items',
        'reference',
        'expression'
    ]

    constraint_props = [
        'has_value_edit',
        'cascading_delete',
        'full_cascading_delete'
    ]

    def __init__(self):

        # Перечисление встречающихся в tasks.xdb атрибутов класса ограничений
        for attr in Constraint.constraint_attr:
            self.__setattr__(attr, None)

        # В составе props
        for props in Constraint.constraint_props:
            self.__setattr__(props, None)

    def __eq__(self, other):
        true = True

        for val in Constraint.constraint_attr:
            true = true and eql(self.__getattribute__(val), other.__getattribute__(val))

        for val in Constraint.constraint_props:
            true = true and eql(self.__getattribute__(val), other.__getattribute__(val))

        return true


class Index:
    index_attr = [
        'name',
        'field'
    ]

    index_props = [
        'uniqueness',
        'fulltext',
        'local',
        'expression',
        'descend'
    ]

    def __init__(self):
        # Перечисление встречающихся в tasks.xdb атрибутов класса индексов
        for attr in Index.index_attr:
            self.__setattr__(attr, None)

        # В составе props
        for props in Index.index_props:
            self.__setattr__(props, None)

    def __eq__(self, other):
        true = True

        for val in Index.index_attr:
            true = true and eql(self.__getattribute__(val), other.__getattribute__(val))

        for val in Index.index_props:
            true = true and eql(self.__getattribute__(val), other.__getattribute__(val))

        return true


def eql(val1, val2):

    if (val1 is None and val2 is False) or (val1 is False and val2 is None):
        return True

    return val1 == val2
