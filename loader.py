from itertools import cycle
from shutil import get_terminal_size
from threading import Thread
from time import sleep
from printer import Printer

class Loader:
    def __init__(self, chan, desc="Loading...", end='', timeout=0.1, mode='prog'):
        self.desc = desc
        self.end = end
        self.timeout = timeout
        self.channel = chan

        self._thread = Thread(target=self._animate, daemon=True)
        if mode == 'std1':
            self.steps = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
        elif mode == 'std2':
            self.steps = ["◜","◝","◞","◟"]
        elif mode == 'std3':
            self.steps = ["😐 ","😐 ","😮 ","😮 ","😦 ","😦 ","😧 ","😧 ","🤯 ","💥 ","✨ ","\u3000 ","\u3000 ","\u3000 "]
        elif mode == 'prog':
            self.steps = ["[∙∙∙]","[●∙∙]","[∙●∙]","[∙∙●]","[∙∙∙]"]

        self.done = False

    def start(self):
        self._thread = Thread(target=self._animate, daemon=True)
        self._thread.start()
        return self

    def _animate(self):
        for c in cycle(self.steps):
            if self.done:
                break
            Printer.print_loader(self.channel, f"\r\t{c} {self.desc} ")
            # print(f"\r{c} {self.desc}", end='', flush=True)
            sleep(self.timeout)

    def __enter__(self):
        self.start()
        return self

    def stop(self):
        self.done = True
        cols = get_terminal_size((80, 20)).columns
        Printer.print_loader(self.channel, "\r" + " " * cols)

        if self.end != "":
            Printer.print_loader(self.channel, f"\r{self.end}")

    def __exit__(self, exc_type, exc_value, tb):
        # handle exceptions with those variables ^
        self.stop()
