# Computer-Architecture-2-Virtual-Machine-in-Python
This is a Virtual Machine capable of running assembly code for a fictional computer called CAT series of microprocessors as part of Computer Architecture II class.

Features:
Capable of running ALU(add, sub, inc, dec etc.) and non-ALU instructions(LD, ST, PUSH, POP etc.)
3 Stage pipe-line
Scoreboarding for hazard-detection
Branch predictor to reduce stalls
Cache-support

note: Cache architecture can be chosen for optimization according to user-input
Choose among:
Width: Double Word/Quad Word
Unified/Split(Data + Instructions)
Associativity: Direct / 4-way
Size: 4 / 16 lines
