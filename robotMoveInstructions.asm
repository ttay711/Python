//SETUP MEMORY ADDRESSES
//0x3A = W_ONLY Command
//0x3B = R_ONLY Sensor 1
//0x3C = R_ONLY Sensor 2
//0x3D = R_ONLY Sensor 3
xor      R3, R3	
addi     R3, 0xff
LSH      R3, R3
LSH      R3, R3
SUBI     R3, 0x2	//SUBI R8 by 2 to 0xFFFA (This will be truncated to 0x3FA when used with LOAD)

//SETUP JUMP REGISTER FOR POLL
//  should always jump to the instruction AFTER the polling loop
//  remember that immediate jumps add 2 extra instructions
xor      R4, R4
addi     R4, 0xF	//We can always jump to r4 to go back to the polling loop

//SETUP REGISTERS FOR SENSOR DATA COMPARISON
// 0x52 = 8CM
// 0x64 = 10CM
XOR      R5, R5		
ADDI     R5, 0x32
ADDI     R5, 0x20	//set r5 to 0x52 to mark 8 cm as max wall distance
XOR      R6, R6
ADDI     R6, 0x32
ADDI     R6, 0x32	//set r6 to 0x64 to mark 10 cm as max wall distance
XOR      R7, R7
ADDI     R7, 0x12	//address just after poll loop

//POLL FOR SENSOR DATA
POLL:
PRB     			//Poll for data from robot
JE       R7			//begin calculations if data is ready
JUMP     R6

//LOAD SENSOR DATA FROM MEMORY
ADDI     R3, 1		//
LOAD     R0, R3		//
ADDI     R3, 1		//
LOAD     R1, R3		//
ADDI     R3, 1		//
LOAD     R2, R3		//
SUBI     R3, 3		// put address back to CMD address

//COMPARE SENSOR DATA
XOR      R8, R8
ADD      R8, R4
ADDI     R8, 0x33
CMP      R0, R6		//Check if front sensor is too close
JL       R8

SUBI     R8, 0xA	//if it is not, check if left sensor is too close
CMP      R1, R5	
JL       R8

ADDI     R8, 0x5	//if neither are, check if the right sensor is too close
CMP      R2, R5	
JL       R8

XOR      R11, R11	//Go forward if all sensors are good
ADDI     R11, 0x1
STOR     R11, R3
CMD
JUMP     R4

XOR      R11, R11	//If the left sensor is too close, correct left
ADDI     R11, 0x6
STOR     R11, R3
CMD
JUMP     R4

XOR      R11, R11	//If the right sensor is too close, correct left
ADDI     R11, 0x5
STOR     R11, R3
CMD
JUMP     R4

XOR      R11, R11	//If the front sensor is too close, figure out where to turn
XOR      R8, R8
ADDI     R8, 0x3C
CMP      R1, R2
JG       R8

ADDI     R11, 0x3	//Turn right if Right sensor has farther or the same distance
STOR     R11, R3
CMD
JUMP     R4

ADDI     R11, 0x4	//Turn left if Left Sensor has farther distance
STOR     R11, R3
CMD
JUMP     R4

STOP