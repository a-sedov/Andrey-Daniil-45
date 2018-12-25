from modules.ram_xdb import XmlMaker  # Модуль конвертации ram->xdb
from modules.mssql_ram import MSSQL_RAM
from modules.mssql_postgres import MSSQL_PG
from modules.postgres_ddl_generator import RamDdl
import os.path  # Модуль для работы с путями
import argparse  # Загружаем стандартную библиотеку обработки параметров консоли


if __name__ == "__main__":

    # Инициализируем argparse объект
    parser = argparse.ArgumentParser(description='Программа преобразования данных.')

    # Добавляем в парсер параметр файла (в сокращенном и полном виде). Default - расположение по умолчанию.
    parser.add_argument('-f', '--file', default='materials/Northwind.xdb',
                        help='Преобразование RAM представления в XDB файл'
                        'и перенос данных из исходной в целевую БД.'
                        )

    args = parser.parse_args()  # Парсим добавленные параметры и запоминаем их в args

    ram = MSSQL_RAM()
    ram.ram_create()
    ram = ram.schema

    # Выводим RAM представление на экран
    test = ram.__dict__
    # Вывод информации о схеме
    print('Преобразованная в память SQL схема:\n\n<?xml version="1.0" encoding="utf-8"?>')
    print("dbd_schema", end=' ')
    for key in ram.__dict__:
        # Выписываем атрибуты не-списки
        if (key != "domains") and (key != "tables") and (ram.__dict__.get(key) is not None):
            print(key + "=" + "'" + ram.__dict__.get(key) + "'", end=' ')
    print("")

    # Вывод доменов
    print("domains:")
    for domain in ram.domains:
        print(domain.__dict__)

    # Вывод таблиц
    print("tables:")
    for table in ram.tables:
        print("table", end=' ')
        for key in table.__dict__:  # Обход словаря каждой таблицы
            if (key != "fields") and (key != "constraints") and (key != "indexes"):  # Выписываем атрибуты не-списки
                print(key, "='", table.__dict__.get(key), "'", sep='', end=' ')

        # Список полей каждой таблицы
        print("\nfields:")
        for field in table.fields:
            print(field.__dict__)
            print(field.domain.__dict__)

        # Список ограничений каждой таблицы
        print("constraints:")
        for constraint in table.constraints:
            print(constraint.__dict__)

        # Список индексов каждой таблицы
        print("indexes:")
        for index in table.indexes:
            print(index.__dict__)
        print()

    xdb_generate = XmlMaker(ram).make_xdb()
    # Записываем в новый файл ковертированное ram-представление
    with open(args.file, "wb") as f:
        f.write(xdb_generate.toprettyxml(indent="  ", encoding="utf-8"))
    print("Конвертация завершена.\n Новый файл - Northwind.xdb")

    ddl_generate = RamDdl(args.file.replace('.xdb', '.ddl'), ram)
    # Записываем в новый файл ковертированное ram-представление
    print("Конвертация завершена.\n Новый файл - Northwind.ddl")

    # Переносим данные из исходной в целевую БД
    pg_generate = MSSQL_PG(ram)
    print("Перенос данных завершен.")
