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
import os
from typing import List

NOP = 0
SAY_HELLO = 99


class CPU:
    CMD_REGISTER = {NOP: "_nop",
                    SAY_HELLO: "_say_hello"}

    def __init__(self):
        print('CPU is ready to use')

    def run_commands(self, commands: List):
        pc = 0
        commands = commands

        while pc < len(commands):
            current_cmd = commands[pc]  # read current command
            self.eval(cmd=current_cmd)  # evaluate/run command
            pc += 1

    def eval(self, cmd):
        if cmd not in self.CMD_REGISTER:
            raise AttributeError(f'Unknown command: {cmd}. Valid commands are {list(self.CMD_REGISTER.keys())}')

        method_name = self.CMD_REGISTER[cmd]
        getattr(self, method_name)()

    @staticmethod
    def _nop():
        # print('doing nothing')
        pass

    @staticmethod
    def _say_hello():
        user = os.getlogin()
        print(f'hello {user}')


if __name__ == '__main__':
    # initialize CPU
    cpu = CPU()

    # just doing nothing:
    print('-> doing nothing:')
    cmds = [NOP] * 100
    cpu.run_commands(commands=cmds)

    # say hello
    print('-> now saying hello:')
    cmds = [SAY_HELLO]
    cpu.run_commands(commands=cmds)

    # invalid command
    print('-> now invalid command after 5 saying hello for 5 times')
    cmds = [NOP] * 5
    cmds += [SAY_HELLO] * 5
    cmds += [-99]
    cpu.run_commands(commands=cmds)
