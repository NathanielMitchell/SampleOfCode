from sys import *

#CONSTANTS
DEBUG = False
SENTINEL = bytearray([0x00, 0xff, 0x00, 0x00, 0xff, 0x00])

storeBool = False
retBool = False
byteMode = False
bitMode = False
offset_true = 0
offset = 0
interval = 1
wrapperFile = ""
hiddenFile = ""

#This is a REALLY ugly way of doing this. Maybe we find a prettier way before we submit??
#This large, ugly loop basically checks each of the arguments passed in to see if they are 
#The expected arguments

for args in argv[1:]:
    if (args[:2] == "-s"):
        storeBool = True
    elif (args[:2] == "-r"):
        retBool = True
    elif (args[:2] == "-B"):
        byteMode = True
    elif (args[:2] == "-b"):
        bitMode = True
    elif (args[:2] == "-o"):
        offset_true = int(args[2:])
    elif (args[:2] == "-i"):
        interval = int(args[2:])
    elif (args[:2] == "-w"):
        wrapperFile = args[2:]
    elif (args[:2] == "-h"):
        hiddenFile = args[2:]
    if(DEBUG):
        print(args[:2])


#Checks to see if we are storing or retrieving data
if(storeBool):
    offset = offset_true

    #tries to open both files provided
    try:
        wf = open(wrapperFile, "rb")
    except:
        print(f"The file: {wrapperFile} does not exist")
        exit(1)
    try:
        hf = open(hiddenFile, "rb")
    except:
        print(f"The file: {hiddenFile} does not exist")
        exit(1)

    
    #opens the files as byte arrays
    wByteArray = bytearray(wf.read())
    hByteArray = bytearray(hf.read())
    before = [x for x in wByteArray]

    #close the files
    wf.close()
    hf.close()

    #checks for either byte or bit mode
    if(byteMode):  

        i = 0

        #iterating through the hidden file byte array and replacing bytes of the wrapper with bytes of the hidden file
        while (i < len(hByteArray)):

            # print(wByteArray[offset], hByteArray[i])
            wByteArray[offset] = hByteArray[i]
            offset += interval
            i+=1
        
        i = 0

        #this places the sentinel at the end of the hidden file data
        while (i < len(SENTINEL)):
            wByteArray[offset] = SENTINEL[i]
            offset += interval
            i += 1
        
    if(bitMode):
        
        i = 0

        while (i < len(hByteArray)):

            #iterating through the individual bytes of the hidden file
            #then placing specific bits of the hidden file in the lsb of the byte of the wrapper
            #then, after the whole byte is placed, we move to the next byte of hidden file
            for j in range(8):
                
                wByteArray[offset] &= 0xfe
                wByteArray[offset] |= ((hByteArray[i] & 0x80) >> 7)
                hByteArray[i] = ((hByteArray[i] << 1) & 0xff)
                offset += interval

            i += 1

        i = 0

        while (i < len(SENTINEL)):
            
            #same as the last for loop, but this time with the bits/ bytes of the sentinel
            for j in range(8):

                wByteArray[offset] &= 0xfe
                wByteArray[offset] |= ((SENTINEL[i] & 0x80) >> 7)
                SENTINEL[i] = ((SENTINEL[i] << 1) & 0xff)
                offset += interval
            
            i += 1

    #writting the new wrapper to stdout
    stdout.buffer.write(wByteArray)

#checking for retrieval
if (retBool):
    offset = offset_true

    #try to open the wrapper file
    try:
        wf = open(wrapperFile, "rb")
    except:
        print(f"The file: {wrapperFile} does not exist")
        exit(1)
    
    #turn the wrapper file into a byte array and instantiate an empty byte array for the hidden file
    wByteArray = bytearray(wf.read())
    hByteArray = bytearray()
    
    #close the wrapper file
    wf.close()

    #checking for byte mode
    if(byteMode):

        # run until the end of the wrapper array (this shouldn't happen)
        while (offset < len(wByteArray)):
            
            # store the correct bytes of the wrapper into the empty hidden file array
            # these bytes have to be converted from integers to the bytes type
            hByteArray += wByteArray[offset].to_bytes(1, 'big')

            # after we get six total bytes, we need to start checking to see if the last six bytes are the sentinel
            if(len(hByteArray) >= 6):
                if(hByteArray[-6:] == SENTINEL):
                    break

            offset += interval

    # checking for bit mode
    if(bitMode):

        # trying to open the file
        try:
            wf = open(wrapperFile, "rb")
        except:
            print(f"The file: {wrapperFile} does not exist")
            exit(1)
        
        # converting it to a byte array and instantiating an empty hidden byte array
        wByteArray = bytearray(wf.read())
        hByteArray = bytearray()

        # closing the file
        wf.close()

        # running until we're withing the last 8 bytes of the wrapper (this shouldn't occur) ((8 because otherwise we could have issues with the for loop))
        while (offset < len(wByteArray) - 8):

            byte = 0

            #iterating through the bytes of the wrapper and copying the lsb of each byte
            for j in range(8):
                byte |= (wByteArray[offset] & 0x01)
                if (j < 7):
                    byte <<= 1
                offset += interval

            # adding the byte to the hidden byte array and checking for the sentinel in the last six bytes
            hByteArray += byte.to_bytes(1, 'big')
            if (len(hByteArray) >= 6):
                if (hByteArray[-6:] == SENTINEL):
                    break
    
    # writing the file to stdout
    stdout.buffer.write(hByteArray)
    print()
    




