from modules.xmlParser import XmlParser  # Модуль конвертации xdb->ram
from modules.ram_dbd import RamDbd  # Модуль конвертации ram->db
import os.path  # Модуль для работы с путями
import argparse  # Загружаем стандартную библиотеку обработки параметров консоли


if __name__ == "__main__":

    # Инициализируем argparse объект
    parser = argparse.ArgumentParser(description='Программа преобразования данных.')

    # Добавляем в парсер параметр файла (в сокращенном и полном виде). Default - расположение по умолчанию.
    parser.add_argument('-f', '--file', default='materials/tasks.xdb',
                        help='Преобразование файла XML представления в RAM представление.')

    args = parser.parse_args()  # Парсим добавленные параметры и запоминаем их в args

    if not os.path.exists(args.file):
        print("Файла {0} не существует.".format(args.file))
        exit(-1)

    ram = XmlParser(args.file).make_ram()

    # Выводим RAM представление на экран
    test = ram.__dict__
    # Вывод информации о схеме
	print('Преобразованная в память XML схема:\n\n<?xml version="1.0" encoding="utf-8"?>')
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

    # Записываем в новый файл ковертированное ram-представление
    dbd_create = RamDbd(args.file.replace('.xdb', '.db'), ram)

    print("Конвертация завершена.\n Новый файл - tasks.db")
