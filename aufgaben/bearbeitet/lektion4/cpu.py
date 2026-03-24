"""

Aus Lektion 1:
    Was ist eine virtuelle CPU:
    - imitiert physikalische CPU
    Was macht eine CPU für seine Benutzer:in?
    - Befehle ausführen, indem es die vereinfachten Befehle in CPU-Befehle umwandelt und ausführt. Z.B. lesen von Daten und sie an einem anderen Ort speichern
    Wie schreibe ich eine CPU in Python?
    - es braucht eine Speicherung von Befehlen (z.B. Array)
    - es braucht ein programm counter (PC), damit der CPU wes, wo er ist
    - Der CPU muss:
        - den aktuellen Befehl lesen
        - evaluieren, ob er den Befehl kennt (ob er im Registersatz ist)
        - den Befehl ausführen (wenn er ihn kennt)
        - mit dem nächsten Befehl weiter machen


Aufgabe Erweiterung:
das Programm soll in einem Loop laufen. Der Loop soll mittels eines JMP an den Anfang des Programmes implementiert sein.
es sollen zwei Instanzen von diesem Programm «gleichzeitig» laufen.
«Gleichzeitig» wird mittels «kooperativem Multitasking» implementiert.
D.h. die erste Program Instanz soll einen Sprung (JMP) in die zweite Program Instanz machen und die in die andere Instanz einen Sprung wieder in die erste.
"""
import getpass
from time import sleep
from typing import List

NOP = 'NOP'
JMP = 'JMP'
SAY_HELLO = 98
SAY_BYE = 99


class CPU:
    CMD_REGISTER = [NOP,
                    JMP,
                    SAY_HELLO,
                    SAY_BYE]

    def __init__(self, commands: List):
        self.mem = commands
        self.pc = 0
        self.op = NOP

    def run(self):
        while self.pc < len(self.mem):
            self.op = self.read()  # read current command
            self.eval()  # evaluate/run command

    def read(self) -> int:
        return self.mem[self.pc]

    def eval(self):
        op = self.op
        if op == NOP:
            self._nop()
        elif op == JMP:
            self._jump()
        elif op == SAY_HELLO:
            self._say_hello()
        elif op == SAY_BYE:
            self._say_bye()
        else:
            raise AttributeError(
                f'Unknown operation {self.op} at pc={self.pc}. Valid operations are {self.CMD_REGISTER}')

    def _nop(self):
        # print('doing nothing')
        self.pc += 1

    def _jump(self):
        """reads next command, interprets it as pointer to new command and sets pc accordingly"""
        # get target (read from the following cmd)
        if self.pc + 1 > len(self.mem):
            raise IndexError(f'JMP at pc={self.pc} has no target address')
        target = self.mem[self.pc + 1]

        # set pc accordingly
        if not (0 <= target < len(self.mem)):
            raise IndexError(f'Invalid jump target {target} at pc={self.pc}')
        self.pc = target

    def _say_hello(self):
        user = getpass.getuser()
        print(f'hello {user}')
        sleep(1.5)
        self.pc += 1

    def _say_bye(self):
        user = getpass.getuser()
        print(f'bye {user}')
        sleep(1.5)
        self.pc += 1


if __name__ == '__main__':
    # just doing nothing:
    print('-> doing nothing:')
    cmds = [NOP] * 100
    cpu = CPU(cmds)
    cpu.run()

    # say hello
    print('now jumping in infinite loop:')
    cmds = [
        NOP, NOP, SAY_HELLO, NOP, JMP, 10,
        255, NOP, SAY_HELLO, SAY_HELLO,  # should be skipped tue to jump
        NOP, NOP, NOP, NOP, SAY_BYE, JMP, 0,
        NOP, NOP, 255, NOP
    ]
    cpu = CPU(cmds)
    cpu.run()
