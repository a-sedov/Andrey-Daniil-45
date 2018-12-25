# -*- coding: utf-8 -*-

from __future__ import unicode_literals

SELECT_SYS_SCHEMA = """
--
-- Получаем всю информацию из schemas
--
    SELECT * 
    FROM sys.schemas 
    WHERE name = 'dbo'
"""

SELECT_SYS_DOMAIN = """
--
-- Получаем всю информацию из types
--
    SELECT 
        name,
        system_type_id,
        user_type_id,
        max_length,
        precision,
        scale,
        is_user_defined
    FROM sys.types
"""

SELECT_SYS_TYPE_DIFF = """
--
-- Получаем имя родительского типа
--
    SELECT name 
    FROM sys.types 
    WHERE system_type_id = {0}
        and user_type_id != {1}
"""

SELECT_SYS_TYPE_EQ = """
--
-- Получаем имя своего типа
--
    SELECT
        name,
        system_type_id,
        user_type_id,
        max_length,
        precision,
        scale,
        is_user_defined 
    FROM sys.types 
    WHERE system_type_id = {0}
        and user_type_id = {1}
"""

SELECT_SYS_TABLE = """
--
-- Получаем информацию о таблицах
--
    SELECT
        name,
        object_id,
        temporal_type
    FROM sys.tables 
    WHERE schema_id = {0}
"""

SELECT_SYS_TABLE_NAME = """
--
-- Получаем имя таблицы
--
    SELECT name
    FROM sys.tables
    WHERE object_id = {0}
"""

SELECT_SYS_COLUMN = """
--
-- Получаем всю информацию о полях
--
    SELECT
        name,
        system_type_id,
        user_type_id,
        max_length,
        precision,
        scale
    FROM sys.columns
    WHERE object_id = {0}
"""

SELECT_SYS_INDEX = """
--
-- Получаем всю информацию о индексах
--
    SELECT
        name,
        index_id,
        type,
        is_unique
    FROM sys.indexes 
    WHERE object_id = {0}
"""

SELECT_SYS_POSITION = """
--
-- Получаем позицию поля
--
    SELECT column_id
    FROM sys.index_columns
    WHERE object_id = {0}
        and index_id = {1}
"""

SELECT_SYS_COLUMN_NAME = """
--
-- Получаем имя поля
--
    SELECT name
    FROM sys.columns 
    WHERE object_id = {0}
        and column_id = {1}
"""

SELECT_SYS_PK = """
--
-- Получаем всю информацию об ограничениях
--
    SELECT
        name,
        type,
        column_id,
        sys.index_columns.object_id,
        sys.index_columns.index_id
    FROM sys.key_constraints 
    LEFT JOIN sys.index_columns
    ON sys.index_columns.index_id = unique_index_id
        and sys.index_columns.object_id = sys.key_constraints.parent_object_id
    WHERE parent_object_id = {0}
"""

SELECT_SYS_FK = """
--
-- Получаем всю информацию о внешних ключах
--
    SELECT
        name,
        sys.foreign_keys.referenced_object_id,
        parent_column_id,
        referenced_column_id,
        delete_referential_action
    FROM sys.foreign_keys
    LEFT JOIN sys.foreign_key_columns
    ON constraint_object_id = object_id
    WHERE sys.foreign_keys.parent_object_id = {0}
"""
