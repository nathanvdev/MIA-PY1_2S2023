from datetime import datetime
import random

class EBR:
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

class MBR:
    def __init__(self, s,f):
        current_time = datetime.now()
        current_time = current_time.strftime("%d-%m-%Y %H:%M:%S")

        self.size = s                                    #int        --> 4 bytes   tamaño total del disco en bytes
        self.date = current_time                        #char[19]   --> 19 bytes fecha y hora de creación del disco
        self.dsk_signature = random.randint(0, 999)     #int        --> 4 bytes   número random entre 1 y 999
        self.fit = f                                    #char[1]    --> 1 byte  tipo de ajuste de las particiones (bf, ff, wf)
        self.partitions = []                            #partitons  --> 30 bytes
        self.partitions.append(Partition("-")) 
        self.partitions.append(Partition("-"))
        self.partitions.append(Partition("-"))
        self.partitions.append(Partition("-"))
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
        self.Partition = tmp_part
    
    def setID(self,count, name):
        return '68'+str(count)+name

        
            

