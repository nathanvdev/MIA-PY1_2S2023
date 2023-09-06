import argparse

parser = argparse.ArgumentParser(description='Manejo de archivos')

subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')

# cmd exit
exit_parser = subparsers.add_parser('exit', help='salir del programa')


# cmd MKDISK
mkdisk_parser = subparsers.add_parser('mkdisk', help='Crear disco')
mkdisk_parser.add_argument('-path',type=str, required=True, help='Ruta para el disco')
mkdisk_parser.add_argument('-size', type=int, required=True, help='Tamaño del disco en MB')
## arguments -> (name, type, category, options, default option)
mkdisk_parser.add_argument('-fit', type=str.lower, required=False, choices=['bf','ff','wf'], default='ff')
mkdisk_parser.add_argument('-unit', type=str.lower, required=False, choices=['k','m'], default='m')

# cmd RMDISK
mkdisk_parser = subparsers.add_parser('rmdisk', help='remover disco')
mkdisk_parser.add_argument('-path', type=str, required=True, help='Ruta para el disco')

# cmd MKFILE
mkfile_parser = subparsers.add_parser('mkfile', help='Crear archivo')
mkfile_parser.add_argument('-name', type=str, required=True, help='Nombre del archivo')
mkfile_parser.add_argument('-age', type=int, required=True, help='Edad del archivo')




args = parser.parse_args()
print(args.accumulate(args.integers))