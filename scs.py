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
#   Hex.   Addr. Inst.               Bin.
    0x80,  # 00  mov r0, #imm = 0   1000 0000
    0x90,  # 01  mov r1, #imm = 0   1001 0000
    0x81,  # 02  mov r0, #imm = 1   1000 0001
    0x92,  # 03  mov r1, #imm = 2   1001 0010
    0xA0,  # 04  mov r0, r1         1010 0000
    0x00,  # 05  jmp addr = 0       0000 0000
    0x00,
    0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

load_store_program = [
#   Hex.   Addr. Inst.               Bin.
    0x80,  # 00  mov r0, #imm = 0    1000 0000
    0x90,  # 01  mov r1, #imm = 0    1001 0000
    0xEE,  # 02  str r0, addr = E    1110 1110
    0x86,  # 03  mov r0, #imm = 6    1000 0110
    0xDD,  # 04  ldr r1, addr = D    1101 1101
    0x20,  # 05  add r0, r1          0010 0000
    0xEE,  # 06  str r0, addr = E    1110 1110
    0x00,  # 07  jmp addr = 0        0000 0000
    0x00, 0x00, 0x00, 0x00, 0x00, 0x05, 0x00, 0x00]

load_store_program2 = [
#   Hex.   Addr. Inst.              Bin.
    0xCF,  # 00  ldr r0, addr = F   1100 1111
    0x93,  # 01  mov r1, #imm = 3   1001 0011
    0x40,  # 02  sub r0, r1         0100 0000
    0x60,  # 03  mul r0, r1         0110 0000
    0x30,  # 04  add r0, r1         0011 0000
    0x50,  # 05  sub r0, r1         0101 0000
    0x10,  # 06  err                0001 0000
    0x00,  # 07  jmp addr = 0       0000 0000
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x07]

def undefined(address):
    print(f'Undefined instruction at address 0x{address:02X}')

if __name__ == "__main__":
    cpu = Cpu(load_store_program2, undefined)

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
