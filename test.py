from structs import SuperBlock, EBR, Inodo
import sys

# newEBR = EBR()
# with open('/home/nathan/test.bin', 'wb') as file:
#     file.write(newEBR.getBytes())

# with open('/home/nathan/test.bin', 'rb') as file:
#     bindata = file.read()
#     newEBR.setBytes(bindata)


# newSB = SuperBlock()
# with open('/home/nathan/test.bin', 'wb') as file:
#     file.write(newSB.getBytes())

# with open('/home/nathan/test.bin', 'rb') as file:
#     bindata = file.read()
#     newSB.setBytes(bindata)


# newIN = Inodo()

# with open('/home/nathan/test.bin', 'wb') as file:
#     file.write(newIN.getBytes())

# with open('/home/nathan/test.bin', 'rb') as file:
#     bindata = file.read()
#     newIN.setBytes(bindata)


newIN = Inodo()

for x in range(0,14):
    newIN.i_block[x] = 69

with open('/home/nathan/test.bin', 'wb') as file:
    file.write(newIN.getBytes())

with open('/home/nathan/test.bin', 'rb') as file:
    bindata = file.read()
    newIN.setBytes(bindata)

print('finish')

