# CR16A assmbler for CS3710
# Author: Trenton Taylor

# Team:
# Brian Hatasaka
# Sean Eastland
# Zane Yarbrough
# Trenton Taylor


### Notes: 
	# Reserved Registers
	# R15 	Stack pointer
	# R14 	Retrun address from jump instruction
	# R13 	Return value
	# R12 	Jump value (we no have immediate jumps so we do this way)
	# R2 	Sensor data
	# R1 	Sensor data
	# R0 	Sensor data

	# No jump immediate instruction is implemented so jump address needs to explicitly
	# be placed into R12 to preform a jump.

###


# TODO
	# add lshi
	# add rshi
	# add stori
#

# Python RE library
import re, sys, getopt

# REs for a CR16A instructions #
iRE = re.compile(r'^\s*([a-zA-Z]{2,6})\s+([R|r][0-9]{1,2}),\s+([R|r]?-?[0-9]+|0?x?[0-9a-fA-F]+)\s*(#|\/\/)?(?(4).*)$')
branchRE = re.compile(r'^\s*(jump|jl|jg|je|JUMP|JL|JG|JE)\s+([r|R][0-9]+|[\S]+)\s*(#|\/\/)?.*$')
retRE = re.compile(r'^\s*(ret|RET)\s+([R|r][0-9]{1,2})\s*(#|\/\/)?.*$')
labelRE = re.compile(r'^\s*([\S]+)(:)\s*(#|\/\/)?.*$')
regRE = re.compile(r'^[r|R][0-9]{1,2}$')
bleRE = re.compile(r'^\s*(stop|STOP|prb|PRB|cmd|CMD)\s*(#|\/\/)?.*$')


#	@brief Takes the name of the instruction and converts it into its binary form
#		   and populates the instruction bit fields of the opcode appropriately.
#		   Instructions that use immediate values do not use the lower instruction
#		   bit field in the opcode; instr2 will be populated with "-1" to indicate
#		   that an instruction using an immediate value was encountered so that the 
#		   fields can set correctly later. The opcode is organized as follows:
#				---------------------------------
#				| instr1 | Rdst | instr2 | Rsrc |
#		   		---------------------------------
#
#	@param instr: the instruction name to be converted to binary bit fields.
#		   opcode: size 4 array that holds all fields of the opcode. 
#		  		   DO NOT MODIFIY OTHER FIELDS.
#
#	@return Opcode with updated instruction fields. 
#
def translate_opcode(instr, opcode):

	if instr[len(str(instr)) - 1] == "I" or instr[len(str(instr)) - 1] == "i":
		opcode[2] = "-1"
		if instr == "ADDI" or instr == "addi":
			opcode[0] = "0101"
		elif instr == "ADDCI" or instr == "addci":
			opcode[0] = "0111"
		elif instr == "ADDCUI" or instr == "addcui":
			opcode[0] = "1101"
		elif instr == "SUBI" or instr == "subi":
			opcode[0] = "1001"
		elif instr == "CMPI" or instr == "cmpi":
			opcode[0] = "1011"
		elif instr == "CMPUI" or instr == "cmpui":
			opcode[0] = "1111"
		else:
			opcode[0] = "INVALID"
			opcode[2] = "INSTRUCTION"
			print("Invalid immediate instruction: %s" % instr)
	elif instr == "WAIT" or instr == "wait":
		opcode[0] = "0000"
		opcode[2] = "0000"
	elif instr == "AND" or instr == "and":
		opcode[0] = "0000"
		opcode[2] = "0001"
	elif instr == "OR" or instr == "or":
		opcode[0] = "0000"
		opcode[2] = "0010"
	elif instr == "XOR" or instr == "xor":
		opcode[0] = "0000"
		opcode[2] = "0011"
	elif instr == "NOT" or instr == "not":
		opcode[0] = "0000"
		opcode[2] = "0100"
	elif instr == "ADD" or instr == "add":
		opcode[0] = "0000"
		opcode[2] = "0101"
	elif instr == "ADDU" or instr == "addu":
		opcode[0] = "0000"
		opcode[2] = "0110"
	elif instr == "ADDC" or instr == "addc":
		opcode[0] = "0000"
		opcode[2] = "0111"
	elif instr == "SUB" or instr == "sub":
		opcode[0] = "0000"
		opcode[2] = "1001"
	elif instr == "CMP" or instr == "cmp":
		opcode[0] = "0000"
		opcode[2] = "1011"
	elif instr == "LOAD" or instr == "load":
		opcode[0] = "0100"
		opcode[2] = "0000"
	elif instr == "STOR" or instr == "stor":
		opcode[0] = "0100"
		opcode[2] = "0100"
	elif instr == "LSH" or instr == "lsh": # Just shifts by 1 and ignores Src reg
		opcode[0] = "1000"
		opcode[2] = "0101"
	elif instr == "RSH" or instr == "rsh": # Just shifts by 1 and ignores Src reg
		opcode[0] = "1000"
		opcode[2] = "1100"
	else:
		opcode[0] = "INVALID"
		opcode[2] = "INSTRUCTION"
		print("Invalid instruction: %s" % instr)

	return opcode


#	@brief Populates the register bit fields or immediate value bit fields. Opcode
#		   is organized as follows:
#		   	---------------------------------
#			| instr1 | Rdst | instr2 | Rsrc |
#		   	---------------------------------
#		  The instr bit fields are modified by another function unless the 
#		  instruction uses an immediate value in which the second instr field 
#		  and the Rsrc fields will both be used as the immediate value. 
#		  Otherwise the instr fields will be left alone. 
#
#	@param reg: register name retrived from regex (could be an immediate value)
#		   field: indicates which register bit field to populate, the 
#				  destination or source bit field in the opcode.
#		   opcode: size 4 array that holds all fields of the opcode. 
#		  		   DO NOT MODIFIY OTHER FIELDS.
#
#	@return Opcode with updated registor field.  
#
def translate_reg(reg, field, opcode):
	
	if reg == "R0" or reg == "r0":
		opcode[field] = ("0000")
	elif reg == "R1" or reg == "r1":
		opcode[field] = ("0001")
	elif reg == "R2" or reg == "r2":
		opcode[field] = ("0010")
	elif reg == "R3" or reg == "r3":
		opcode[field] = ("0011")
	elif reg == "R4" or reg == "r4":
		opcode[field] = ("0100")
	elif reg == "R5" or reg == "r5":
		opcode[field] = ("0101")
	elif reg == "R6" or reg == "r6":
		opcode[field] = ("0110")
	elif reg == "R7" or reg == "r7":
		opcode[field] = ("0111")
	elif reg == "R8" or reg == "r8":
		opcode[field] = ("1000")
	elif reg == "R9" or reg == "r9":
		opcode[field] = ("1001")
	elif reg == "R10" or reg == "r10":
		opcode[field] = ("1010")
	elif reg == "R11" or reg == "r11":
		opcode[field]= ("1011")
	elif reg == "R12" or reg == "r12":
		opcode[field] = ("1100")
	elif reg == "R13" or reg == "r13":
		opcode[field] = ("1101")
	elif reg == "R14" or reg == "r14":
		opcode[field] = ("1110")
	elif reg == "R15" or reg == "r15":
		opcode[field] = ("1111") 
	else:
		print("register error: %s" % reg)

	return opcode


#	@brief Scan through file and store all labels into a dictionary with the address of
#		   the next instuction. Labels are found using the Regex labelRE.
#
#	@param fname: file name.
#		   labels: dictionary to store the labels and associated addresses.
#
#	@return 
#
def find_labels(fname, labels):
	lncount = 0

	with open(fname, "r") as fl_in:
		for lines in fl_in:
			if lines.rstrip():
				if not lines.startswith("#") and not lines.startswith("//"):
					if labelRE.match(lines):
						# Store label in dictionary with corresponding line number.
						# Label address is the same address as the instructions that 
						#	immidieately follows the label.
						li = labelRE.search(lines)
						#lncount += 1
						labels[li.group(1)] = lncount
					elif bleRE.match(lines):
						# Match BLE instructions
						lncount += 1
					elif branchRE.match(lines):
						# Increment line count by 3 to account for insertion of extra
						# instructions to do the jump.
						lncount += 3
					elif retRE.match(lines):
						# Match Return instruction
						lncount += 1
					elif iRE.match(lines):
						# Match any other valid instruction
						lncount += 1
					else:
						# Invalid instruction
						print("Invalid instruction encountered near line: %d" % lncount)
						print(lines)
						break
	#print(labels)


#	@brief Convert an integer into binary.
#
#	@param n: number to convert
#		   bits: number of bits to represent n
#
#	@return binary string
#
def bin_digits(n, bits):
    s = bin(n & int("1"*bits, 2))[2:]
    return ("{0:0>%s}" % (bits)).format(s)


#	@brief Takes a sigle assembly instruction and converts it into a machine
#		   instruction by setting all fields of an opcode.
#
#	@param ai: a single CR16A assembly instruction
#
#	@return Updated opcode with all fields populated approprietly.
#
def assembly_to_machine(ai):	
	opcode = [None] * 4

	# set instruction bit fields.
	translate_opcode(ai.group(1), opcode)

	# set destination register bit field.
	translate_reg(ai.group(2), 1, opcode)

	# check if instruction uses immediate value and set src and lower instruction
	# bit fields appropriatly.
	if opcode[2] != "-1":
		translate_reg(ai.group(3), 3, opcode)
	else:
		tmp_bin = bin_digits((int(eval(ai.group(3)))), 8)
		opcode[2] = tmp_bin[0:4]
		opcode[3] = tmp_bin[4:8]

	return opcode


#	@brief Application that reads in an ASM file and converts all instructions into
#		   CR16A machine instructions that can be executed by the processor we
#		   designed using the DE1-SoC FPGA for the course CS3710.
#
#	@param N/A
#
#	@return N/A
#
def main(argv):

	labels = {}			# Dictionary to store labels and associated line number.
	foundLabelJump = False	# Flag to know if a jump instruction used a label.
	foundJump = False	# Flag to know if a jump instruction was encountered.
	arg_label = [None] * 2	# Store the immediate value for the extra addi for jump.
	arg_reg = [None]	# Store the register for the extra add for jump.
	jump_type = [None]  # Store jump type to store corret opcode before writing to file.
	skip_label = False

	print("Start assembler...")

	# Get all labels and store them with their associated line numbers to
	# replace them in jump instructions.
	fname = "./instructions.asm"

	find_labels(fname, labels)
	#print(labels)

	# Open asm file and convert it to binary opcodes and write it to an output file
	with open(fname, "r") as f_in:
		with open("output.txt", "w") as f_out:
			for lines in f_in:
				if lines.rstrip():
					# Remove comments for the executable file
					if not lines.startswith("#") and not lines.startswith("//"):

						# Convert ALU opcodes to binary
						if iRE.match(lines):
							ai = iRE.search(lines)
							op = assembly_to_machine(ai)
							#print(op)
						elif retRE.match(lines):
							# RET instruction must use R14 as Dest Reg
							# and has no Src Reg.
							ri = retRE.search(lines)
							op = [None] * 4
							op[0] = "1100"
							op[1] = "1110"
							op[2] = "1111"
							op[3] = "0000"
							#print(op)
						elif branchRE.match(lines):
							# Jump instructions can only use r12 at the processor level
							# so we need to add extra instructions.
							foundLabelJump = True
							bi = branchRE.search(lines)

							# Get opcode for the specific jump type
							if bi.group(1) == "jump" or bi.group(1) == "JUMP":
								jump_type = "0000"
							elif bi.group(1) == "jl" or bi.group(1) == "JL":
								jump_type = "0010"
							elif bi.group(1) == "jg" or bi.group(1) == "JG":
								jump_type = "0001"
							elif bi.group(1) == "je" or bi.group(1) == "JE":
								jump_type = "0011"
							else:
								jump_type = "error"

							# Check what the jump argument is: a label or a register.
							if regRE.match(bi.group(2)):
								foundLabelJump = False
								translate_reg(bi.group(2), 0, arg_reg)
								op = [None] * 4
								op[0] = "1100"
								op[1] = arg_reg[0]
								op[2] = jump_type
								op[3] = "0000"
								#print(arg_reg)
								#print(op)
							else:
								foundLabelJump = True
								address = labels[bi.group(2)]
								arg_label[0] = '{0:08b}'.format(int(address))[0:4]
								arg_label[1] = '{0:08b}'.format(int(address))[4:8]
								#print(arg_label)
						elif bleRE.match(lines):
							# BLE instructions
							blei = bleRE.search(lines)
							op = [None] * 4
							if blei.group(1) == "CMD" or blei.group(1) == "cmd": 
								op[0] = "0100"
								op[1] = "0000"
								op[2] = "0111"
								op[3] = "0000"
							elif blei.group(1) == "PRB" or blei.group(1) == "prb": 
								op[0] = "0100"
								op[1] = "0000"
								op[2] = "0011"
								op[3] = "0000"
							elif blei.group(1) == "STOP" or blei.group(1) == "stop": 
								op[0] = "0000"
								op[1] = "0000"
								op[2] = "1111"
								op[3] = "0000"
							#print(op)
						elif labelRE.match(lines):
							# Dont add Labels to the output file.
							skip_label = True
							
							# For Debug
							#li = labelRE.search(lines)
							#address = labels[li.group(1)]
							#op = [None] * 4
							#op[0] = '{0:016b}'.format(int(address))[0:4]
							#op[1] = '{0:016b}'.format(int(address))[4:8]
							#op[2] = '{0:016b}'.format(int(address))[8:12]
							#op[3] = '{0:016b}'.format(int(address))[12:16]
							#print(op)
						else:
							print("No matching RE for the following expression:")
							print(lines)

						# If jump instruction was encountered then replace it with these
						# instructions in order to preform the jump:
						#	xor r12, r12 to clear the jump register
						#	add r12, r? OR addi r12, NUM // depending on jump argument
						#	jump r12
						if foundLabelJump:
							foundLabelJump = False
							extra_op = [None] * 4

							# xor r12, r12
							extra_op[0] = "0000"
							extra_op[1] = "1100"
							extra_op[2] = "0011"
							extra_op[3] = "1100"
							for i in extra_op:
								f_out.write("%s" % i)
							f_out.write("\n")

							# Add an "addi" instruction if a label was used for the jump
							# addi r12, NUM
							extra_op[0] = "0101"
							extra_op[1] = "1100"
							extra_op[2] = arg_label[0]
							extra_op[3] = arg_label[1] 
							for i in extra_op:
								f_out.write("%s" % i)
							f_out.write("\n")

							# jump r12
							extra_op[0] = "1100"
							extra_op[1] = "1100"
							extra_op[2] = jump_type
							extra_op[3] = "0000"
							for i in extra_op:
								f_out.write("%s" % i)
							f_out.write("\n")
						elif skip_label:
							# Dont add the label to the output file.
							skip_label = False
						else:
							# Write the binary opcode to the output file.
							for item in op:
								f_out.write("%s" % item)

							# replacing '#' with '//' for the asm
							lines = lines.replace("#","//")
							# writing the asm as a comment (writing up until the newline)
							f_out.write("\t//%s" % lines[0:len(lines)-1])
							f_out.write("\n")

	print("Assembler finished.")

# Start assembler
main(sys.argv)