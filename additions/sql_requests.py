# -*- coding: utf-8 -*-

from __future__ import unicode_literals

INSERT_SCHEMA = """
--
-- Вставка значений в таблицу схем
--
    INSERT INTO dbd$schemas (       
        fulltext_engine,
        version,
        name,        
        description
    )
    VALUES (?, ?, ?, ?)
    """

INSERT_DOMAIN = """
--
-- Вставка значений в таблицу доменов
--
    INSERT INTO dbd$domains (
        name,
        description,
        data_type_id,
        align,
        length,
        width,
        precision,
        char_length,
        scale,
        show_null,
        show_lead_nulls,
        thousands_separator,
        summable,
        case_sensitive,
        uuid
    )
    VALUES (?, ?, (SELECT id FROM dbd$data_types WHERE type_id = ?), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

CREATE_TEMP_DOMAIN = """
--
-- Создание временной таблицы доменов
--
    CREATE TEMP TABLE temp_domains (
        name varchar unique default(null),  -- имя домена
        description varchar default(null),  -- описание
        data_type_id integer not null,      -- идентификатор типа (dbd$data_types)
        length integer default(null),       -- длина
        char_length integer default(null),  -- длина в символах
        precision integer default(null),    -- точность
        scale integer default(null),        -- количество знаков после запятой
        width integer default(null),        -- ширина визуализации в символах
        align char default(null),           -- признак выравнивания
        show_null boolean default(null),    -- нужно показывать нулевое значение?
        show_lead_nulls boolean default(null),      -- следует ли показывать лидирующие нули?
        thousands_separator boolean default(null),  -- нужен ли разделитель тысяч?
        summable boolean default(null),             -- признак того, что поле является суммируемым
        case_sensitive boolean default(null)        -- признак необходимости регистронезависимого поиска для поля
    );
    """

INSERT_TEMP_DOMAIN = """
--
-- Вставка значений во временную таблицу доменов
--
    INSERT INTO temp_domains (
        name,
        description,
        data_type_id,
        align,
        length,
        width,
        precision,
        char_length,
        scale,
        show_null,
        show_lead_nulls,
        thousands_separator,
        summable,
        case_sensitive)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

SET_NAME_DOMAIN = """
--
-- Удаление имени у неименованных доменов
--
    UPDATE dbd$domains
    SET name = ""
    WHERE INSTR(name, 'temp_unname_')
"""

ORDERBY_TEMP_DOMAIN = """
--
-- Извлечение неименованных доменов без повторений
--
    SELECT DISTINCT
        name,
        description,
        data_type_id,
        align,
        length,
        width,
        precision,
        char_length,
        scale,
        show_null,
        show_lead_nulls,
        thousands_separator,
        summable,
        case_sensitive
    FROM temp_domains;
    """

INSERT_TABLE = """
--
-- Вставка значений в таблицу таблиц
--
    INSERT INTO dbd$tables (
        schema_id,
        name,
        description,
        ht_table_flags,
        access_level,
        temporal_mode,
        means,
        can_add,
        can_edit,
        can_delete,
        uuid
    )
    VALUES ((SELECT id FROM dbd$schemas WHERE id = ?), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

INSERT_FIELD = """
--
-- Вставка значений в таблицу полей
--
    INSERT INTO dbd$fields (
        table_id,
        position,
        name,
        russian_short_name,
        domain_id,
        description,        
        can_input,
        can_edit,
        show_in_grid,
        show_in_details,
        is_mean,
        autocalculated,
        required,
        uuid
     )
    Values((SELECT id FROM dbd$tables WHERE dbd$tables.name = ?), ?, ?, ?, 
            (SELECT id FROM dbd$domains WHERe dbd$domains.name = ?), ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

INSERT_INDEXES = """
--
-- Вставка значений в таблицу индексов
--
    INSERT INTO dbd$indexes(
        table_id,
        name,
        local,
        kind,
        uuid
    )
    Values((SELECT id FROM dbd$tables WHERE dbd$tables.name = ?), ?, ?, ?, ?)
    """

INSERT_INDEXES_DETAILS = """
--
-- Вставка значений в таблицу описаний индексов
--
    INSERT INTO dbd$index_details(
        index_id,
        position,
        field_id,
        expression,
        descend
    )
    Values((SELECT id FROM dbd$indexes WHERE dbd$indexes.name = ?), ?,
            (SELECT id FROM dbd$fields WHERE dbd$fields.name = ?), ?, ?)
    """

DELETE_INDEXES_TEMP_NAME = """
--
-- Удаление временных имён из таблицы индексов
--
    UPDATE dbd$indexes
    SET name=NULL
    WHERE name LIKE 'temp_%';
    """

INSERT_CONSTRAINTS = """
--
-- Вставка значений в таблицу ограничений
--
    INSERT INTO dbd$constraints(
        table_id,
        name,
        constraint_type,
        reference,
        expression,
        unique_key_id,
        has_value_edit,
        cascading_delete,
        uuid
    )
    Values((SELECT id FROM dbd$tables WHERE dbd$tables.name = ?), ?, ?,
            (SELECT id FROM dbd$tables WHERE dbd$tables.name = ?), ?, ?, ?, ?, ?)
    """

INSERT_CONSTRAINT_DETAILS = """
--
-- Вставка значений в таблицу описаний ограничений
--
    INSERT INTO dbd$constraint_details(
        constraint_id,
        position,
        field_id)
    Values((SELECT id FROM dbd$constraints WHERE dbd$constraints.name = ?), ?,
            (SELECT id FROM dbd$fields WHERE dbd$fields.name = ?))
    """

DELETE_CONSTRAINTS_TEMP_NAME = """
--
-- Удаление временных имён из таблицы ограничений
--
        UPDATE dbd$constraints
        SET name=NULL
        WHERE name LIKE 'temp_%';
    """

SELECT_SCHEMA = """
--
-- Получаем всю информацию из таблицы схем
--
    SELECT * FROM dbd$schemas
    ORDER BY id
"""

SELECT_DOMAIN = """
--
-- Получаем всю информацию из таблицы доменов
--
    SELECT * FROM dbd$domains
    LEFT JOIN dbd$data_types
    ON dbd$domains.data_type_id = dbd$data_types.id ORDER BY id
"""

SELECT_TABLE = """
--
-- Получаем всю информацию из таблицы таблиц
--
    SELECT * FROM dbd$tables
    ORDER BY id
"""

SELECT_FIELD = """
--
-- Получаем всю информацию из таблицы полей
--
    SELECT * FROM dbd$fields
    ORDER BY table_id, position
"""

SELECT_INDEX = """
--
-- Получаем всю информацию из таблицы индексов
--
    SELECT *  FROM dbd$indexes
    LEFT JOIN dbd$index_details
        ON dbd$index_details.index_id = dbd$indexes.id
    LEFT JOIN (select dbd$fields.name, dbd$fields.id FROM dbd$fields) field
        ON field.id = dbd$index_details.field_id
    GROUP BY dbd$indexes.table_id, dbd$index_details.position;
"""

SELECT_CONSTRAIN = """
--
-- Получаем всю информацию из таблицы ограничений
--
    SELECT * FROM dbd$constraints
    LEFT JOIN dbd$constraint_details
        ON dbd$constraint_details.constraint_id = dbd$constraints.id
    LEFT JOIN (Select dbd$fields.id, dbd$fields.name FROM dbd$fields) fields
        ON dbd$constraint_details.field_id = fields.id
    LEFT JOIN (Select dbd$tables.id, dbd$tables.name FROM dbd$tables) tab
        ON dbd$constraints.reference = tab.id
    GROUP BY dbd$constraints.table_id, dbd$constraint_details.position
"""
