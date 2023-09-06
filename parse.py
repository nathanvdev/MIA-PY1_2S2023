import main, argparse


#main function 
def cmd_parser(text):
    #description
    parser = argparse.ArgumentParser(description='Comandos mkdisk y mkfile')

    # each subparser must be a proyect command
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')

    # cmd exit
    exit_parser = subparsers.add_parser('exit', help='salir del programa')


    # cmd MKDISK
    mkdisk_parser = subparsers.add_parser('mkdisk', help='Crear disco')
    mkdisk_parser.add_argument('-path',type=str, required=True, help='Ruta para el disco')
    mkdisk_parser.add_argument('-size', type=int, required=True, help='Tamaño del disco en MB')
    ## arguments -> (name, type, category, options, default option)
    mkdisk_parser.add_argument('-fit', type=str.lower, required=False, choices=['b','f','w'], default='f')
    mkdisk_parser.add_argument('-unit', type=str.lower, required=False, choices=['k','m'], default='m')
    
    # cmd RMDISK
    mkdisk_parser = subparsers.add_parser('rmdisk', help='remover disco')
    mkdisk_parser.add_argument('-path', type=str, required=True, help='Ruta para el disco')

    # cmd FDISK
    fdisk_parser = subparsers.add_parser('fdisk', help='administrar particiones')
    fdisk_parser.add_argument('-size', type=int, required=False, help='tamaño de la particion', default=99999)
    fdisk_parser.add_argument('-path', type=str, required=True, help='ruta donde se ecuentra el disco')
    fdisk_parser.add_argument('-name', type=str, required=True, help='indicara el nombre de la particion')
    ## optional
    fdisk_parser.add_argument('-unit', type=str.lower, required=False, help='indica las unidades del size', choices=['b','k','m'], default='k')
    fdisk_parser.add_argument('-type', type=str.lower, required=False, help='tipo de particion', choices=['p','e','l'], default='p')
    fdisk_parser.add_argument('-fit', type=str.lower, required=False, help='indica el ajuste que utilizara la particion', choices=['b','f','w'], default='w')
    fdisk_parser.add_argument('-delete', type=str.lower, required=False, help='eliminar una particion', choices=['full'], default='none')
    fdisk_parser.add_argument('-add', type=int, required=False, help='agregar o quitar espacion de la particion', default='99999')

    # cmd Mount
    mount_parser = subparsers.add_parser('mount', help='montar una particion')
    mount_parser.add_argument('-path', type=str, required=True, help='ruta de la particion')
    mount_parser.add_argument('-name', type=str, required=True, help='nombre de la particion')


    
    # cmd MKFILE
    mkfile_parser = subparsers.add_parser('mkfile', help='Crear archivo')
    mkfile_parser.add_argument('-name', type=str, required=True, help='Nombre del archivo')
    mkfile_parser.add_argument('-age', type=int, required=True, help='Edad del archivo')

    args = parser.parse_args()
    # entrada = 'mkdisk -path=/home/user/Disco2.dsk -size=1000'

    #read the input, must be changed to file content
    try:
        args = parser.parse_args(text.split())
    except SystemExit:
        print("Entrada no válida")
        return

    #calls to cmd functions, must be classes ------------------------------------------

    if int(args.size) <= 0:
        print("Size debe ser mayor que 0")

    elif args.command == 'mkdisk':
        main.mkdisk_cmd(args.size, args.path, args.fit, args.unit)

    elif args.command == 'rmdisk':
        main.rmdisk_cmd(args.path)

    elif args.command == 'fdisk':

        if args.add != 99999 and args.delete != 'none':
            print('Comandos incompatibles')
        
        elif args.add != 99999:
            main.fdisk_add(args.path, args.name, args.unit, args.add)

        elif args.delete != 'none':
            main.fdisk_del(args.path, args.name)
        
        elif args.type == 'l':
            main.fdisk_logic(args.path, args.fit, args.size, args.name)
        
        else:
            main.fdisk_cmd(args.path, args.name, args.unit, args.size, args.type, args.fit)
        
    

    else:
        print("Comando no reconocido")

if __name__ == '__main__':

    while True:

        text = ''
        print("------------------------------INGRESE UN COMANDO------------------------------")
        print("--------------------------------exit para salir-------------------------------")
        
        text = input()

        if text.lower() == "exit":
            break



        cmd_parser(text)