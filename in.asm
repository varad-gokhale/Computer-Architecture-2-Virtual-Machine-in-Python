; sum an array
       go   0
0      ld   0 .count
.loop  dec  0
       bnz  0 .loop
       sys  1 16
       dw   0
.count dw   2
.val   dw   4
       dw   8