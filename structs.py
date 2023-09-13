from datetime import datetime
import random

class EBr:
    def __init__(self, n = '-'):
        self.status = 0                 #int 4bytes
        self.fit = '-'                  #char 1byte
        self.start = -1                 #int 4bytes    
        self.size = -1                  #int 4bytes
        self.next = -1                  #int 4bytes
        self.name = n.ljust(16)[:16]    #char 16bytes
                                ## -->> 33 bytes

    def getBytes(self):
        bytes = bytearray()
        bytes += self.status.to_bytes(4,byteorder='big')
        bytes += self.fit.encode('utf-8')
        bytes += self.start.to_bytes(4, byteorder='big', signed=True)
        bytes += self.size.to_bytes(4, byteorder='big', signed=True)
        bytes += self.next.to_bytes(4, byteorder='big', signed=True)
        bytes += self.name.encode('utf-8')
        return bytes
    
    def setBytes(self, bytes):
        self.status = int.from_bytes(bytes[0:4], byteorder='big')
        self.fit = bytes[4:5].decode('utf-8')
        self.start = int.from_bytes(bytes[5:9], byteorder='big', signed=True)
        self.size = int.from_bytes(bytes[9:13], byteorder='big', signed=True)
        self.next = int.from_bytes(bytes[13:17], byteorder='big', signed=True)
        self.name = bytes[17:33].decode('utf-8')

    def setname(self, name):
        self.name = name.ljust(16)[:16]

class Partition:
    def __init__(self,n):
        self.status = 0                #int    -> 4 bytes   # 0-> no usada 1-> en uso 2-> eliminada
        self.type = "-"                #char   -> 1 byte
        self.fit = "-"                 #char   -> 1 byte
        self.start = 0                 #int    -> 4 bytes
        self.size = 0                  #int    -> 4 bytes
        self.name = n.ljust(16)[:16]   #Char   -> 16 bytes
        
                                        #    ----> 30 bytes

    def getBytes(self):
        bytes = bytearray()
        bytes += self.status.to_bytes(4, byteorder="big")
        bytes += self.type.encode('utf-8')
        bytes += self.fit.encode("utf-8")
        bytes += self.start.to_bytes(4, byteorder="big")
        bytes += self.size.to_bytes(4, byteorder="big")
        bytes += self.name.encode("utf-8")
        return bytes
    
    def setBytes(self, bytes):
        self.status =  int.from_bytes(bytes[0:4], byteorder="big")
        self.type = bytes[4:5].decode("utf-8")
        self.fit = bytes[5:6].decode('utf-8')
        self.start = int.from_bytes(bytes[6:10], byteorder="big")
        self.size = int.from_bytes(bytes[10:14], byteorder="big")
        self.name = bytes[14:30].decode("utf-8")

    def setname(self, name):
        self.name = name.ljust(16)[:16]

class MBr:
    def __init__(self, s,f):
        current_time = datetime.now()
        current_time = current_time.strftime("%d-%m-%Y %H:%M:%S")

        self.size = s                                    #int        --> 4 bytes   tamaño total del disco en bytes
        self.date = current_time                        #char[19]   --> 19 bytes fecha y hora de creación del disco
        self.dsk_signature = random.randint(0, 999)     #int        --> 4 bytes   número random entre 1 y 999
        self.fit = f                                    #char[1]    --> 1 byte  tipo de ajuste de las particiones (bf, ff, wf)
        self.partitions = [Partition("-") for _ in range(4)]#partitons  --> 30 bytes
        #-------------> 118 bytes 
        

    def getBytes(self):
        bytes = bytearray()
        bytes += self.size.to_bytes(4, byteorder='big')
        bytes += self.date.encode('utf-8')
        bytes += self.dsk_signature.to_bytes(4, byteorder="big")
        bytes += self.fit.encode('utf-8')

        for x in self.partitions:
            bytes += x.getBytes()
        return bytes
    
    def set_bytes(self, bytes):
        self.size = int.from_bytes(bytes[0:4], byteorder="big")
        self.date = bytes[4:23].decode('utf-8')
        self.dsk_signature = int.from_bytes(bytes[23:27], byteorder="big")
        self.fit = bytes[27:28].decode('utf-8')

        start = 28
        finish = 58

        for x in self.partitions:
            x.setBytes(bytes[start:finish])
            start += 30
            finish += 30

class Mount:
    def __init__(self, count, name, path, tmp_part):
        self.id = self.setID(count,name)
        self.Path = path
        self.Partition:Partition = tmp_part
    
    def setID(self,count, name):
        return '68'+str(count)+name
    
class SuperBlock:
    def __init__(self):
        current_time = datetime.now()
        current_time = current_time.strftime("%d-%m-%Y %H:%M:%S")

        self.filesystem_type = -1               #int 4bytes
        self.inodecount = -1                    #int 4bytes
        self.blockcount = -1                    #int 4bytes
        self.free_blockcount = -1               #int 4bytes
        self.free_inodecount = -1               #int 4bytes
        self.mtime = current_time               #char 19bytes
        self.umtiem = '-'.ljust(19)[:19]         #char 19bytes   
        self.mnt_count = -1                     #int 4bytes
        self.magic = -1                         #int 4bytes
        self.inode_s = -1                       #int 4bytes
        self.block_s = -1                       #int 4bytes
        self.first_ino = -1                     #int 4bytes
        self.first_blo = -1                     #int 4bytes
        self.bm_inode_start = -1                #int 4bytes
        self.bm_block_start = -1                #int 4bytes
        self.inode_start = -1                   #int 4bytes
        self.block_start = -1                   #int 4bytes
        #-------------------------------------> 98 bytes
    def getBytes(self):
        bytes = bytearray()
        bytes += self.filesystem_type.to_bytes(4, byteorder='big', signed=True)
        bytes += self.inodecount.to_bytes(4, byteorder='big', signed=True)
        bytes += self.blockcount.to_bytes(4, byteorder='big', signed=True)
        bytes += self.free_blockcount.to_bytes(4, byteorder='big', signed=True)
        bytes += self.free_inodecount.to_bytes(4, byteorder='big', signed=True )
        bytes += self.mtime.encode('utf-8')
        bytes += self.umtiem.encode('utf-8')
        bytes += self.mnt_count.to_bytes(4, byteorder='big', signed=True)
        bytes += self.magic.to_bytes(4, byteorder='big', signed=True)
        bytes += self.inode_s.to_bytes(4, byteorder='big', signed=True)
        bytes += self.block_s.to_bytes(4, byteorder='big', signed=True)
        bytes += self.first_ino.to_bytes(4, byteorder='big', signed=True)
        bytes += self.first_blo.to_bytes(4, byteorder='big', signed=True)
        bytes += self.bm_inode_start.to_bytes(4, byteorder='big', signed=True)
        bytes += self.bm_block_start.to_bytes(4, byteorder='big', signed=True)
        bytes += self.inode_start.to_bytes(4, byteorder='big', signed=True)
        bytes += self.block_start.to_bytes(4, byteorder='big', signed=True)
        return bytes
    
    def setBytes(self, bytes):
        self.filesystem_type = int.from_bytes(bytes[0:4], byteorder='big', signed=True)
        self.inodecount = int.from_bytes(bytes[4:8], byteorder='big', signed=True)
        self.blockcount = int.from_bytes(bytes[8:12], byteorder='big', signed=True)
        self.free_blockcount = int.from_bytes(bytes[12:16], byteorder='big', signed=True)
        self.free_inodecount = int.from_bytes(bytes[16:20], byteorder='big', signed=True)
        self.mtime = bytes[20:39].decode('utf-8')
        self.umtiem = bytes[39:58].decode('utf-8')
        self.mnt_count = int.from_bytes(bytes[58:62], byteorder='big', signed=True)
        self.magic = int.from_bytes(bytes[62:66], byteorder='big', signed=True)
        self.inode_s = int.from_bytes(bytes[66:70], byteorder='big', signed=True)
        self.block_s = int.from_bytes(bytes[70:74], byteorder='big', signed=True)
        self.first_ino = int.from_bytes(bytes[74:78], byteorder='big', signed=True)
        self.first_blo = int.from_bytes(bytes[78:82], byteorder='big', signed=True)
        self.bm_inode_start = int.from_bytes(bytes[82:86], byteorder='big', signed=True)
        self.bm_block_start = int.from_bytes(bytes[86:90], byteorder='big', signed=True)
        self.inode_start = int.from_bytes(bytes[90:94], byteorder='big', signed=True)
        self.block_start = int.from_bytes(bytes[94:98], byteorder='big', signed=True)


class Inodo:
    def __init__(self):
        current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.i_uid = -1                 #int 4bytes
        self.i_gid = -1                 #int 4bytes
        self.i_size = -1                #int 4bytes
        self.i_atime = '-'.ljust(19)[:19]   #char 19bytes
        self.i_ctime = current_time         #char 19bytes
        self.i_mtime = '-'.ljust(19)[:19]   #char 19bytes
        self.i_block = [-1] * 15        #int 60bytes
        self.i_type = -1                #int 4bytes
        self.i_perm = -1                #int 4bytes
        #-------------------------------------> 137 bytes

    def getBytes(self):
        bytes = bytearray()
        bytes += self.i_uid.to_bytes(4, byteorder='big', signed=True)
        bytes += self.i_gid.to_bytes(4, byteorder='big', signed=True)
        bytes += self.i_size.to_bytes(4, byteorder='big', signed=True)
        bytes += self.i_atime.encode('utf-8')
        bytes += self.i_ctime.encode('utf-8')
        bytes += self.i_mtime.encode('utf-8')
        for x in self.i_block:
            bytes += x.to_bytes(4, byteorder='big', signed=True)
        bytes += self.i_type.to_bytes(4, byteorder='big', signed=True)
        bytes += self.i_perm.to_bytes(4, byteorder='big', signed=True)
        return bytes
    
    def setBytes(self, bytes):
        self.i_uid = int.from_bytes(bytes[0:4], byteorder='big', signed=True)
        self.i_gid = int.from_bytes(bytes[4:8], byteorder='big', signed=True)
        self.i_size = int.from_bytes(bytes[8:12], byteorder='big', signed=True)
        self.i_atime = bytes[12:31].decode('utf-8')
        self.i_ctime = bytes[31:50].decode('utf-8')
        self.i_mtime = bytes[50:69].decode('utf-8')
        start = 69
        finish = 73
        
        for x in range(0,14):
            self.i_block[x] = int.from_bytes(bytes[start:finish], byteorder='big', signed=True)
            start += 4
            finish += 4
        self.i_type = int.from_bytes(bytes[125:129], byteorder='big', signed=True)
        self.i_perm = int.from_bytes(bytes[133:137], byteorder='big', signed=True)

class Content:
    def __init__(self, n, p):
        self.b_name = n.ljust(12)[:12]  #char 12bytes
        self.b_inodo = p                #int 4bytes
        #-------------------------------------> 16 bytes

    def getBytes(self):
        bytes = bytearray()
        bytes += self.b_name.encode('utf-8')
        bytes += self.b_inodo.to_bytes(4, byteorder='big', signed=True)
        return bytes
    
    def setBytes(self, bytes):
        self.b_name = bytes[0:12].decode('utf-8')
        self.b_inodo = int.from_bytes(bytes[12:16], byteorder='big', signed=True)

    def setName(self, name):
        self.b_name = name.ljust(12)[:12]

class Block:
    def __init__(self):
        self.b_content = [Content('-', -1) for _ in range(4)]      #Content 64bytes
        #-------------------------------------> 64 bytes

    def getBytes(self):
        bytes = bytearray()
        for x in self.b_content:
            bytes += x.getBytes()
        return bytes
    
    def setBytes(self, bytes):
        start = 0
        finish = 4
        for x in range(0,3):
            self.b_content[x] = int.from_bytes(bytes[start:finish], byteorder='big', signed=True)
            start += 4
            finish += 4
    

class BlockFile:
    def __init__(self, n = '-'):
        self.b_content = n.ljust(64)[:64]  #char 64bytes

    def getBytes(self):
        bytes = bytearray()
        bytes += self.b_content.encode('utf-8')
        return bytes
    
    def setBytes(self, bytes):
        self.b_content = bytes[0:64].decode('utf-8')

    def setContent(self, content):
        self.b_content = content.ljust(64)[:64]

class Journaling:
    pass