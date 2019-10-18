"""CPU functionality."""

import sys
import time

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0b0] * 256    # 256 bytes of Memory
        self.reg = [0b0] * 8      # 8 general-purpose registers

        # Interal registers
        self.pc = 0
        self.sp = 7
        self.fl = 0

        # _opcode_
        self._opcode_ = { 
            0b10000010: 'LDI',
            0b01000111: 'PRN',
            0b00000001: 'HLT',
            0b01000101: 'PSH',
            0b01000110: 'POP',

            # PC mutators
            0b01010000: 'CALL',
            0b00010001: 'RET',
            0b01010100: 'JMP',
            0b01010101: 'JEQ',
            0b01010110: 'JNE',

            # ALU ops
            0b10100000: 'ADD',
            0b10100001: 'SUB',
            0b10100010: 'MUL',
            0b10100011: 'DIV',
            0b10100100: 'MOD',
            0b01100101: 'INC',
            0b01100110: 'DEC',
            0b10100111: 'CMP',
        }

        # self._dispatch_op_ = {}

        # # ALU functions
        # self._dispatch_op_['MUL'] = self.alu('MUL', )

    def load(self):
        """Load a program into memory."""

        try:
            address = 0
            with open(sys.argv[1]) as f:
                for line in f:
                    # Process comments:
                    # Ignore anything after a # symbol
                    comment_split = line.split("#")
                    # Convert any numbers from binary strings to integers
                    num = comment_split[0].strip()
                    try:
                        x = int(num, 2)
                    except ValueError:
                        continue
                    # print in binary and decimal
                    self.ram[address] = x
                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            """
            Divide the value in the first register by the value in the second,
            storing the result in registerA.

            If the value in the second register is 0, the system should print an
            error message and halt.
            """
            pass
        elif op == "MOD":
            """
            Divide the value in the first register by the value in the second,
            storing the _remainder_ of the result in registerA.

            If the value in the second register is 0, the system should print an
            error message and halt.
            """
            pass
        elif op == "INC":
            self.reg[reg_a] += 1
        elif op == "DEC":
            self.reg[reg_a] -= 1
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
            else:
                self.fl = 0b00000000
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        
        running = True

        while running:
            command = self.ram[self.pc]

            if self._opcode_[command] == 'LDI':
                address = self.ram[self.pc + 1]
                value = self.ram[self.pc + 2]
                self.reg[address] = value
                self.pc += 3
            
            elif self._opcode_[command] == 'PRN':
                address = self.ram[self.pc + 1]
                print(self.reg[address])
                self.pc += 2

            elif self._opcode_[command] == 'HLT':
                running = False
            
            elif self._opcode_[command] == 'ADD':
                x = self.ram[self.pc + 1]
                y = self.ram[self.pc + 2]
                self.alu('ADD', x, y)
                self.pc += 3

            elif self._opcode_[command] == 'MUL':
                x = self.ram[self.pc + 1]
                y = self.ram[self.pc + 2]
                self.alu('MUL', x, y)
                self.pc += 3

            elif self._opcode_[command] == 'PSH':
                reg = self.ram[self.pc + 1]
                val = self.reg[reg]
                # Decrement the SP.
                self.reg[self.sp] -= 1
                # Copy the value in the given register to the address pointed to by SP.
                self.ram[self.reg[self.sp]] = val
                self.pc += 2

            elif self._opcode_[command] == 'POP':
                reg = self.ram[self.pc + 1]
                val = self.ram[self.reg[self.sp]]
                # Copy the value from the address pointed to by SP to the given register.
                self.reg[reg] = val
                # Increment self.sp.
                self.reg[self.sp] += 1
                self.pc += 2

            elif self._opcode_[command] == 'CALL':
                self.reg[self.sp] -= 1
                self.ram[self.reg[self.sp]] = self.pc + 2

                reg = self.ram[self.pc + 1]
                self.pc = self.reg[reg]

            elif self._opcode_[command] == 'RET':
                self.pc = self.ram[self.reg[self.sp]]
                self.reg[self.sp] += 1

            elif self._opcode_[command] == 'JMP':
                address = self.ram[self.pc + 1]
                self.pc = self.reg[address]

            elif self._opcode_[command] == 'JEQ':
                if self.fl == 0b00000001:
                    address = self.ram[self.pc + 1]
                    self.pc = self.reg[address]
                else:
                    self.pc += 2

            elif self._opcode_[command] == 'JNE':
                if self.fl == 0b00000000:
                    address = self.ram[self.pc + 1]
                    self.pc = self.reg[address]
                else:
                    self.pc += 2

            elif self._opcode_[command] == 'CMP':
                x = self.ram[self.pc + 1]
                y = self.ram[self.pc + 2]
                self.alu('CMP', x, y)
                self.pc += 3

            else:
                print(f"Unknown instruction: {command}")
                sys.exit(1)


        pass

    """
    Ram helper functions

    MAR = _Memory Address Register_ -> Address to store to
    MDR = _Memory Data Register_    -> Data to read or write
    """
    def ram_read(self, MAR):
        """ 
        Accepts the address to read and return the value stored
        there.
        """
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        """
        Accepts a value to write, and the address to write it to
        """
        self.ram[MAR] = MDR
        pass
