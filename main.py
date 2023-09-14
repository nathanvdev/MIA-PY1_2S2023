from math import floor
import os, sys
from structs import Journaling, MBr, EBr, Mount, SuperBlock, Inodo, Block, BlockFile
from datetime import datetime


def ReadDisk(Path):
    Path = Path.replace('"','')
    try:
        tmp_MBr = MBr(0, 'f')
        with open(Path, 'rb+') as file:
            bindata = file.read()
            tmp_MBr.set_bytes(bindata)
            return tmp_MBr
        
            
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print("No se pudo leer la información del disco.")
        print("Exception type: ", exception_type)
        print("File name: ", filename)
        print("Line number: ", line_number)
        print('Error: ',e)
        return None

def WriteDisk(Path, tmp_MBr, Name):
    Path = Path.replace('"','')
    try:
        with open(Path, 'rb+') as file:
            file.seek(0)
            file.write(tmp_MBr.getBytes())

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno

        print("Exception type: ", exception_type)
        print("File name: ", filename)
        print("Line number: ", line_number)
        print('Error: ',e)
        print("No se pudo modificar el archivo.")

def mkdisk_cmd(Size,Path,Fit,Unit):

    directorio = os.path.dirname(Path)
    directorio = directorio.replace('"', '')
    if Unit == "m":
        Size *= 1024
    NewMBr = MBr(Size, Fit)

    os.makedirs(directorio, exist_ok=True)
    Path = Path.replace('"', '')


    try:
        with open(Path, "wb+") as file:
            file.write(b'\x00' * 1024 * Size)
            file.seek(0)
            file.write(NewMBr.getBytes())

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print("Fallo creando el disco.")
        print("Exception type: ", exception_type)
        print("File name: ", filename)
        print("Line number: ", line_number)
        print('Error: ',e)
        pass

    try:
        with open(Path, "rb") as file2:
            bindata = file2.read()
            MBruno = MBr(0,'f')
            MBruno.set_bytes(bindata)
            print(f"Tamaño del disco: {MBruno.size}")
            print(f"Fecha del disco: {MBruno.date}")
            print(f"Firma del disco: {MBruno.dsk_signature}")
            print(f"Ajuste del disco: {MBruno.fit}")

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print("No se pudo leer la información del disco.")
        print("Exception type: ", exception_type)
        print("File name: ", filename)
        print("Line number: ", line_number)
        print('Error: ',e)

def rmdisk_cmd(p):
    Path = p.replace('"', '')
    
    if os.path.exists(Path):
        os.remove(Path)
        print(f"El archivo '{Path}' ha sido eliminado.")
    else:
        print(f"El archivo '{Path}' no existe.")

def fdisk_cmd(Path,Name,Unit, Size,Type,Fit):
    Path = Path.replace('"','')
    if Unit == "m":
        Size *= 1024
    Name = Name.replace('"','')

    tmp_MBr = MBr(0,'f')

    tmp_MBr:MBr = ReadDisk(Path)
    if tmp_MBr == False:
        return
    
    if Type == 'e':
        for i in range(len(tmp_MBr.partitions)):
            if tmp_MBr.partitions[i].type == 'e':
                print('ya existe una particion extendida')
                return


    for i in range(len(tmp_MBr.partitions)):
        if tmp_MBr.partitions[i].status == 0:
            tmp_MBr.partitions[i].status = 1
            tmp_MBr.partitions[i].type = Type
            tmp_MBr.partitions[i].fit = Fit
            tmp_MBr.partitions[i].size = int(Size)
            tmp_MBr.partitions[i].setname(Name)

            if tmp_MBr.partitions[i-1].size !=0:
                newStart = tmp_MBr.partitions[i-1].start + tmp_MBr.partitions[i-1].size
                tmp_MBr.partitions[i].start = newStart
            else:
                tmp_MBr.partitions[i].start = 148

            if tmp_MBr.partitions[i].type == 'e':

                newEBr = EBr()
                with open (Path, 'rb+') as filetmp:
                    filetmp.seek(tmp_MBr.partitions[i].start)
                    filetmp.write(newEBr.getBytes())
                
                with open(Path, 'rb+') as tmpfile:
                    bindata = tmpfile.read()
                    tmpEBr = EBr()
                    tmpEBr.setBytes(bindata[tmp_MBr.partitions[i].start: tmp_MBr.partitions[i].start+33])

            WriteDisk(Path, tmp_MBr, Name)

            with open(Path, "rb+") as file2:
                bindata = file2.read()
                MBruno = MBr(0,'f')
                MBruno.set_bytes(bindata)

                for tmp_partiton in MBruno.partitions:
                    if tmp_partiton.name == Name.ljust(16)[:16]:
                        print(f"Status: {tmp_partiton.status}")
                        print(f"Tipo: {tmp_partiton.type}")
                        print(f"FIt: {tmp_partiton.fit}")
                        print(f"Start: {tmp_partiton.start}")
                        print(f"Size: {tmp_partiton.size}")
                        print(f"Name: {tmp_partiton.name}")
                        break
            return  # Para asegurarse de que solo se modifique una partición
        
    # Filtra las particiones con partition.status == 3
    available_partitions = [partition for partition in tmp_MBr.partitions if partition.status == 2]

    if not available_partitions:
        print("Todas las particiones están llenas.")
        return    
        
    # Filtra las particiones con Size mayor que partition.size
    available_partitions = [partition for partition in available_partitions if Size <= partition.size]

    if not available_partitions:
        print("Ya no hay espacio para esta particion")
        return   

    if tmp_MBr.fit == 'f':
        available_partitions[0].status = 1
        available_partitions[0].type = Type
        available_partitions[0].fit = Fit
        available_partitions[0].size = int(Size)
        available_partitions[0].setname(Name)

    elif tmp_MBr.fit == 'b':
        #particion con el tamano mas pequeno
        min_partition = min(available_partitions, key=lambda partition: partition.size)
        min_partition.status = 1
        min_partition.type = Type
        min_partition.fit = Fit
        min_partition.size = int(Size)
        min_partition.setname(Name)

    elif tmp_MBr.fit == 'w':
        # The above code is finding the partition with the maximum size from a list of available
        # partitions.
        max_partition = max(available_partitions, key=lambda partition: partition.size)
        max_partition.status = 1
        max_partition.type = Type
        max_partition.fit = Fit
        max_partition.size = int(Size)
        max_partition.setname(Name)

    WriteDisk(Path, tmp_MBr, Name)

    with open(Path, "rb+") as file2:
        bindata = file2.read()
        MBruno = MBr(0,'f')
        MBruno.set_bytes(bindata)

        for tmp_partiton in MBruno.partitions:
            if tmp_partiton.name == Name.ljust(16)[:16]:
                print(f"Status: {tmp_partiton.status}")
                print(f"Tipo: {tmp_partiton.type}")
                print(f"FIt: {tmp_partiton.fit}")
                print(f"Start: {tmp_partiton.start}")
                print(f"Size: {tmp_partiton.size}")
                print(f"Name: {tmp_partiton.name}")
                break
    return  # Para asegurarse de que solo se modifique una partición

def fdisk_add(Path,Name,Unit, Add):

    if Unit == "m":
        Size *= 1024
    Name = Name.replace('"','')
    Path = Path.replace('"','')
    Positive = True
    if Add < 0:
        Positive = False

    
    tmp_MBr = ReadDisk(Path)
    if tmp_MBr == False:
        return


    for i in range(len(tmp_MBr.partitions)):
        if tmp_MBr.partitions[i].name == Name.ljust(16)[:16]:
            if not Positive:
                tmp_MBr.partitions[i].size += Add
            else:
                if i + 1 >= len(tmp_MBr.partitions)-1:
                    print('no hay sufuciente espacio')
                    return
                if tmp_MBr.partitions[i+1].size != 0:
                    result =  tmp_MBr.partitions[i+1].start - (tmp_MBr.partitions[i].start + tmp_MBr.partitions[i].size)
                    if Add >  result:
                        print('no hay sufuciente espacio')
                    else:
                        tmp_MBr.partitions[i].size += Add
            break 

    WriteDisk(Path, tmp_MBr, Name)
        
    with open(Path, "rb+") as file2:
        bindata = file2.read()
        MBruno = MBr(0,'f')
        MBruno.set_bytes(bindata)

        for tmp_partiton in MBruno.partitions:
            if tmp_partiton.name == Name.ljust(16)[:16]:
                print(f"Status: {tmp_partiton.status}")
                print(f"Tipo: {tmp_partiton.type}")
                print(f"FIt: {tmp_partiton.fit}")
                print(f"Start: {tmp_partiton.start}")
                print(f"Size: {tmp_partiton.size}")
                print(f"Name: {tmp_partiton.name}")
                break

def fdisk_del(Path,Name):
    Name = Name.replace('"','')
    Path = Path.replace('"','')
        
    try:
        tmp_MBr = MBr(0, 'f')
        #Leer el Disco
        with open(Path, 'rb+') as file:
            bindata = file.read()
            tmp_MBr.set_bytes(bindata)

        #Eliminar particion
        for tmp_partiton in tmp_MBr.partitions:

            if tmp_partiton.name == Name.ljust(16)[:16]:
                tmp_partiton.status = 2
                with open(Path, 'rb+') as file:
                    file.seek(0)
                    file.write(tmp_MBr.getBytes())
                    file.seek(tmp_partiton.start+34)
                    for i in range(tmp_partiton.size-34):
                        file.write(b'\x00')

                print('particion eliminada correctamente')
                print(f"Status: {tmp_partiton.status}")
                print(f"Tipo: {tmp_partiton.type}")
                print(f"Fit: {tmp_partiton.fit}")
                print(f"Start: {tmp_partiton.start}")
                print(f"Size: {tmp_partiton.size}")
                print(f"Name: {tmp_partiton.name}")

                break

            if tmp_partiton.type == 'e':

                tmp_EBr:EBr = EBr()
                tmp_EBr.setBytes(bindata[(tmp_partiton.start):(tmp_partiton.start+33)])
                while tmp_EBr.name != Name.ljust(16)[:16]:
                    if tmp_EBr.next == -1:
                        print('no se encontro la particion')
                        return
                    tmp_EBr.setBytes(bindata[(tmp_EBr.next):(tmp_EBr.next+33)])
                
                if tmp_EBr.name == Name.ljust(16)[:16]:
                    tmp_EBr.status = 2
                    with open(Path, 'rb+') as file:
                        file.seek(tmp_EBr.start)
                        file.write(tmp_EBr.getBytes())
                        file.seek(tmp_EBr.start+34)
                        for i in range(tmp_EBr.size-34):
                            file.write(b'\x00')

                    print('particion logica eliminada correctamente')
                    print(f"Status: {tmp_EBr.status}")
                    print(f"Fit: {tmp_EBr.fit}")
                    print(f"Start: {tmp_EBr.start}")
                    print(f"Size: {tmp_EBr.size}")
                    print(f"Name: {tmp_EBr.name}")
                    break
                else:
                    print('no se encontro la particion')

    
    except FileNotFoundError:
        print("El archivo no existe o no se puede abrir.")
        return
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print("No se pudo leer la información del disco.")
        print("Exception type: ", exception_type)
        print("File name: ", filename)
        print("Line number: ", line_number)
        print('Error: ',e)
        return

def fdisk_logic(Path,fit,size,name):
    Path = Path.replace('"','')
    part_size = size
    tmp_MBr = MBr(0,'-')
    tmp_EBr = EBr()
    
    new_EBr = EBr()
    new_EBr.status = 1
    new_EBr.fit = fit
    new_EBr.size = size
    new_EBr.setname(name)

    try:
        with open(Path, 'rb+') as file:
            bindata = file.read()
            tmp_MBr.set_bytes(bindata)

            tmp_partiton = next((partition for partition in tmp_MBr.partitions if partition.type == 'e'), None)
            if tmp_partiton == None :
                print("no se encotro una particion extendida")
                return
            if part_size > tmp_partiton.size:
                print('espacio insuficiente')
                return
            
            tmp_EBr.setBytes(bindata[(tmp_partiton.start):(tmp_partiton.start+33)])
            

            if tmp_EBr.status == 0:
                new_EBr.start = tmp_partiton.start

            else:
                num_LogicParts = 0
                while tmp_EBr.next != -1:
                    if num_LogicParts >= 26:
                        print("se llego al limite de particiones logicas")
                        return
                    if tmp_EBr.name == name.ljust(16)[:16]:
                        print('ya existe una particion con ese noMBre')
                        return

                    
                    tmp_EBr.setBytes(bindata[tmp_EBr.next:tmp_EBr.next+33])
                    part_size += tmp_EBr.size
                    num_LogicParts += 1

                if part_size > tmp_partiton.size:
                    print('espacio insuficiente')
                    return
                if tmp_EBr.name == name.ljust(16)[:16]:
                        print('ya existe una particion con ese noMBre')
                        return
                
                tmp_EBr.next = (tmp_EBr.start+tmp_EBr.size)
                file.seek(tmp_EBr.start)
                file.write(tmp_EBr.getBytes())

                new_EBr.start = (tmp_EBr.next)
            
            file.seek(new_EBr.start)
            file.write(new_EBr.getBytes())

            print('particion logica creada correctamente')
            print(f"Status: {new_EBr.status}")
            print(f"FIt: {new_EBr.fit}")
            print(f"Start: {new_EBr.start}")
            print(f"Size: {new_EBr.size}")
            print(f"Name: {new_EBr.name}")

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print("No se pudo leer la información del disco.")
        print("Exception type: ", exception_type)
        print("File name: ", filename)
        print("Line number: ", line_number)
        print('Error: ',e)
        return False

    pass

def mount_cmd(Path, Name):
    Path = Path.replace('"','')
    tmp_MBr = ReadDisk(Path)
    if tmp_MBr == None:
        print('no se encontro el disco')
        return None, None
    count = 0
    for partition in tmp_MBr.partitions:
        count += 1
        if partition.name == Name.ljust(16)[:16]:
            return partition, count
        
        if partition.type == 'e':
            with open(Path, 'rb+') as file:
                bindata = file.read()

                tmp_EBr:EBr = EBr()
                tmp_EBr.setBytes(bindata[(partition.start):(partition.start+33)])
                count += 1
                while tmp_EBr.name != Name.ljust(16)[:16]:

                    if tmp_EBr.next == -1:
                        print('no es una particion logica')
                        break
                    tmp_EBr.setBytes(bindata[(tmp_EBr.next):(tmp_EBr.next+33)])
                    count += 1
                
                if tmp_EBr.name == Name.ljust(16)[:16]:
                    return tmp_EBr, count
    return None, None

def mkfs_ext2(mount: Mount):
    tmp_part = mount.Partition

    #ext2 = (Part.size - Superblock.size)/(4+inodo.size+3(block.size))
    ext2 = (tmp_part.size - 98) / (4 + 137 + (3 * 64))
    ext2 = floor(ext2)


    current_time = datetime.now()
    newSuperBlock:SuperBlock = SuperBlock()
    newSuperBlock.umtiem = current_time.strftime("%d-%m-%Y %H:%M:%S")
    newSuperBlock.mnt_count = 1

    newSuperBlock.filesystem_type = 2
    newSuperBlock.inodecount = int(ext2)
    newSuperBlock.blockcount = int(3*ext2)
    newSuperBlock.free_inodecount = int(ext2)-2
    newSuperBlock.free_blockcount = int(3*ext2)-2

    newSuperBlock.bm_inode_start = int(tmp_part.start + 98)
    newSuperBlock.bm_block_start = int(newSuperBlock.bm_inode_start + ext2)
    newSuperBlock.inode_start = int(newSuperBlock.bm_block_start + (3*ext2))
    newSuperBlock.block_start = int(newSuperBlock.inode_start + (ext2*137))

    totalSize = int(newSuperBlock.block_start) + (3 * ext2 * 64)
    totalSize = totalSize - tmp_part.start
    if totalSize > tmp_part.size:  
        print('no hay espacio suficiente')
        return

    try:
        with open(mount.Path.replace(' ',''), 'rb+') as file:
            #Escrubir SuperBloque
            file.seek(tmp_part.start)
            file.write(newSuperBlock.getBytes())

            #Escribir Bitmap de Inodos
            file.write(b'0' * int(ext2))

            #Escribir Bitmap de Bloques
            file.write(b'0' * int(3*ext2))

            #Escribir Inodos
            Inodotmp = Inodo()
            file.write(Inodotmp.getBytes() * int(ext2))

            #Escribir Bloques
            Blocktmp = Block()
            file.write(Blocktmp.getBytes() * int(3*ext2))

            
            #Primer Inodo
            newInodo:Inodo = Inodo()
            newInodo.i_uid = 1
            newInodo.i_gid = 1
            newInodo.i_size = 0
            newInodo.i_atime = current_time.strftime("%d-%m-%Y %H:%M:%S")
            newInodo.i_ctime = current_time.strftime("%d-%m-%Y %H:%M:%S")
            newInodo.i_mtime = current_time.strftime("%d-%m-%Y %H:%M:%S")
            newInodo.i_block[0] = 0
            newInodo.i_type = 0
            newInodo.i_perm = 664;  ##  permisos  los primeros 3 bits Uusuario i_uid. los siguientes 3  grupo que pertenece y ultimos 3 permisos de otros usuarios.
            
            newBlock:Block = Block()
            newBlock.b_content[0].setName('.')
            newBlock.b_content[0].b_inodo = 0
            newBlock.b_content[1].setName('..')
            newBlock.b_content[1].b_inodo = 0
            newBlock.b_content[2].setName('users.txt') 
            newBlock.b_content[2].b_inodo = 1
            newBlock.b_content[3].setName('-') 
            newBlock.b_content[3].b_inodo = -1


            #inodo 1
            data = "1,G,root\n1,U,root,root,123\n";
            newInodo1:Inodo = Inodo()
            newInodo1.i_uid = 1
            newInodo1.i_gid = 1 
            newInodo1.i_size = len(data) + 64 # 64 es el tamaño del bloque
            newInodo1.i_atime = current_time.strftime("%d-%m-%Y %H:%M:%S")
            newInodo1.i_mtime = current_time.strftime("%d-%m-%Y %H:%M:%S")
            newInodo1.i_block[0] = 1
            newInodo1.i_type = 1
            newInodo1.i_perm = 664;
            #inodohijo + bloquehijo + inodopadre
            newInodo.i_size = newInodo1.i_size + 64 + 137
        
            newBlockFile:BlockFile = BlockFile()
            newBlockFile.setContent(data)

            #Crear Carpeta root  /  inodo 0
            file.seek(newSuperBlock.bm_inode_start)
            file.write(b'1' *2)

            file.seek(newSuperBlock.bm_block_start)
            file.write(b'1' *2)

            file.seek(newSuperBlock.inode_start)
            file.write(newInodo.getBytes())
            file.write(newInodo1.getBytes())

            file.seek(newSuperBlock.block_start)
            file.write(newBlock.getBytes())
            file.write(newBlockFile.getBytes())

            print('Sistema de archivos creado correctamente')



    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print("No se pudo leer la información del disco.")
        print("Exception type: ", exception_type)
        print("File name: ", filename)
        print("Line number: ", line_number)
        print('Error: ',e)
        return False

def mkfs_ext3(mount: Mount):
    tmp_part = mount.Partition

    #ext3 = (Part.size - Superblock.size)/(4+journaling.size+inodo.size+3(block.size))
    ext3 = (tmp_part.size - 98) / (4 + 1024 + 137 + (3 * 64))
    ext3 = floor(ext3)

    current_time = datetime.now()
    newSuperBlock:SuperBlock = SuperBlock()
    newSuperBlock.umtiem = current_time.strftime("%d-%m-%Y %H:%M:%S")
    newSuperBlock.mnt_count = 1

    newSuperBlock.filesystem_type = 3
    newSuperBlock.inodecount = int(ext3)
    newSuperBlock.blockcount = int(3*ext3)
    newSuperBlock.free_inodecount = int(ext3)-2
    newSuperBlock.free_blockcount = int(3*ext3)-2

    newSuperBlock.bm_inode_start = int(tmp_part.start + 98 + (ext3*189))
    newSuperBlock.bm_block_start = int(newSuperBlock.bm_inode_start + ext3)
    newSuperBlock.inode_start = int(newSuperBlock.bm_block_start + (3*ext3))
    newSuperBlock.block_start = int(newSuperBlock.inode_start + (ext3*137))


    try:
        with open(mount.Path.replace(' ',''), 'rb+') as file:
            #Escrubir SuperBloque
            file.seek(tmp_part.start)
            file.write(newSuperBlock.getBytes())

            Journaltmp = Journaling()
            file.write(Journaltmp.getBytes() * int(ext3))

            #Escribir Bitmap de Inodos
            file.write(b'0' * int(ext3))

            #Escribir Bitmap de Bloques
            file.write(b'0' * int(3*ext3))

            #Escribir Inodos
            Inodotmp = Inodo()
            file.write(Inodotmp.getBytes() * int(ext3))

            #Escribir Bloques
            Blocktmp = Block()
            file.write(Blocktmp.getBytes() * int(3*ext3))

            
            #Primer Inodo
            newInodo:Inodo = Inodo()
            newInodo.i_uid = 1
            newInodo.i_gid = 1
            newInodo.i_size = 0
            newInodo.i_atime = current_time.strftime("%d-%m-%Y %H:%M:%S")
            newInodo.i_ctime = current_time.strftime("%d-%m-%Y %H:%M:%S")
            newInodo.i_mtime = current_time.strftime("%d-%m-%Y %H:%M:%S")
            newInodo.i_block[0] = 0
            newInodo.i_type = 0
            newInodo.i_perm = 664;  ##  permisos  los primeros 3 bits Uusuario i_uid. los siguientes 3  grupo que pertenece y ultimos 3 permisos de otros usuarios.
            
            newBlock:Block = Block()
            newBlock.b_content[0].setName('.')
            newBlock.b_content[0].b_inodo = 0
            newBlock.b_content[1].setName('..')
            newBlock.b_content[1].b_inodo = 0
            newBlock.b_content[2].setName('users.txt') 
            newBlock.b_content[2].b_inodo = 1
            newBlock.b_content[3].setName('-') 
            newBlock.b_content[3].b_inodo = -1


            #inodo 1
            data = "1,G,root\n1,U,root,root,123\n";
            newInodo1:Inodo = Inodo()
            newInodo1.i_uid = 1
            newInodo1.i_gid = 1 
            newInodo1.i_size = len(data) + 64 # 64 es el tamaño del bloque
            newInodo1.i_atime = current_time.strftime("%d-%m-%Y %H:%M:%S")
            newInodo.i_ctime = current_time.strftime("%d-%m-%Y %H:%M:%S")
            newInodo1.i_mtime = current_time.strftime("%d-%m-%Y %H:%M:%S")
            newInodo1.i_block[0] = 1
            newInodo1.i_type = 1
            newInodo1.i_perm = 664;
            #inodohijo + bloquehijo + inodopadre
            newInodo.i_size = newInodo1.i_size + 64 + 137
        
            newBlockFile:BlockFile = BlockFile()
            newBlockFile.setContent(data)

            bindata = file.read()
            
            Journal1 = Journaling()
            Journal1.setBytes(bindata[tmp_part.start + 98:])
            Journal1.Operation = 'mkdir'.ljust(10)[:10]
            Journal1.Path = '/'.ljust(100)[:100]
            Journal1.content = 'raiz'.ljust(60)[:60]
            Journal1.Date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            file.seek(tmp_part.start + 98)
            file.write(Journal1.getBytes())

            Journal2 = Journaling()
            Journal2.setBytes(bindata[tmp_part.start + 98 + 189:])
            Journal2.Operation = 'mkfile'.ljust(10)[:10]
            Journal2.Path = '/users.txt'.ljust(100)[:100]
            Journal2.content = data.ljust(60)[:60]
            Journal2.Date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            file.write(Journal2.getBytes())



            #Crear Carpeta root  /  inodo 0,1
            file.seek(newSuperBlock.bm_inode_start)
            file.write(b'1' *2)

            file.seek(newSuperBlock.bm_block_start)
            file.write(b'1' *2)

            file.seek(newSuperBlock.inode_start)
            file.write(newInodo.getBytes())
            file.write(newInodo1.getBytes())

            file.seek(newSuperBlock.block_start)
            file.write(newBlock.getBytes())
            file.write(newBlockFile.getBytes())

            print('Sistema de archivos creado correctamente')

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print("No se pudo leer la información del disco.")
        print("Exception type: ", exception_type)
        print("File name: ", filename)
        print("Line number: ", line_number)
        print('Error: ',e)
        return False