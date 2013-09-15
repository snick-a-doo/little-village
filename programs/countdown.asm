;;;
;;; Take a user input and count down to zero.  From Wikipedia
;;; 
     INP
LOOP SUB ONE     ; Label this memory address as LOOP.  Subtract 1 from the accumulator.
     OUT      
     BRZ QUIT    ; If the accumulator value is not 0, jump to LOOP.
     BRA LOOP
QUIT HLT         ; Label this memory address as QUIT.
ONE  DAT 1       ; Store the value 1 in this memory address and label it.
