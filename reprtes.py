import copy
import os
from structs import MBr, EBr, Partition, Mount, SuperBlock, Inodo


def MBrReport(Path, mount:Mount):
    Path = Path.replace('"','')
    os.makedirs(Path, exist_ok=True)

    tmp_MBr:MBr = MBr(0,'-')

    with open(mount.Path, 'rb') as file:
        bindata = file.read()
        tmp_MBr.set_bytes(bindata)
        
        if tmp_MBr == None:
            print('no se encontro el disco')
            return
        
        # Genera el reporte
        DotCode = f'''digraph G{{
            node [shape=plaintext fontname="Courier New"]
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
                DotCode += "       <td colspan=\"30\" align=\"left\" bgcolor=\"#EA2745\" border=\"1\"> PARTICION EXTENDIDA</td> \n"
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
                tmp_EBr:EBr = EBr()
                with open(mount.Path, 'rb') as file:
                    bindata = file.read()
                    tmp_EBr.setBytes(bindata[(partition.start):(partition.start+33)])
                    
                    while tmp_EBr.next != -1:
                        if tmp_EBr.status != 1:
                            tmp_EBr.setBytes(bindata[(tmp_EBr.next):(tmp_EBr.next+33)])
                            continue
                        DotCode += f'''
        <tr>
            <td colspan="30" align="left" bgcolor="#27EADE" border="1"> PARTICION LOGICA</td> 
        </tr>
        <tr>
            <td align="center" colspan="15" bgcolor="#C7C4A6"> part_status: </td> 
            <td align="center" colspan="15" bgcolor="#C7C4A6"> {tmp_EBr.status} </td> 
        </tr>
        <tr>
            <td align="center" colspan="15" bgcolor="#C7C4A6"> part_fit: </td> 
            <td align="center" colspan="15" bgcolor="#C7C4A6"> {tmp_EBr.fit} </td> 
        </tr>
        <tr>
            <td align="center" colspan="15" bgcolor="#C7C4A6"> part_size: </td> 
            <td align="center" colspan="15" bgcolor="#C7C4A6"> {tmp_EBr.size} </td> 
        </tr>
        <tr>
            <td align="center" colspan="15" bgcolor="#C7C4A6"> part_start: </td> 
            <td align="center" colspan="15" bgcolor="#C7C4A6"> {tmp_EBr.start} </td> 
        </tr>
        <tr>
            <td align="center" colspan="15" bgcolor="#C7C4A6"> part_next: </td> 
            <td align="center" colspan="15" bgcolor="#C7C4A6"> {tmp_EBr.next} </td> 
        </tr>
        <tr>
            <td align="center" colspan="15" bgcolor="#C7C4A6"> part_name: </td> 
            <td align="center" colspan="15" bgcolor="#C7C4A6"> {tmp_EBr.name} </td> 
        </tr>
                        '''
                        tmp_EBr.setBytes(bindata[(tmp_EBr.next):(tmp_EBr.next+33)])

        DotCode += "</table>>]\n"
        DotCode += "}\n" 
        print(DotCode)

def DiskReport(Path, mount:Mount):
    Path = Path.replace('"','')
    os.makedirs(Path, exist_ok=True)

    tmp_MBr:MBr = MBr(0,'-')

    with open(mount.Path, 'rb') as file:
        bindata = file.read()
        tmp_MBr.set_bytes(bindata)
        if tmp_MBr == None:
            print('no se encontro el disco')
            return
        
        DotCode = f'''digraph {{
            node [shape=plaintext];
            A [label=<<TABLE BORDER="6" CELLBORDER="2" CELLSPACING="1" WIDTH="300" HEIGHT="200">
            <TR>
            <TD ROWSPAN="3" WIDTH="300" HEIGHT="200"> MBR </TD>
        }}'''


        part:Partition
        for part in tmp_MBr.partitions:
            if part.status != 1:
                continue
            if part.type == 'p':
                percentage_allocated = (part.size / tmp_MBr.size) * 100
                formatted_percentage = round(percentage_allocated * 100.0) / 100.0
                percentage_info = str(formatted_percentage) + " % del disco"
                DotCode += "<TD ROWSPAN=\"3\" WIDTH=\"300\" HEIGHT=\"200\"> PARTICION PRIMARIA <BR/>" + part.name + "<BR/>" + percentage_info + "</TD>\n"


            elif part.type == 'e':
                Logics = []
                tmp_EBr = EBr()
                tmp_EBr.setBytes(bindata[(part.start):(part.start + 33)])
                Logics.append(copy.copy(tmp_EBr))
                while tmp_EBr.next != -1:
                    tmp_EBr.setBytes(bindata[(tmp_EBr.next):(tmp_EBr.next + 33)])
                    Logics.append(copy.copy(tmp_EBr))

                percentage_allocated = (float(part.size) / tmp_MBr.size) * 100
                formatted_percentage = round(percentage_allocated, 2)
                percentage_info = f"{formatted_percentage} % del disco"

                DotCode += "<TD>\n"
                DotCode += "   <TABLE BORDER=\"2\" CELLBORDER=\"5\" CELLSPACING=\"3\" WIDTH=\"300\" HEIGHT=\"200\">\n"

                for x in range(Logics):
                    pass
    

