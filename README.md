# TwoPhaseLockingProtocol
This program simulates the behavior of the two-phase locking (2PL) protocol for concurrency control. 
The particular protocol to be implemented will be rigorous 2PL, with the wait die method for dealing with deadlock.
The input to the program is a file of transaction operations in a particular sequence given as "file.txt".

   Each line has a single transaction operation. The possible operations are: b (begin transaction), r (read item), w (write item), and e (end transaction). 
Each operation is followed by a transaction id that is an integer between 1 and 99. For r and w operations, an item name follows between parentheses (item names are single letters from A to Z). 
The output of the program is given in the file "output.txt".
