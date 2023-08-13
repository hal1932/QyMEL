# coding: utf-8
from typing import *
import subprocess
import ctypes
import ctypes.wintypes
import msvcrt


_kernel32 = ctypes.windll.kernel32


class NonBlockingPipeReader(object):

    def __init__(self, pipe: IO) -> None:
        self.__handle = msvcrt.get_osfhandle(pipe.fileno())
        self.__stocked_lines = []  # type: List[str]
        self.__unstocked_str = ''  # type: str

    def read(self, size: int = MAXSIZE) -> bytes:
        available = ctypes.wintypes.DWORD()
        readable = _kernel32.PeekNamedPipe(self.__handle, None, 0, None, ctypes.byref(available), None)
        if not readable or available.value == 0:
            return b''

        if size == MAXSIZE:
            size = available.value

        buffer = ctypes.create_string_buffer(size)
        bytes_read = ctypes.wintypes.DWORD()
        success = _kernel32.ReadFile(self.__handle, buffer, size, ctypes.byref(bytes_read), None)
        if not success:
            return b''

        return buffer.value

    def readline(self, encoding: Optional[str] = None) -> str:
        if self.__stocked_lines:
            line = self.__stocked_lines.pop(0)
        else:
            buffer = self.read()

            if encoding is None:
                buffer = buffer.decode()
            else:
                buffer = buffer.decode(encoding)

            if len(buffer) == 0:
                return ''

            ends_with_newline = buffer.endswith('\n')
            lines = buffer.splitlines()

            line = self.__unstocked_str + lines[0]
            self.__unstocked_str = ''

            if len(lines) > 1:
                if ends_with_newline:
                    self.__stocked_lines = lines[1:]
                else:
                    self.__stocked_lines = lines[1:-1]
                    self.__unstocked_str = lines[-1]

        return line


if __name__ == '__main__':
    import cProfile
    import pstats

    SCRIPT = '''
import sys
for i in range(10000):
    # pipe = sys.stdout if i % 2 == 0 else sys.stderr
    pipe = sys.stdout
    pipe.write(str(pipe.__class__) + str(i) + \\"\\n\\")
    pipe.flush()
'''
    COMMAND = 'C:/Python27/python.exe -c "{}"'.format(SCRIPT)

    pr = cProfile.Profile()

    proc = subprocess.Popen(COMMAND, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    comm_outputs, comm_errors = proc.communicate()

    proc = subprocess.Popen(COMMAND, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout = NonBlockingPipeReader(proc.stdout)
    stderr = NonBlockingPipeReader(proc.stderr)

    outputs = []
    errors = []

    pr.enable()
    i = 0
    while proc.poll() is None:
        out = stdout.readline()
        if len(out) > 0:
            outputs.append(out)
            i += 1
    while True:
        err = stdout.readline()
        if len(err) > 0:
            errors.append(err)
            i += 1
        else:
            break
    pr.disable()

    ps = pstats.Stats(pr).sort_stats('cumulative')
    ps.print_stats()

    print(len(outputs))

    for got, expected in zip(outputs, comm_outputs.splitlines()):
        assert got == expected.decode()
    for got, expected in zip(errors, comm_errors.splitlines()):
        assert got == expected.decode()
