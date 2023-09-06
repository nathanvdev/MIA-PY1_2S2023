import os
import sys
from structs import MBR, EBR


##cambiar a funciones 


def ReadDisk(Path):
    try:
        tmp_mbr = MBR(0, 'f')
        with open(Path, 'rb+') as file:
            bindata = file.read()
            tmp_mbr.set_bytes(bindata)
            return tmp_mbr
            
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

def WriteDisk(Path, tmp_mbr, Name):

    try:
        with open(Path, 'rb+') as file:
            file.seek(0)
            file.write(tmp_mbr.getBytes())

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
    if Unit == "m":
        Size *= 1024
    NewMBR = MBR(Size, Fit)

    try:
        with open(Path, "wb+") as file:
            file.write(b'\x00' * 1024 * Size)
            file.seek(0)
            file.write(NewMBR.getBytes())

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
            mbruno = MBR(0,'f')
            mbruno.set_bytes(bindata)
            print(f"Tamaño del disco: {mbruno.size}")
            print(f"Fecha del disco: {mbruno.date}")
            print(f"Firma del disco: {mbruno.dsk_signature}")
            print(f"Ajuste del disco: {mbruno.fit}")

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
    if Unit == "m":
        Size *= 1024
    Name = Name.replace('"','')

    tmp_mbr = MBR(0,'f')

    tmp_mbr = ReadDisk(Path)
    if tmp_mbr == False:
        return


    for i in range(len(tmp_mbr.partitions)):
        if tmp_mbr.partitions[i].status == 0:
            tmp_mbr.partitions[i].status = 1
            tmp_mbr.partitions[i].type = Type
            tmp_mbr.partitions[i].fit = Fit
            tmp_mbr.partitions[i].size = int(Size)
            tmp_mbr.partitions[i].setname(Name)

            if tmp_mbr.partitions[i-1].size !=0:
                newStart = tmp_mbr.partitions[i-1].start + tmp_mbr.partitions[i-1].size
                tmp_mbr.partitions[i].start = newStart
            else:
                tmp_mbr.partitions[i].start = 148

            if tmp_mbr.partitions[i].type == 'e':

                newEBR = EBR()
                with open (Path, 'rb+') as filetmp:
                    filetmp.seek(tmp_mbr.partitions[i].start)
                    filetmp.write(newEBR.getBytes())
                
                with open(Path, 'rb') as tmpfile:
                    bindata = tmpfile.read()
                    tmpEBR = EBR()
                    tmpEBR.setBytes(bindata[tmp_mbr.partitions[i].start: tmp_mbr.partitions[i].start+33])

            WriteDisk(Path, tmp_mbr, Name)

            with open(Path, "rb") as file2:
                bindata = file2.read()
                mbruno = MBR(0,'f')
                mbruno.set_bytes(bindata)

                for tmp_partiton in mbruno.partitions:
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
    available_partitions = [partition for partition in tmp_mbr.partitions if partition.status == 2]

    if not available_partitions:
        print("Todas las particiones están llenas.")
        return    
        
    # Filtra las particiones con Size mayor que partition.size
    available_partitions = [partition for partition in available_partitions if Size <= partition.size]

    if not available_partitions:
        print("Ya no hay espacio para esta particion")
        return   

    if tmp_mbr.fit == 'f':
        available_partitions[0].status = 1
        available_partitions[0].type = Type
        available_partitions[0].fit = Fit
        available_partitions[0].size = int(Size)
        available_partitions[0].setname(Name)

    elif tmp_mbr.fit == 'b':
        #particion con el tamano mas pequeno
        min_partition = min(available_partitions, key=lambda partition: partition.size)
        min_partition.status = 1
        min_partition.type = Type
        min_partition.fit = Fit
        min_partition.size = int(Size)
        min_partition.setname(Name)

    elif tmp_mbr.fit == 'w':
        max_partition = max(available_partitions, key=lambda partition: partition.size)
        max_partition.status = 1
        max_partition.type = Type
        max_partition.fit = Fit
        max_partition.size = int(Size)
        max_partition.setname(Name)

    WriteDisk(Path, tmp_mbr, Name)

    with open(Path, "rb") as file2:
        bindata = file2.read()
        mbruno = MBR(0,'f')
        mbruno.set_bytes(bindata)

        for tmp_partiton in mbruno.partitions:
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

    
    tmp_mbr = ReadDisk(Path)
    if tmp_mbr == False:
        return


    for i in range(len(tmp_mbr.partitions)):
        if tmp_mbr.partitions[i].name == Name.ljust(16)[:16]:
            if not Positive:
                tmp_mbr.partitions[i].size += Add
            else:
                if tmp_mbr.partitions[i+1].size != 0:
                    result =  tmp_mbr.partitions[i+1].start - (tmp_mbr.partitions[i].start + tmp_mbr.partitions[i].size)
                    if Add >  result:
                        print('no hay sufuciente espacio')
                    else:
                        tmp_mbr.partitions[i].size += Add
            break 

    WriteDisk(Path, tmp_mbr, Name)
        
    with open(Path, "rb") as file2:
        bindata = file2.read()
        mbruno = MBR(0,'f')
        mbruno.set_bytes(bindata)

        for tmp_partiton in mbruno.partitions:
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
        
    try:
        tmp_mbr = MBR(0, 'f')
        #Leer el Disco
        with open(Path, 'rb+') as file:
            bindata = file.read()
            tmp_mbr.set_bytes(bindata)

        #Eliminar particion
        for tmp_partiton in tmp_mbr.partitions:
            if tmp_partiton.name == Name.ljust(16)[:16]:
                tmp_partiton.status = 2

                with open(Path, 'rb+') as file:
                    file.seek(0)
                    file.write(tmp_mbr.getBytes())

                    file.seek(tmp_partiton.start)
                    file.write(b'\x00' * 1024 * tmp_mbr.size)
                break
        

        with open(Path, "rb") as file2:
            bindata = file2.read()
            mbruno = MBR(0,'f')
            mbruno.set_bytes(bindata)

            for tmp_partiton in mbruno.partitions:
                if tmp_partiton.name == Name.ljust(16)[:16]:
                    print(f"Status: {tmp_partiton.status}")
                    print(f"Tipo: {tmp_partiton.type}")
                    print(f"FIt: {tmp_partiton.fit}")
                    print(f"Start: {tmp_partiton.start}")
                    print(f"Size: {tmp_partiton.size}")
                    print(f"Name: {tmp_partiton.name}")
                    break

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
    part_size = size
    tmp_mbr = MBR(0,'-')
    tmp_ebr = EBR()
    
    new_ebr = EBR()
    new_ebr.status = 1
    new_ebr.fit = fit
    new_ebr.size = size
    new_ebr.setname(name)

    try:
        with open(Path, 'rb+') as file:
            bindata = file.read()
            tmp_mbr.set_bytes(bindata)

            tmp_partiton = next((partition for partition in tmp_mbr.partitions if partition.type == 'e'), None)
            if tmp_partiton == None :
                print("no se encotro una particion extendida")
                return
            if part_size > tmp_partiton.size:
                print('espacio insuficiente')
                return
            
            tmp_ebr.setBytes(bindata[(tmp_partiton.start):(tmp_partiton.start+33)])
            part_size += tmp_ebr.size
            

            if tmp_ebr.status == 0:
                new_ebr.start = tmp_partiton.start

            else:
                num_LogicParts = 0
                while tmp_ebr.next != -1:
                    if num_LogicParts >= 26:
                        print("se llego al limite de particiones logicas")
                        return

                    
                    tmp_ebr.setBytes(bindata[tmp_ebr.next:tmp_ebr.next+33])
                    part_size += tmp_ebr.size
                    num_LogicParts += 1

                if part_size > tmp_partiton.size:
                    print('espacio insuficiente')
                    return
                
                tmp_ebr.next = (tmp_ebr.start+tmp_ebr.size)
                file.seek(tmp_ebr.start)
                file.write(tmp_ebr.getBytes())

                new_ebr.start = (tmp_ebr.start+tmp_ebr.size)
            file.seek(new_ebr.start)
            file.write(new_ebr.getBytes())


            
            
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


def mount_cmd(tokens):
    print("mount:", tokens)

def unmount_cmd(tokens):
    print("unmount:", tokens)

def mkfs_cmd(tokens):
    print("mkfs:", tokens)

def login_cmd(tokens):
    print("login:", tokens)

def logout_cmd(tokens):
    print("logout:", tokens)

def mkgrp_cmd(tokens):
    print("mkgrp:", tokens)

def rmgrp_cmd(tokens):
    print("rmgrp:", tokens)


