import copy
import os
import sys
from typing import List
from structs import MBr, EBr, Partition, Mount, SuperBlock, Inodo, Block, BlockFile


def MBrReport(Path, mount:Mount):
    tmp_MBr:MBr = MBr(0,'-')

    with open(mount.Path.replace('"',''), 'rb') as file:
        bindata = file.read()
        tmp_MBr.set_bytes(bindata)
        
        if tmp_MBr == None:
            print('no se encontro el disco')
            return
        
        # Genera el reporte
        DotCode = f'''digraph G{{
            node [shape=plaintext fontname="Courier-bold"]
            tabla [label=<<table border="3" cellborder="1" cellspacing="2">
                <tr>
                    <td colspan="30" bgcolor="#E5D518" border="3" > REPORTE DE MBr </td> 
                </tr>
                <tr>
                    <td align="center" colspan="15" bgcolor="#C7C4A6">MBr_tamano: </td>
                    <td align="center" colspan="15" bgcolor="#C7C4A6"> {tmp_MBr.size} </td>
                </tr>
                <tr>
                    <td align="center" colspan="15" bgcolor="#C7C4A6">MBr_fecha_creacion: </td>
                    <td align="center" colspan="15" bgcolor="#C7C4A6"> {tmp_MBr.date} </td>
                </tr>
                <tr>
                    <td align="center" colspan="15" bgcolor="#C7C4A6">MBr_disk_asignature: </td>
                    <td align="center" colspan="15" bgcolor="#C7C4A6"> {tmp_MBr.dsk_signature} </td>
                </tr>
                <tr>
                    <td align="center" colspan="15" bgcolor="#C7C4A6">MBr_type_ajust: </td>
                    <td align="center" colspan="15" bgcolor="#C7C4A6"> {tmp_MBr.fit} </td>
                </tr>
        }}
        '''
        for partition in tmp_MBr.partitions:
            if partition.status != 1:
                continue

            DotCode += "   <tr>\n"
            if partition.type == 'p':
                DotCode += "       <td colspan=\"30\" align=\"left\" bgcolor=\"#EA2745\" border=\"1\"> PARTICION PRIMARIA</td> \n"
            elif partition.type == 'e':
                DotCode += "       <td colspan=\"30\" align=\"left\" bgcolor=\"#3BF088\" border=\"1\"> PARTICION EXTENDIDA</td> \n"
            DotCode += f'''   </tr>
    <tr>
        <td align="center" colspan="15" bgcolor="#C7C4A6"> part_status: </td> 
        <td align="center" colspan="15" bgcolor="#C7C4A6"> {str(partition.status)} </td> 
    </tr>
    <tr>
        <td align="center" colspan="15" bgcolor="#C7C4A6"> part_size: </td> 
        <td align="center" colspan="15" bgcolor="#C7C4A6"> {str(partition.size)} </td> 
    </tr>
    <tr>
        <td align="center" colspan="15" bgcolor="#C7C4A6"> part_start: </td> 
        <td align="center" colspan="15" bgcolor="#C7C4A6"> {str(partition.start)} </td> 
    </tr>
    <tr>
        <td align="center" colspan="15" bgcolor="#C7C4A6"> part_status: </td> 
        <td align="center" colspan="15" bgcolor="#C7C4A6"> {str(partition.status)} </td> 
    </tr>
    <tr>
        <td align="center" colspan="15" bgcolor="#C7C4A6"> part_type: </td> 
        <td align="center" colspan="15" bgcolor="#C7C4A6"> {partition.type} </td> 
    </tr>
    <tr>
        <td align="center" colspan="15" bgcolor="#C7C4A6"> part_fit: </td> 
        <td align="center" colspan="15" bgcolor="#C7C4A6"> {partition.fit} </td> 
    </tr>
    '''
            if partition.type == 'e':
                Logics = []
                tmp_EBr = EBr()
                tmp_EBr.setBytes(bindata[(partition.start):(partition.start + 33)])
                Logics.append(copy.copy(tmp_EBr))

                while tmp_EBr.next != -1:
                    tmp_EBr.setBytes(bindata[(tmp_EBr.next):(tmp_EBr.next + 33)])
                    Logics.append(copy.copy(tmp_EBr))

                for logic in Logics:
                    if logic.status != 1:
                        continue
                    DotCode += f'''
        <tr>
            <td colspan="30" align="left" bgcolor="#27EADE" border="1"> PARTICION LOGICA</td> 
        </tr>
        <tr>
            <td align="center" colspan="15" bgcolor="#C7C4A6"> part_status: </td> 
            <td align="center" colspan="15" bgcolor="#C7C4A6"> {logic.status} </td> 
        </tr>
        <tr>
            <td align="center" colspan="15" bgcolor="#C7C4A6"> part_fit: </td> 
            <td align="center" colspan="15" bgcolor="#C7C4A6"> {logic.fit} </td> 
        </tr>
        <tr>
            <td align="center" colspan="15" bgcolor="#C7C4A6"> part_size: </td> 
            <td align="center" colspan="15" bgcolor="#C7C4A6"> {logic.size} </td> 
        </tr>
        <tr>
            <td align="center" colspan="15" bgcolor="#C7C4A6"> part_start: </td> 
            <td align="center" colspan="15" bgcolor="#C7C4A6"> {logic.start} </td> 
        </tr>
        <tr>
            <td align="center" colspan="15" bgcolor="#C7C4A6"> part_next: </td> 
            <td align="center" colspan="15" bgcolor="#C7C4A6"> {logic.next} </td> 
        </tr>
        <tr>
            <td align="center" colspan="15" bgcolor="#C7C4A6"> part_name: </td> 
            <td align="center" colspan="15" bgcolor="#C7C4A6"> {logic.name.replace(' ','')} </td> 
        </tr>
                        '''
                        


        DotCode += "</table>>]\n"
        DotCode += "}\n" 
        WriteDot(DotCode, Path)

def DiskReport(Path, mount:Mount):

   with open(mount.Path.replace('"',''), 'rb+') as file:
        bindata = file.read()
        tmp_MBr:MBr = MBr(0,'-')
        tmp_MBr.set_bytes(bindata)

        DotCode = f'''
digraph {{ node [shape=plaintext fontname="Courier-bold" fontsize="40"]; A [label=<
<table border="10" CELLBORDER="10" cellspacing="0" width="300" HEIGHT="200">
  <tr>
    <td rowspan="3" width="300" bgcolor="#EA2745" height="200">MBR</td>'''
        partition: Partition
        for partition in tmp_MBr.partitions:
            if partition.status != 1:
                percent = round((partition.size / tmp_MBr.size) * 100)
                DotCode += f'''
    <td rowspan="3" width="300" bgcolor="#808080" height="200">Libre<br/>{partition.name.replace(' ','')}<br/>{str(percent)}% del disco</td>'''
            
            elif partition.type == 'p':
                percent =  round((partition.size / tmp_MBr.size) * 100)
                DotCode += f'''
    <td rowspan="3" width="300" bgcolor="#0C78F0" height="200">Primaria<br/>{partition.name.replace(' ','')}<br/>{str(percent)}% del disco</td>'''
            
            elif partition.type == 'e':
                Logics = []
                tmp_EBr = EBr()
                tmp_EBr.setBytes(bindata[(partition.start):(partition.start + 33)])
                Logics.append(copy.copy(tmp_EBr))

                while tmp_EBr.next != -1:
                    tmp_EBr.setBytes(bindata[(tmp_EBr.next):(tmp_EBr.next + 33)])
                    Logics.append(copy.copy(tmp_EBr))
                



                percent =  round((partition.size / tmp_MBr.size) * 100)
                DotCode += f'''
    <td>
      <table border="0" CELLBORDER="10" cellspacing="0" width="300" HEIGHT="200">
    <tr>
      <td colspan="3" width="300" bgcolor="#3BF088" height="200">Extendida<br/>{partition.name.replace(' ','')}<br/>{percent}% del disco</td>
    </tr>
    <tr>'''
                logic:EBr
                for logic in Logics:
                    if logic.status != 1:
                        percent =  round((logic.size / partition.size) * 100)
                        DotCode += f'''
      <td rowspan="3" width="300" bgcolor="#808080" height="200">Libre<br/>{logic.name.replace(' ','')}<br/>{percent}% de la extendida</td>'''
                    else:
                        percent =  round((logic.size / partition.size) * 100)
                        DotCode += f'''
      <td rowspan="3" width="300" bgcolor="#00EFEF" height="200">Logica<br/>{logic.name.replace(' ','')}<br/>{percent}% de la extendida</td>'''
                DotCode += f''' 
          </tr>
        </table>
     </td>'''
                
        DotCode += f'''
  </tr>
</table>
> ]; }}'''

        WriteDot(DotCode, Path)

def InodeReport(Path, mount:Mount):
    bindata = None
    Inodes: List[Inodo] = []
    DotCode = '''digraph G { rankdir=LR; forcelabels=true; node [shape=plaintext fontname="Courier" fontsize="40"]; '''
    try:
        
        file = open(mount.Path.replace('"',''), 'rb')
        bindata = file.read()

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
    
    if bindata == None:
        return
    
    SuperBlocktmp:SuperBlock = SuperBlock()
    SuperBlocktmp.setBytes(bindata[mount.Partition.start:])

    Inodotmp = Inodo()
    Inodotmp.setBytes(bindata[SuperBlocktmp.inode_start:])
    nexSeek = SuperBlocktmp.inode_start + 137
    
    while Inodotmp.i_size != -1:
        Inodes.append(copy.deepcopy(Inodotmp))
        Inodotmp.setBytes(bindata[nexSeek:])
        nexSeek += 137

    for x in range(0, len(Inodes)):
        DotCode += f'''
inode{x} [label = <
<table>
  <tr>
    <td colspan="2" bgcolor="#000080"><font color="white">INODO {x}</font></td>
  </tr>
  <tr>
    <td bgcolor="#87CEFA">NOMBRE</td>
    <td bgcolor="#87CEFA">VALOR</td>
  </tr>
  <tr>
    <td>i_uid</td>
    <td>{str(Inodes[x].i_uid)}</td>
  </tr>
  <tr>
    <td>i_gid</td>
    <td>{str(Inodes[x].i_gid)}</td>
  </tr>
  <tr>
    <td>i_size</td>
    <td>{str(Inodes[x].i_size)}</td>
  </tr>
  <tr>
    <td>i_atime</td>
    <td>{str(Inodes[x].i_atime)}</td>
  </tr>
  <tr>
    <td>i_ctime</td>
    <td>{str(Inodes[x].i_ctime)}</td>
  </tr>
  <tr>
    <td>i_mtime</td>
    <td>{str(Inodes[x].i_mtime)}</td>
  </tr>
  <tr>
    <td>i_block_1</td>
    <td port="0">{str(Inodes[x].i_block[0])}</td>
  </tr>
  <tr>
    <td>i_block_2</td>
    <td port="1">{str(Inodes[x].i_block[1])}</td>
  </tr>
  <tr>
    <td>i_block_3</td>
    <td port="2">{str(Inodes[x].i_block[2])}</td>
  </tr>
  <tr>
    <td>i_block_4</td>
    <td port="3">{str(Inodes[x].i_block[3])}</td>
  </tr>
  <tr>
    <td>i_block_5</td>
    <td port="4">{str(Inodes[x].i_block[4])}</td>
  </tr>
  <tr>
    <td>i_block_6</td>
    <td port="5">{str(Inodes[x].i_block[5])}</td>
  </tr>
  <tr>
    <td>i_block_7</td>
    <td port="6">{str(Inodes[x].i_block[6])}</td>
  </tr>
  <tr>
    <td>i_block_8</td>
    <td port="7">{str(Inodes[x].i_block[7])}</td>
  </tr>
  <tr>
    <td>i_block_9</td>
    <td port="8">{str(Inodes[x].i_block[8])}</td>
  </tr>
  <tr>
    <td>i_block_10</td>
    <td port="9">{str(Inodes[x].i_block[9])}</td>
  </tr>
  <tr>
    <td>i_block_11</td>
    <td port="10">{str(Inodes[x].i_block[10])}</td>
  </tr>
  <tr>
    <td>i_block_12</td>
    <td port="11">{str(Inodes[x].i_block[11])}</td>
  </tr>
  <tr>
    <td>i_block_13</td>
    <td port="12">{str(Inodes[x].i_block[12])}</td>
  </tr>
  <tr>
    <td>i_block_14</td>
    <td port="13">{str(Inodes[x].i_block[13])}</td>
  </tr>
  <tr>
    <td>i_block_15</td>
    <td port="14">{str(Inodes[x].i_block[14])}</td>
  </tr>
  <tr>
    <td>i_type</td>
    <td>{str(Inodes[x].i_type)}</td>
  </tr>
  <tr>
    <td>i_perm</td>
    <td>{str(Inodes[x].i_perm)}</td>
  </tr>
</table>
>]; '''

        if len(Inodes) > x+1:
            if Inodes[x+1].i_ctime != '-'.ljust(19)[:19]:
                DotCode += f'''inode{x} -> inode{x+1}'''

    DotCode += '}'
    WriteDot(DotCode, Path)

def BlockReport(Path, mount:Mount):
  bindata = None
  Inodes: List[Inodo] = []
  DotCode = '''digraph G { rankdir=LR; forcelabels=true; node [shape=plaintext fontname="Courier" fontsize="40"]; '''
  try:
      file = open(mount.Path.replace('"',''), 'rb')
      bindata = file.read()

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
    
  if bindata == None:
      return
    
  SuperBlocktmp:SuperBlock = SuperBlock()
  SuperBlocktmp.setBytes(bindata[mount.Partition.start:])

  Inodotmp = Inodo()
  Inodotmp.setBytes(bindata[SuperBlocktmp.inode_start:])
  nexSeek = SuperBlocktmp.inode_start + 137
  
  while Inodotmp.i_size != -1:
      Inodes.append(copy.deepcopy(Inodotmp))
      Inodotmp.setBytes(bindata[nexSeek:nexSeek+137])
      nexSeek += 137

  BlocksCount = 0
  tmpBlock:Block = Block()
  tmpBlockFile:BlockFile = BlockFile()
  
  for Inode in Inodes:
    #0-->carpeta 1-->archivo
    if Inode.i_type == 0:
      for x in Inode.i_block:
          if x == -1:
            continue
          ctmp = SuperBlocktmp.block_start+(x*64)
          tmpBlock.setBytes(bindata[SuperBlocktmp.block_start+(x*64):])
          DotCode += f'''
block{BlocksCount} [label = <
<table>
  <tr>
    <td bgcolor="#87CEFA">Bloque<br/>Carpeta</td>
    <td bgcolor="#87CEFA">   {BlocksCount} </td>
  </tr>
  <tr>
    <td>{tmpBlock.b_content[0].b_name.replace(' ', '')}</td>
    <td>{tmpBlock.b_content[0].b_inodo}</td>
  </tr>
  <tr>
    <td>{tmpBlock.b_content[1].b_name.replace(' ', '')}</td>
    <td>{tmpBlock.b_content[1].b_inodo}</td>
  </tr>  
  <tr>
    <td>{tmpBlock.b_content[2].b_name.replace(' ', '')}</td>
    <td>{tmpBlock.b_content[2].b_inodo}</td>
  </tr>  
  <tr>
    <td>{tmpBlock.b_content[3].b_name.replace(' ', '')}</td>
    <td>{tmpBlock.b_content[3].b_inodo}</td>
  </tr>
</table>
>];'''
    elif Inode.i_type == 1:
      for x in Inode.i_block:
          if x == -1:
            continue
          tmpBlockFile.setBytes(bindata[SuperBlocktmp.block_start+(x*64):])
          content = tmpBlockFile.b_content.replace(' ', '')
          content = content.replace('\n', '<br/>')
          DotCode += f'''
block{BlocksCount} [label = <
<table>
  <tr>
    <td bgcolor="#87CEFA">Bloque<br/>Archivo</td>
  </tr>
  <tr>
    <td>{content}</td>
  </tr>
</table>
>];'''
    BlocksCount += 1
  
  for x in range(0, BlocksCount-1):
      DotCode += f'''
block{x} -> block{x+1}'''
  DotCode += '\n}'

  WriteDot(DotCode, Path)
    

def WriteDot(GraphCode:str, Path:str):
    Path = Path.replace('"', '')
    Path = Path[:-4]
    directorio = os.path.dirname(Path)
    os.makedirs(directorio, exist_ok=True)
    

    NewFile= open('{}.dot'.format(Path),'w')
    NewFile.write(GraphCode)
    NewFile.close()

    os.system('dot -Tsvg {}.dot -o {}.svg'.format(Path,Path))

    print('Reporte generado con exito '+ Path)
