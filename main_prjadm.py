from modules.xdb_ram import XmlParser  # Модуль конвертации xdb->ram
from modules.ram_dbd import RamDbd  # Модуль конвертации ram->db
from modules.dbd_ram import DbdRam  # Модуль конвертации db->ram
from modules.ram_xdb import XmlMaker  # Модуль конвертации ram->xdb
import argparse  # Загружаем стандартную библиотеку обработки параметров консоли
import os.path  # Загружаем модуль для работы с путями

if __name__ == "__main__":
    #
    # Преобразование XDB -> RAM -> DBD
    #
    parser = argparse.ArgumentParser(description='Программа преобразования данных.')

    parser.add_argument('-f', '--file', default='materials/prjadm.xdb',
                        help='Преобразование XDB -> RAM -> DBD.')

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print("Файла {0} не существует.".format(args.file))
        exit(-1)

    ram = XmlParser(args.file).make_ram()

    dbd_create = RamDbd(args.file.replace('.xdb', '.db'), ram)

    print("Конвертация XDB -> RAM -> DBD успешна.\n Новый файл - prjadm.db")
    #
    # Преобразование DBD -> RAM - > XDB2
    #
    parser2 = argparse.ArgumentParser(description='Программа преобразования данных.')

    parser2.add_argument('-f', '--file', default='materials/prjadm.db',
                        help='Преобразование DBD -> RAM - > XDB2.')

    args = parser2.parse_args()

    ram = DbdRam(args.file).schema

    xml2 = XmlMaker(ram).make_xdb()

    # Записываем в новый файл ковертированное ram-представление
    with open("materials/prjadm2.xdb", "wb") as f:
        f.write(xml2.toprettyxml(indent="  ", encoding="utf-8"))

    print("Конвертация DBD -> RAM - > XDB2 успешна.\n Новый файл - prjadm2.xdb\n")
