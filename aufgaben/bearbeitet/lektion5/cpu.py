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

Aus Lektion 4:
    Aufgabe Erweiterung:
    das Programm soll in einem Loop laufen. Der Loop soll mittels eines JMP an den Anfang des Programmes implementiert sein.
    es sollen zwei Instanzen von diesem Programm «gleichzeitig» laufen.
    «Gleichzeitig» wird mittels «kooperativem Multitasking» implementiert.
    D.h. die erste Program Instanz soll einen Sprung (JMP) in die zweite Program Instanz machen und die in die andere Instanz einen Sprung wieder in die erste.

Aufgabe Erweiterung:
Interrupt Handling in der Python CPU implementieren:
- Sprung in einen Interrupt Handler, der in Assembler geschrieben ist
- Abspeichern des CPU Zustands
- Rücksprung aus dem Interrupt Handler in einen Kontext, d.h. Wiederherstellung des CPU Zustands (in Zukunft sagt der Scheduler der CPU, welcher Kontext wiederhergestellt werden soll)
"""
import getpass
from threading import Thread, Lock
from time import sleep
from typing import List

NOP = 'NOP'
JMP = 'JMP'
IRET = 'IRET'
SAY_HELLO = 98
SAY_BYE = 99

MEMORY = [
    # programm 1
    NOP, NOP, SAY_HELLO, NOP, JMP, 10,
    255, NOP, SAY_HELLO, SAY_HELLO,  # should be skipped tue to jump
    # programm 2
    NOP, NOP, NOP, NOP, SAY_BYE, JMP, 0, NOP, NOP, 255,
    # ISR1
    NOP, NOP, NOP, NOP, IRET, None, None, None, None, None,
    # ISR2
    NOP, NOP, NOP, NOP, NOP, NOP, NOP, NOP, IRET, None,
    # ISR3
    NOP, NOP, NOP, NOP, NOP, NOP, NOP, NOP, NOP, NOP, IRET
]


class CPU:
    CMD_REGISTER = [NOP,
                    JMP,
                    IRET,
                    SAY_HELLO,
                    SAY_BYE]

    IVT = {1: 20,
           2: 30,
           3: 40}

    def __init__(self, memory: List):
        self.mem = memory
        self.op = NOP

        # contexts (=programms) for future scheduling
        self.contexts = {
            'A': {'pc': 0}
        }
        self.current_context = 'A'

        # interrupt
        self.interrupt_lock = Lock()
        self.pending_irq = []
        self.current_irq = 0  # 0 = passive-level; Normale Threadausführung
        self.context_stack = []

    @property
    def pc(self):
        return self.contexts[self.current_context]["pc"]

    @pc.setter
    def pc(self, value):
        self.contexts[self.current_context]["pc"] = value

    def run(self):
        while self.pc < len(self.mem):
            self.op = self.read()  # read current command
            self.eval()  # evaluate/run command
            self._check_interrupt()  # check for interrupts

    def read(self) -> int:
        return self.mem[self.pc]

    def eval(self):
        op = self.op
        if op == NOP:
            self._nop()
        elif op == JMP:
            self._jump()
        elif op == IRET:
            self._iret()
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
        sleep(0.1)
        self.pc += 1

    def _say_bye(self):
        user = getpass.getuser()
        print(f'bye {user}')
        sleep(0.1)
        self.pc += 1

    def interrupt(self, code):
        with self.interrupt_lock:
            self.pending_irq.append(code)
            self.pending_irq.sort(reverse=True)  # highest priority first

    def _check_interrupt(self):
        with self.interrupt_lock:
            if not self.pending_irq:
                return

            # only interrupt when new interrupt has higher priority
            if self.current_irq >= self.pending_irq[0]:
                return

            irq = self.pending_irq.pop(0)
        self._enter_interrupt(irq)

    def _enter_interrupt(self, irq: int):
        if irq not in self.IVT:
            raise ValueError(f'Unknown interrupt {irq}')
        # print(f'--- enter IRQ: {irq}')
        # sleep(irq / 4) # keep high prio interrupts 'alive' (for demonstration only)

        # save current context (incl. pc)
        self.context_stack.append({'context': self.current_context,
                                   'pc': self.pc,
                                   'current_irq': self.current_irq
                                   })

        # set current irq
        # self.current_context = f'IRQ-{irq}'
        self.current_irq = irq
        self.pc = self.IVT[irq]  # lookup context handler in IVT -> set pc accordingly

    def _iret(self):
        if len(self.context_stack) < 1:
            raise RuntimeError("IRET ohne Kontext")

        context = self.context_stack.pop(-1)

        # self.current_context = context["context"]
        self.current_context = context['context']
        self.current_irq = context['current_irq']
        self.pc = context["pc"]

        # if self.current_irq > 0:
        #     print(f'switched back to IRQ-{self.current_irq}')
        # else:
        #     if len(self.pending_irq) > 0:
        #         print(f'still  {len(self.pending_irq)} interrupts in queue')
        #     else:
        #         print(f'switched back to context {self.current_context}')


if __name__ == '__main__':
    # initialize CPU
    cpu = CPU(memory=MEMORY)

    # start CPU as thread
    cpu_thread = Thread(target=cpu.run)
    cpu_thread.start()


    # start interrupts
    def interrupt(irq, freq: float):
        sleep(1.5 + 0.5 * irq)
        while True:
            cpu.interrupt(irq)
            sleep(freq)


    interrupt1 = Thread(target=interrupt, kwargs={'irq': 1, 'freq': 1})
    interrupt2 = Thread(target=interrupt, kwargs={'irq': 2, 'freq': 2})
    interrupt3 = Thread(target=interrupt, kwargs={'irq': 3, 'freq': 3})
    interrupt1.start()
    interrupt2.start()
    interrupt3.start()
