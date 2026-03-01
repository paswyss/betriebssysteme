"""
Was ist eine virtuelle CPU:
- imitiert physikalische CPU
Was macht eine CPU für seine Benutzer:in?
- Befehle ausführen indem es die vereinfachten Befehle in CPU-Befehle umwandelt und ausführt. Z.B. lesen von Daten und sie an einem anderen Ort speichern
Wie schreibe ich eine CPU in Python?
- es braucht eine Speicherung von Befehlen (z.B. Array)
- es braucht ein programm counter (PC), damit der CPU weiss, wo er ist
- Der CPU muss:
    - den aktuellen Befehl lesen
    - evaluieren, ob er den Befehl kennt (ob er im Registersatz ist)
    - den Befehl ausführen (wenn er ihn kennt)
    - mit dem nächsten Befehl weiter machen
"""
import getpass
from typing import List

NOP = 0
SAY_HELLO = 99


class CPU:
    CMD_REGISTER = [NOP, SAY_HELLO]

    def __init__(self, commands: List):
        self.mem = commands
        self.pc = 0

    def run(self):
        while self.pc < len(self.mem):
            op_code = self.mem[self.pc]  # read current command
            self.eval(op_code=op_code)  # evaluate/run command
            self.pc += 1

    def eval(self, op_code):
        if op_code == NOP:
            self._nop()
        elif op_code == SAY_HELLO:
            self._say_hello()
        else:
            raise AttributeError(
                f'Unknown operation {op_code} at pc={self.pc}. Valid operations are {self.CMD_REGISTER}')

    @staticmethod
    def _nop():
        # print('doing nothing')
        pass

    @staticmethod
    def _say_hello():
        user = getpass.getuser()
        print(f'hello {user}')


if __name__ == '__main__':
    # just doing nothing:
    print('-> doing nothing:')
    cmds = [NOP] * 100
    cpu = CPU(cmds)
    cpu.run()

    # say hello
    print('-> now saying hello:')
    cmds = [SAY_HELLO]
    cpu = CPU(cmds)
    cpu.run()

    # invalid command
    print('-> now invalid command after saying hello 5 times')
    cmds = [NOP] * 5
    cmds += [SAY_HELLO] * 5
    cmds += [-99]
    cpu = CPU(cmds)
    cpu.run()
