#! python
# (c) DL, UTA, 2009 - 2011
import  sys, string, time, math, pprint
global wordsize
global numregbits
global opcodesize
global addrsize
global memloadsize
global numregs
global regmask
global addmask
global nummask
global opcposition
global reg1position
global reg2position
global memaddrimmedposition
global realmemsize
global codeseg
global dataseg
global trapreglink
global trapval
global mem
global reg
global clock
global ic
global numcoderefs
global numdatarefs
global starttime
global curtime
global first_time_execute
first_time_execute = 0
global RAW
global pipeline_length
global j
global data_hazard
global scoreboard
global bnz_fetch_trace
global branch_predictor_1_bit
global pipeline_full_bootup
global loop_variable
global cache_width
global cache_size
global cache_associativity
global bits_cache_width
global bits_cache_size
global bits_cache_size_split
global bits_cache_associativity
global cache_type
global cache
global cache_data
global read_miss_cache
global read_hit_cache
global LRU
global LRU_data_cache
global hit_flag
global miss_flag
hit_flag = 0
miss_flag = 0
loop_variable = 0
pipeline_full_bootup = 0
bnz_fetch_trace = 0
branch_predictor_1_bit = "NOT TAKEN"
scoreboard = [["-" for x in range(8)] for x in range(1024)]
pipeline_length = 3
RAW = 0
wordsize = 24                                        # everything is a word
numregbits = 3                                       # actually +1, msb is indirect bit
opcodesize = 5
addrsize = wordsize - (opcodesize+numregbits+1)      # num bits in address
memloadsize = 1024                                # change this for larger programs
numregs = 2**numregbits
regmask = (numregs*2)-1                              # including indirect bit
addmask = (2**(wordsize - addrsize)) -1
nummask = (2**(wordsize))-1
opcposition = wordsize - (opcodesize + 1)            # shift value to position opcode
reg1position = opcposition - (numregbits +1)            # first register position
reg2position = reg1position - (numregbits +1)
memaddrimmedposition = reg2position                  # mem address or immediate same place as reg2
realmemsize = memloadsize * 1                        # this is memory size, should be (much) bigger than a program
#memory management regs
codeseg = numregs - 1                                # last reg is a code segment pointer
dataseg = numregs - 2                                # next to last reg is a data segment pointer
#ints and traps
trapreglink = numregs - 3                            # store return value here
trapval     = numregs - 4                            # pass which trap/int
mem = [0] * realmemsize                              # this is memory, init to 0, list initialize. listsize is [0] * n
reg = [0] * numregs                                  # registers, same with regs
clock = 0                                            # initialize clock
ic = 0                                               # instruction count
numcoderefs = 0                                      # number of times instructions read
numdatarefs = 0                                      # number of times data read
starttime = time.time()
curtime = starttime


def startexechere ( p ):
    # start execution at this address
    reg[ codeseg ] = p    
def loadmem():                                       # get binary load image
  curaddr = 0
  for line in open("a.out", 'r').readlines():
    token = string.split( string.lower( line ))      # first token on each line is mem word, ignore rest
    if ( token[ 0 ] == 'go' ):
        startexechere(  int( token[ 1 ] ) )
    else:    
        mem[ curaddr ] = int( token[ 0 ], 0 )                
        curaddr = curaddr = curaddr + 1
def getcodemem ( a ):
    # get code memory at this address
    memval = mem[ a + reg[ codeseg ] ]
    return ( memval )
def putdatamem ( a ):
    regval = reg[reg1]
    return regval
def getdatamem ( a ):
    global numdatarefs, line_number, set_number, word_number, cache_type,replace_block, no_replace
    if(cache_type == 'U'):
        in_cache(a)
        if(cache_associativity != 1):
            no_replace = 0
            memval = cache[line_number][replace_block][0]
        elif(cache_associativity == 1 or no_replace == 1):
            no_replace = 0
            memval = cache[line_number][set_number][0]

    if(cache_type == 'S'):
        in_cache_data(a)
        if(cache_associativity != 1):
            no_replace = 0
            memval = cache_data[line_number][replace_block][0]
        elif(cache_associativity == 1 or no_replace == 1):
            no_replace = 0
            memval = cache_data[line_number][set_number][0]

    # memval = mem[ a + reg[ dataseg ] ]
    numdatarefs += 1
    return ( memval )
def getregval ( r ):
    # get reg or indirect value
    if ( (r & (1<<numregbits)) == 0 ):               # not indirect
       rval = reg[ r ] 
    else:
       rval = getdatamem( reg[ r - numregs ] )       # indirect data with mem address, when indirect, out of 4 bits,
                                                     # MSB set: eg - 1011(*3). So 8 added, subtract that 8 and pass to
                                                     # next function to get true reg value.
    return ( rval )
def checkres( v1, v2, res):
    v1sign = ( v1 >> (wordsize - 1) ) & 1
    v2sign = ( v2 >> (wordsize - 1) ) & 1
    ressign = ( res >> (wordsize - 1) ) & 1
    if ( ( v1sign ) & ( v2sign ) & ( not ressign ) ):
      return ( 1 )
    elif ( ( not v1sign ) & ( not v2sign ) & ( ressign ) ):
      return ( 1 )
    else:
      return( 0 )
def dumpstate ( d ):
    if ( d == 1 ):
        print reg
    elif ( d == 2 ):
        print mem
    elif ( d == 3 ):

        print 'clock=', clock, 'IC=', ic, 'Coderefs=', numcoderefs,'Datarefs=', numdatarefs, 'Start Time=', starttime, 'Currently=', time.time()
        print("\nSCOREBOARD:")
        print("                        "+ "R1   R2   R3   R4   R5   R6   R7   R8")
        for x in range(0, count_trace):
            print("instruction number " + str(x+1) + ": " + str((scoreboard)[x]))
        print("\nread hit cache: " + str(read_hit_cache))
        print("read miss cache: " + str(read_miss_cache))
def trap ( t ):
    # unusual cases
    # trap 0 illegal instruction
    # trap 1 arithmetic overflow
    # trap 2 sys call
    # trap 3+ user
    rl = trapreglink                            # store return value here
    rv = trapval
    if ( ( t == 0 ) | ( t == 1 ) ):
       dumpstate( 1 )
       dumpstate( 2 )
       dumpstate( 3 )
    elif ( t == 2 ):                          # sys call, reg trapval has a parameter
       what = reg[ trapval ] 
       if ( what == 1 ):
           a = a        #elapsed time
    return ( -1, -1 )
    return ( rv, rl )

# opcode type (1 reg, 2 reg, reg+addr, immed), mnemonic
opcodes = { 1: (2, 'add'), 2: ( 2, 'sub'), 
            3: (1, 'dec'), 4: ( 1, 'inc' ),
            7: (3, 'ld'),  8: (3, 'st'), 9: (3, 'ldi'),
           12: (3, 'bnz'), 13: (3, 'brl'),
           14: (1, 'ret'),
           16: (3, 'int') }
startexechere( 0 )                                  # start execution here if no "go"
loadmem()                                           # load binary executable
ip = 0                                     # start execution at codeseg location 0
ir = [0] * 1024
# while instruction is not halt
def trace():
    global opcode,reg1, regdata, memdata, operand1, operand2, addr, tval, treg, reg2

    trace = "STAGE: EXECUTE "

    if (opcode == 1):
        trace += "add "
    elif (opcode == 2):
        trace += "sub "
    elif (opcode == 3):
        trace += "dec "
    elif (opcode == 4):
        trace += "inc "
    elif (opcode == 7):
        trace += "ld "
    elif (opcode == 8):
        trace += "st "
    elif (opcode == 9):
        trace += "ldi "
    elif (opcode == 12):
        trace += "bnz "
    elif (opcode == 13):
        trace += "brl "
    elif (opcode == 14):
        trace += "ret "
    elif (opcode == 16):
        trace += "int "

    if((reg1 & 0x80) >> 3 == 1):
        reg1_temp = reg1 - 8
        trace = trace + "*" + str(reg1_temp)
    else:
        reg1_temp = reg1
        trace = trace + str(reg1_temp) + " "

    if(opcode == 7 or opcode == 9 or opcode == 12 or opcode == 8 or opcode == 13 or opcode == 16):
        trace = trace + str(addr) + " "

    elif(opcode == 1 or opcode == 2 ):
        if(reg2 > 7):
          reg2_temp = reg2 - 8
          trace = trace + "*" + str(reg2_temp)
        else:
          reg2_temp = reg2
          trace = trace + str(reg2_temp) + " "

    print(trace)

def create_cache():
    global cache
    global cache_data
    global valid, valid_data, line_tag, line_tag_data, line_tag, line_tag_data, LRU, LRU_data_cache

    if(cache_type == 'U'):
        LRU = [[0 for x in range(int(cache_associativity))] for x in range(int(cache_size))]
        cache = [[[0 for k in xrange(int(cache_width))] for j in xrange(int(cache_associativity))] for i in xrange(int(cache_size))]
        print("CACHE:")
        pprint.pprint(cache)
        print("\n")
        print("valid array:")
        valid = [[("false") for x in xrange(int(cache_associativity))] for y in xrange(int(cache_size))]
        line_tag = [0 for x in xrange(cache_size)]
        pprint.pprint(valid)
        print("tag array:")
        pprint.pprint(line_tag)
        print("\n")

        for y in xrange(int(cache_size)):                               #seed the LRU fields
            for x in xrange(int(cache_associativity)):
                LRU[y][x] = x

        print("LRU:")
        pprint.pprint(LRU)

    elif(cache_type == 'S'):
        LRU = [[0 for x in range(int(cache_associativity))] for x in range(int(cache_size))]
        LRU_data_cache = [[0 for x in range(int(cache_associativity))] for x in range(int(cache_size))]
        cache_data = [[[0 for k in xrange(int(cache_width))] for j in xrange(int(cache_associativity))] for i in xrange(int(cache_size))]
        cache = [[[0 for k in xrange(int(cache_width))] for j in xrange(int(cache_associativity))] for i in xrange(int(cache_size))]
        print("cache_instr: ")
        pprint.pprint(cache)

        print("cache_data: ")
        pprint.pprint(cache_data)

        print("valid array for instruction cache:")
        valid = [[("false") for x in xrange(int(cache_associativity))] for x in xrange(cache_size)]
        line_tag = [0 for x in xrange((cache_size))]
        pprint.pprint(valid)
        print("tag_bits array for instruction cache:")
        pprint.pprint(line_tag)
        # print("\n")

        print("\n")
        print("valid array for data cache:")
        valid_data = [["false" for x in xrange(int(cache_associativity))] for x in xrange(cache_size)]
        line_tag_data = [0 for x in xrange((cache_size))]
        pprint.pprint(valid)
        print("tag_bits array for data cache:")
        pprint.pprint(line_tag_data)
        print("\n")

        for y in xrange(cache_size):                               #seed the LRU fields
            for x in xrange(int(cache_associativity)):
                LRU[y][x] = x

        for y in xrange(cache_size):                               #seed the LRU fields
            for x in xrange(int(cache_associativity)):
                LRU_data_cache[y][x] = x

def decode_cache():
    global ip, loop_variable, cache_associativity, cache_size,cache_width, bits_cache_associativity
    global bits_cache_width, bits_tag, memloadsize,cache_type, bits_cache_size, bits_cache_size_split
    global valid, valid_data, read_hit_cache, read_miss_cache, line_tag, line_tag_data, bits_tag_split
    global word_number, line_number, set_number

    if(cache_width == 2):
        bits_cache_width = 1
    elif(cache_width == 4):
        bits_cache_width = 2

    if(cache_size == 4):
        if(cache_type == 'S'):
            cache_size /= 2
            bits_cache_size = 1
            bits_cache_size_split = 1
        else:
            bits_cache_size = 2
            bits_cache_size_split =0

#        if(cache_width == 4):
#            bits_cache_size -= 1
#        if(cache_associativity == str(4)):
#            bits_cache_size -= 1
    elif(cache_size == 16):
        if(cache_type == 'S'):
            cache_size /= 2
            bits_cache_size = 3
            bits_cache_size_split = 3
        else:
            bits_cache_size = 4
            bits_cache_size_split = 0
#        if(cache_width == 4):
#           bits_cache_size -= 1
#        if(cache_associativity == str(4)):
#            bits_cache_size -= 1
    if(cache_type == 'U'):
        print("Total Cache size in words = " + str(cache_width * cache_size))
    elif(cache_type == 'S'):
        print("Size of Data and Instruction Cache each(in words) is: " + str((cache_size/2) * cache_width) + "\n")

    if(cache_width * cache_size == 8):
        if(cache_associativity == 1):
            if(cache_associativity == 1):
                bits_cache_associativity = 0
        elif(cache_associativity == str(4)):
                if(cache_type == "S"):
                    print("With a Seperate Instruction and Data Cache, width = 2 and no. of lines = 4, the number of lines are already 1 for each seperate cache. Can't go any lower with set associativity")
                    bits_cache_associativity = 0
                    cache_associativity = 1
                elif(cache_type == "U"):
                    cache_size /= 4
                    bits_cache_size -= 2
                    bits_cache_associativity = 2

    elif(cache_width * cache_size != 8):
        if(cache_associativity == 1):
            if(cache_associativity == 1):
                bits_cache_associativity = 0
        elif(cache_associativity == str(4)):
                cache_size /= 4
                bits_cache_associativity = 2
                bits_cache_size -= 2
                if(cache_type == "S"):
                    bits_cache_size_split -= 2

    print("cache width bits:")
    print(bits_cache_width)

    print("cache line bits:")
    print(bits_cache_size)

    print("split cache line bits:")
    print(bits_cache_size_split)

    print("cache associativity bits:")
    print(bits_cache_associativity)

    print("total mem bits:")
    print(int(math.log(memloadsize,2)))
    bits_tag = int(math.log(memloadsize,2)) - bits_cache_size - bits_cache_width
    print("tag bits:")
    print(bits_tag)

    if(cache_type == "S"):
        bits_tag_split = int(math.log(memloadsize,2)) - bits_cache_size_split - bits_cache_width
        print("Data Cache tag bits:")
        print(bits_tag_split)

#    ip = 0
#    print("\n")

def in_cache(ip):
    global line_number, word_number, read_miss_cache, read_hit_cache, set_number, LRU, hit_flag, miss_flag
    tag = ip >> (int(math.log(memloadsize,2)) - bits_tag)
    if(bits_cache_width == 1):
        mask = 1
    else:
        mask = 3
    word_number = ip & mask

    if(cache_size == 8):
        mask = 7
    if(cache_size == 4):
        mask = 3
    if(cache_size == 16 ):
        mask = 15
    if(cache_size == 2):
        mask = 1
    if(cache_size == 1):
        mask = 0
    line_number = (ip >> bits_cache_width) & mask

    if(bits_cache_associativity == 2):
        mask = 3
        set_number = (ip >> bits_cache_size + bits_cache_width) & mask
    else:
        set_number = 0

    print("ip " + str((ip)) + "\n")
    print("word number: " + str(bin(word_number)) + "\n")
    print("line number: " + str(bin(line_number)) + "\n")
    print("set number: " + str(bin(set_number)) + "\n")
    print("tag: " + str(bin(tag)) + "\n")

# if(cache_type == "U"):
#     if(line_number <= cache_size):
    if(line_tag[line_number] == tag and (valid[line_number][set_number]) == "true"):
        hit_flag = 1
        for x in xrange(0, int(cache_associativity)):
            if(LRU[line_number][x] == int(cache_associativity) - 1):
                LRU[line_number][x] = 0
            else:
                LRU[line_number][x] += 1
    else:
        read_line_cache(ip)
        valid[line_number][set_number] = "true"
        line_tag[line_number] = tag
        miss_flag = 1


def in_cache_data(ip):
    global line_number, word_number, read_miss_cache, read_hit_cache, set_number, LRU, hit_flag, miss_flag
    tag = ip >> (int(math.log(memloadsize,2)) - bits_tag)
    if(bits_cache_width == 1):
        mask = 1
    else:
        mask = 3
    word_number = ip & mask

    if(cache_size == 8):
        mask = 7
    if(cache_size == 4):
        mask = 3
    if(cache_size == 16 ):
        mask = 15
    if(cache_size == 2):
        mask = 1
    if(cache_size == 1):
        mask = 0
    line_number = (ip >> bits_cache_width) & mask

    if(bits_cache_associativity == 2):
        mask = 3
        set_number = (ip >> bits_cache_size + bits_cache_width) & mask
    else:
        set_number = 0

    print("ip data " + str((ip)) + "\n")
    print("word number data: " + str(bin(word_number)) + "\n")
    print("line number data: " + str(bin(line_number)) + "\n")
    print("set number data: " + str(bin(set_number)) + "\n")
    print("tag data: " + str(bin(tag)) + "\n")

# if(cache_type == "U"):
#     if(line_number <= cache_size):
    if(line_tag_data[line_number] == tag and (valid_data[line_number][set_number]) == "true"):
        hit_flag = 1
        for x in xrange(0, int(cache_associativity)):
            if(LRU_data_cache[line_number][x] == int(cache_associativity) - 1):
                LRU_data_cache[line_number][x] = 0
            else:
                LRU_data_cache[line_number][x] += 1
    else:
        read_line_cache_data(ip)
        valid_data[line_number][set_number] = "true"
        line_tag_data[line_number] = tag
        miss_flag = 1


def read_line_cache(addr):
    global line_number, mem, cache, cache_associativity, cache_width, replace_block, no_replace

    temp_ip = addr
    if(valid[line_number][0] == "false" or cache_associativity == 1):              #read in the whole line only
        replace_block = 0                                                          # if invalid(i.e first time)
        for x in range(0, int(cache_associativity)):
            if(x != 0):
                if(cache_width == 2 and cache_size == 4):
                    temp_ip += 6
                elif(cache_width == 4 and cache_size == 4):
                    temp_ip += 12
                elif(cache_width == 2 and cache_size == 1):
                    temp_ip += 6
                elif(cache_width == 4 and cache_size == 1):
                    temp_ip += 12
            for y in range(0,int(cache_width)):
                (cache[line_number][x][y]) = (mem[temp_ip])
                temp_ip += 1

    else:
        if(int(cache_associativity) > 1):
            for x in xrange(0, int(cache_associativity)):
                if(LRU[line_number][x] == int(cache_associativity) - 1):
                    replace_block = x
                    break
            for x in xrange(0, int(cache_associativity)):
                LRU[line_number][x] += 1
            LRU[line_number][replace_block] = 0


        for y in range(0,int(cache_width)):
            (cache[line_number][replace_block][y]) = (mem[temp_ip])
            temp_ip += 1

def read_line_cache_data(addr):
    global line_number, mem, cache, cache_associativity, cache_width, replace_block, no_replace

    temp_ip = addr
    if(valid_data[line_number][0] == "false" or cache_associativity == 1):              #read in the whole line only
        replace_block = 0                                                          # if invalid(i.e first time)
        for x in range(0, int(cache_associativity)):
            if(x != 0):
                if(cache_width == 2 and cache_size == 4):
                    temp_ip += 6
                elif(cache_width == 4 and cache_size == 4):
                    temp_ip += 12
                elif(cache_width == 2 and cache_size == 1):
                    temp_ip += 6
                elif(cache_width == 4 and cache_size == 1):
                    temp_ip += 12
            for y in range(0,int(cache_width)):
                (cache_data[line_number][x][y]) = (mem[temp_ip])
                temp_ip += 1

    else:
        if(int(cache_associativity) > 1):
            for x in xrange(0, int(cache_associativity)):
                if(LRU_data_cache[line_number][x] == int(cache_associativity) - 1):
                    replace_block = x
                    break
            for x in xrange(0, int(cache_associativity)):
                LRU_data_cache[line_number][x] += 1
            LRU_data_cache[line_number][replace_block] = 0


        for y in range(0,int(cache_width)):
            (cache_data[line_number][replace_block][y]) = (mem[temp_ip])
            temp_ip += 1


    # print("memory:")
    # for x in range(0, memloadsize):
    #     print(str(x) + ": " + str((mem[x])))
    print("data cache")
    pprint.pprint(cache_data)

def fetch():
    global ip, clock, numcoderefs
    global ir, bnz_fetch_trace, pipeline_full_bootup, loop_variable, branch_predictor_1_bit, hit_flag, miss_flag
    global read_miss_cache, read_hit_cache

    if(ip < pipeline_length - 1 and pipeline_full_bootup == 0):
        clock += 1
    else:
        pipeline_full_bootup = 1

    if(branch_predictor_1_bit == "TAKEN"):
        in_cache(loop_variable)
        ir[loop_variable] = int(cache[line_number][set_number][word_number])    # - fetch the branch address because predcitction is "TAKEN"
        opcode = ir[loop_variable] >> opcposition
        reg1   = (ir[loop_variable] >> reg1position) & regmask
        reg2   = (ir[loop_variable] >> reg2position) & regmask
        addr   = (ir[loop_variable]) & addmask

    else:
        in_cache(ip)
        ir[ip] = (cache[line_number][set_number][word_number])                            # - fetch
        opcode = ir[ip] >> opcposition
        reg1   = (ir[ip] >> reg1position) & regmask
        reg2   = (ir[ip] >> reg2position) & regmask
        addr   = (ir[ip]) & addmask


    trace = "STAGE: FETCH "
    if (opcode == 1):
        trace += "add "
    elif (opcode == 2):
        trace += "sub "
    elif (opcode == 3):
        trace += "dec "
    elif (opcode == 4):
        trace += "inc "
    elif (opcode == 7):
        trace += "ld "
    elif (opcode == 8):
        trace += "st "
    elif (opcode == 9):
        trace += "ldi "
    elif (opcode == 12):
        trace += "bnz "
    elif (opcode == 13):
        trace += "brl "
    elif (opcode == 14):
        trace += "ret "
    elif (opcode == 16):
        trace += "int "

    if((reg1 & 0x80) >> 3 == 1):
        reg1_temp = reg1 - 8
        trace = trace + "*" + str(reg1_temp)
    else:
        reg1_temp = reg1
        trace = trace + str(reg1_temp) + " "

    if(opcode == 7 or opcode == 9 or opcode == 12 or opcode == 8 or opcode == 13 or opcode == 16):
        trace = trace + str(addr) + " "

    elif(opcode == 1 or opcode == 2 ):
        if(reg2 > 7):
          reg2_temp = reg2 - 8
          trace = trace + "*" + str(reg2_temp)
        else:
          reg2_temp = reg2
          trace = trace + str(reg2_temp) + " "


    print(trace)
    print("CLOCK = " + str(clock) + "\n")

    if(bnz_fetch_trace == 0):
        numcoderefs += 1
        if(hit_flag == 1):
            hit_flag = 0
            read_hit_cache += 1
        elif(miss_flag == 1):
            miss_flag = 0
            read_hit_cache  += 1
            read_miss_cache += 1

#   ip = ip + 1
#   print(ir)


def decode():
    global opcode,reg1,reg1position, regdata, memdata, operand1, operand2, addr, tval, treg, reg2, clock
    global reg1_temp, reg2_temp, opcode_prev, RAW

    opcode = ir[ip] >> opcposition                       # - decode
    reg1   = (ir[ip] >> reg1position) & regmask
    reg2   = (ir[ip] >> reg2position) & regmask
    addr   = (ir[ip]) & addmask

    trace = "STAGE: DECODE "

    if (opcode == 1):
        trace += "add "
    elif (opcode == 2):
        trace += "sub "
    elif (opcode == 3):
        trace += "dec "
    elif (opcode == 4):
        trace += "inc "
    elif (opcode == 7):
        trace += "ld "
    elif (opcode == 8):
        trace += "st "
    elif (opcode == 9):
        trace += "ldi "
    elif (opcode == 12):
        trace += "bnz "
    elif (opcode == 13):
        trace += "brl "
    elif (opcode == 14):
        trace += "ret "
    elif (opcode == 16):
        trace += "int "

    if((reg1 & 0x80) >> 3 == 1):
        reg1_temp = reg1 - 8
        trace = trace + "*" + str(reg1_temp)
    else:
        reg1_temp = reg1
        trace = trace + str(reg1_temp) + " "

    if(opcode == 7 or opcode == 9 or opcode == 12 or opcode == 8 or opcode == 13 or opcode == 16):
        trace = trace + str(addr) + " "

    elif(opcode == 1 or opcode == 2 ):
        if(reg2 > 7):
          reg2_temp = reg2 - 8
          trace = trace + "*" + str(reg2_temp)
        else:
          reg2_temp = reg2
          trace = trace + str(reg2_temp) + " "

    if(reg1 > 7):
        reg1_temp = reg1 - 8
    else:
        reg1_temp = reg1

    if(reg2 > 7):
        reg2_temp = reg2 - 8
    else:
        reg2_temp = reg2

    if(first_time_execute == 1 and RAW == 0):
        if(opcode_prev == 9 or opcode_prev == 7 or opcode_prev == 1 or opcode_prev == 2 or opcode_prev == 3 or opcode_prev == 4 or opcode_prev == 13 or opcode_prev == 16): #write in previous stage
            if(opcode == 1 or opcode == 2):                     #these instructions read registers
                if(reg1_prev == reg2_temp):
                    RAW = 1
                    print(trace)
                    print("CLOCK = " + str(clock))
                    print("DATA HAZARD DETECTED, STALL! \n ")
                    return(RAW)
                else:
                    RAW = 0
            elif(opcode == 3 or opcode == 4 or opcode == 14):   #these instructions read registers
                if(reg1_temp == reg1_prev):
                    RAW = 1
                    print(trace)
                    print("CLOCK = " + str(clock))
                    print("DATA HAZARD DETECTED, STALL! \n ")
                    return(RAW)
                else:
                    RAW = 0

#    clock += 1
    RAW = 0                                          # - operand fetch
    print(trace)
    print("CLOCK = " + str(clock) + "\n")

    if not (opcodes.has_key( opcode )):              # This checks
      tval, treg = trap(0)
      if (tval == -1):                              # illegal instruction
         return(-1)
    memdata = 0                                      #     contents of memory for loads
    if opcodes[ opcode ] [0] == 1:                   #     dec, inc, ret type
      operand1 = getregval( reg1 )                  #       fetch operands
    elif opcodes[ opcode ] [0] == 2:                 #     add, sub type
      operand1 = getregval( reg1 )                  #       fetch operands
      operand2 = getregval( reg2 )
    elif opcodes[ opcode ] [0] == 3:                 #     ld, st, br type
      operand1 = getregval( reg1 )                  #       fetch operands
      operand2 = addr
    elif opcodes[ opcode ] [0] == 0:                 #     ? type
      return(-1)

    if (opcode == 7):                                # get data from data memory for loads
      memdata = getdatamem( operand2 )

    if(opcode == 8):
        regdata = putdatamem(operand2)

def execute():
   global data_hazard, count_trace
   global ip, result, reg1, opcode, ic, clock, reg2, reg1_prev, reg2_prev, opcode_prev, first_time_execute
   global scoreboard, bnz_fetch_trace, branch_predictor_1_bit, loop_variable

   first_time_execute = 1


   if(reg1 > 7 ):
    reg1_prev = reg1 - 8
   else:
       reg1_prev = reg1
   if(reg2 > 7 ):
       reg2_prev = reg2 - 8
   else:
       reg2_prev = reg2

   opcode_prev = opcode

   if(opcode_prev == 9 or opcode_prev == 7 or opcode_prev == 1 or opcode_prev == 2 or opcode_prev == 13 or opcode_prev == 16):
       scoreboard[count_trace][reg1_prev] = "W"


   if(opcode_prev == 14 or opcode_prev == 1 or opcode_prev == 2):
       scoreboard[count_trace][reg2_prev] = "R"

   if(opcode_prev == 3 or opcode_prev == 4):
       scoreboard[count_trace][reg2_prev] = "RW"

   count_trace += 1

   trace()
   clock = clock + 1
   print("CLOCK = " + str(clock) + "\n")

   ic = ic + 1
   if opcode == 1:                     # add
    result = (operand1 + operand2) & nummask
    if ( checkres( operand1, operand2, result )):
     tval, treg = trap(1)
     if (tval == -1):                           # overflow
        return(-1)
   elif opcode == 2:                   # sub
      result = (operand1 - operand2) & nummask
      if ( checkres( operand1, operand2, result )):
         tval, treg = trap(1)
         if (tval == -1):                           # overflow
            return(-1)
   elif opcode == 3:                   # dec
      result = operand1 - 1
   elif opcode == 4:                   # inc
      result = operand1 + 1
   elif opcode == 7:                   # load
      result = memdata
   elif opcode == 8:
       result = regdata
   elif opcode == 9:                   # load immediate
      result = operand2
   elif opcode == 12:                  # conditional branch
      result = operand1
      if result <> 0:
         if(branch_predictor_1_bit == "NOT TAKEN"):
             branch_predictor_1_bit = "TAKEN"
             print("BRANCH PREDICTED : NOT TAKEN, ACTUAL BRANCH : TAKEN")
             print("PREDICTION IS INCORRECT. PIPELINE HAS TO BE FLUSHED. CONTROL HAZARD PENALTY\n")
             loop_variable = operand2
             bnz_fetch_trace = 1
             ip = operand2
             clock += 1
             fetch()
             bnz_fetch_trace = 0
             ip = ip - 1
             clock += 1
         elif(branch_predictor_1_bit == "TAKEN"):
             branch_predictor_1_bit = "TAKEN"
             print("BRANCH PREDICTED : TAKEN, ACTUAL BRANCH : TAKEN")
             print("PREDICTION IS CORRECT, NO CONTROL HAZARD PENALTY\n")
             ip = operand2 - 1
      else:
        if(branch_predictor_1_bit == "TAKEN"):
            branch_predictor_1_bit = "NOT TAKEN"
            print("BRANCH PREDICTED : TAKEN, ACTUAL BRANCH :NOT TAKEN")
            print("PREDICTION IS INCORRECT, WRONG INSTRUCTIONS FETCHED. PENALTY DUE TO IMPERFECT BRANCH PREDICTOR \n")
            clock += 1
            bnz_fetch_trace = 1
            fetch()
            bnz_fetch_trace = 0
            clock += 1
   elif opcode == 13:                  # branch and link
      result = ip
      ip = operand2 - 1
   elif opcode == 14:                   # return
      ip = operand1
   elif opcode == 16:                   # interrupt/sys call
      result = ip
      tval, treg = trap(reg1)
      if (tval == -1):
        return(-1)
      reg1 = treg
      ip = operand2
   # write back
   if ( (opcode == 1) | (opcode == 2 ) |
         (opcode == 3) | (opcode == 4 ) ):     # arithmetic
        reg[ reg1 ] = result
   elif ( (opcode == 7) | (opcode == 9 )):     # loads
        reg[ reg1 ] = result
   elif ((opcode == 8)):                       ### WRITE THROUGH ALLOCATE CACHE STRATEGY
        if(cache_type == 'U'):
            in_cache(ip)
            cache[line_number][replace_block][0] = result
        elif(cache_type == 'S'):
            in_cache_data(ip)
            cache[line_number][replace_block][0] = result
        mem[addr + reg[dataseg]] = result

   elif (opcode == 13):                        # store return address
        reg[ reg1 ] = result
   elif (opcode == 16):                        # store return address
        reg[ reg1 ] = result

count_trace = 0
data_hazard = 0



# while(1):
#     ip = input('enter ip:')
#     if(ip >= 0 and ip < 1023):
#         print('{0:09b}'.format(ip))
#         break
#     elif(ip > 1023):
#         print("Enter IP between 0 and 1023")

while(1):
    cache_width = input('Enter cache width(2-word or 4-word): ')
    if(cache_width != 2 and cache_width != 4):
        print("Enter either 2 or 4")
    else:
        break
while(1):
    cache_type = raw_input('Enter Cache Type(U for Unified, S for Split):')
    if(cache_type != 'U' and cache_type != 'S' and cache_type != 's' and cache_type != 'u'):
        print("Enter either U or S")
    else:
        if(cache_type == 'u'):
            cache_type = 'U'
        elif(cache_type == 's'):
            cache_type = 'S'
        break
while(1):
    cache_size = input('Enter size of cache(4 or 16 lines): ')
    if(cache_size != 4 and (cache_size != 16)):
        print("Enter either 4 or 16")
    else:
        break
        print("\n")

while(1):
    cache_associativity = raw_input('Enter associativity. "D" for Direct mapped and "4" for 4-way set associativity: ')
    if(cache_associativity != "D" and (cache_associativity != "4") and (cache_associativity != 'd')):
        print("Enter either D or 4")
    else:
        if(cache_associativity == 'd'):
            cache_associativity = 'D'

        if(cache_associativity == "D"):
            cache_associativity = 1
        break

if(cache_width == 4 and cache_size == 4 and cache_type == 'S' and cache_associativity == str(4)):
    print("With width = 4 and no. of lines = 4, the number of lines are already 1 for 4-way associativity. Can't go any lower by splitting Cache")
    cache_type = 'U'

if(cache_width == 2 and cache_type == 'S' and cache_associativity == str(4) and cache_size == 4):
     cache_type = 'U'
     print("With a Seperate Instruction and Data Cache, width = 2 and no. of lines = 4, the number of lines are already 1 for each seperate cache. Can't go any lower with set associativity")
     print("Implementing Unified Cache only.")
read_hit_cache = 0
read_miss_cache = 0

decode_cache()
create_cache()
# in_cache()
#
# ip = ip+1
# in_cache()

# for x in range (0,70):
#     in_cache(x)
#     ip = ip+1
#     print("read hit cache: " + str(read_hit_cache))
#     print("read miss cache: " + str(read_miss_cache))
#     print("line number: " + str(line_number))
#     print("set number: " + str(set_number))
#     print("LRU:")
#     pprint.pprint(LRU)
#     # pprint.pprint(valid)
#     print (" ")


# while(1):
#     pass
# in_cache()
ip = 0
fetch()

ip = ip + 1
fetch()

ip = 0
decode()

i = 0
j = 0
while( 1 ):
#-------------------------------------------------------------------------------#
    if(j != 1):
        i = execute()
        if(i == -1):
            break
        ip = ip + 1

    if(j == 1):
        clock += 1
        j = 0
    j = decode()
    if(j == -1):
        break
    if( j!= 1 ):
        ip = ip + 1

    if(j != 1):
        fetch()
        ip = ip - 1

#-------------------------------------------------------------------------------#

   # end of instruction loop
# end of execution

   
