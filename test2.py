from modules.xmlMaker import XmlMaker  # Модуль конвертации ram->xdb
from modules.dbd_ram import DbdRam  # Модуль конвертации db->ram
import argparse  # Загружаем стандартную библиотеку обработки параметров консоли


if __name__ == "__main__":

    # Инициализируем argparse объект
    parser = argparse.ArgumentParser(description='Программа преобразования данных.')

    # Добавляем в парсер параметр файла (в сокращенном и полном виде). Default - расположение по умолчанию.
    parser.add_argument('-f', '--file', default='materials/tasks.db',
                        help='Преобразование файла XML представления в RAM представление.')

    args = parser.parse_args()  # Парсим добавленные параметры и запоминаем их в args

    ram = DbdRam(args.file).schema

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

        # Список ограничений каждой таблицы
        print("constraints:")
        for constraint in table.constraints:
            print(constraint.__dict__)

        # Список индексов каждой таблицы
        print("indexes:")
        for index in table.indexes:
            print(index.__dict__)
        print()

    xml2 = XmlMaker(ram).make_xdb()

    # Записываем в новый файл ковертированное ram-представление
    with open("materials/tasks2.xdb", "wb") as f:
        f.write(xml2.toprettyxml(indent="  ", encoding="utf-8"))

    print("Конвертация завершена.\n Новый файл - tasks.xdb\n")
