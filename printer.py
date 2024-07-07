from shutil import get_terminal_size

class Printer:
    @staticmethod
    def print_loader(channel, message):
        clear_line = "\r" + " " * get_terminal_size().columns + "\r"
        print(f"{clear_line}{message}", end='')