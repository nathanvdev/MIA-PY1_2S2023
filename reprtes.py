import copy
import os
from structs import MBr, EBr, Partition, Mount, SuperBlock, Inodo


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


def WriteDot(GraphCode:str, Path:str):
    Path = Path.replace('"', '')
    directorio = os.path.dirname(Path)
    os.makedirs(directorio, exist_ok=True)
    

    NewFile= open('{}.dot'.format(Path),'w')
    NewFile.write(GraphCode)
    NewFile.close()

    os.system('dot -Tsvg {}.dot -o {}.svg'.format(Path,Path))

    print('Reporte generado con exito '+ Path)
