import sys
import termios
import fcntl
import os
from cpu import Cpu

def init_nonblocking_input():
    fd = sys.stdin.fileno()

    # Save original terminal settings
    original_termios = termios.tcgetattr(fd)
    new_termios = termios.tcgetattr(fd)

    # Turn off canonical mode and echo
    new_termios[3] &= ~(termios.ICANON | termios.ECHO)
    termios.tcsetattr(fd, termios.TCSANOW, new_termios)

    # Set stdin to non-blocking
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    return original_termios

def restore_input(original_termios):
    fd = sys.stdin.fileno()
    termios.tcsetattr(fd, termios.TCSANOW, original_termios)

def read_key():
    try:
        return sys.stdin.read(1)
    except IOError:
        return None
        

base_program = [
    0x80,
    0x90,
    0x81,
    0x92,
    0xA0,
    0x00,
    0x00,
    0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

# 1	    1	0001
# 2	    2	0010
# 3	    3	0011
# 4	    4	0100
# 5	    5	0101
# 6	    6	0110
# 7	    7	0111
# 8	    8	1000
# 9	    9	1001
# 10	A	1010
# 11	B	1011
# 12	C	1100
# 13	D	1101
# 14	E	1110
# 15	F	1111

load_store_program = [
    0x80,#1 - 1000 0000 - mov r0, #imm = 0
    0x90,#1 - 1001 0000 - mov r1, #imm = 0
    0xEE,#2 - 1110 1110 - str rn, addr = E -> 13
    0x86,#3 - 1000 0110 - mov r0, #imm = 6
    0xDD,#4
    0x20,#5
    0xEE,
    0x00,#6
    0x00, 0x00, 0x00, 0x00, 0x00, 0x05, 0x00, 0x00]

if __name__ == "__main__":
    cpu = Cpu(load_store_program)

    print("Press any key ('q' to quit, space for clock, d for debug dump)...")

    original_settings = init_nonblocking_input()
    try:
        while True:
            key = read_key()
            if key:
                # print(f"Key pressed: {repr(key)}") # uncomment to see what's pressed
                if key == 'q':
                    break
                if key == 'd':
                    cpu.debug_dump()
                if key == ' ':
                    cpu.next_cycle()
    finally:
        restore_input(original_settings)
        print("\nExit.")

