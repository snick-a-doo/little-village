;;; 
;;; Add two numbers
;;; 
        INP         ; Get the first number
        STA first   ; Store it
        INP         ; Get the second number
        ADD first   ; Add the first to it
        OUT         ; Give the result
        HLT
first   DAT         ; Storage for the first number
