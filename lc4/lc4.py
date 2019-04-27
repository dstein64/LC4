import argparse
from enum import Enum, unique
import os
import random
import sys

import numpy as np

version_txt = os.path.join(os.path.dirname(__file__), 'version.txt')
with open(version_txt, 'r') as f:
    __version__ = f.read().strip()

_python_major_version = sys.version_info.major
if _python_major_version < 3:
    message = 'Unsupported version of Python: {}'.format(_python_major_version)
    raise RuntimeError(message)


# ************************************************************
# * Environment
# ************************************************************

# Enable ANSI terminal colors on Windows
if sys.platform == 'win32':
    import ctypes
    from ctypes import wintypes
    kernel32 = ctypes.windll.kernel32
    STD_OUTPUT_HANDLE = -11                  # https://docs.microsoft.com/en-us/windows/console/getstdhandle
    STD_ERROR_HANDLE = -12                   # ditto
    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x4 # https://docs.microsoft.com/en-us/windows/console/getconsolemode
    for std_device in [STD_OUTPUT_HANDLE, STD_ERROR_HANDLE]:
        handle = kernel32.GetStdHandle(wintypes.DWORD(std_device))
        old_console_mode = wintypes.DWORD()
        kernel32.GetConsoleMode(handle, ctypes.byref(old_console_mode))
        new_console_mode = wintypes.DWORD(ENABLE_VIRTUAL_TERMINAL_PROCESSING | old_console_mode.value)
        kernel32.SetConsoleMode(handle, new_console_mode)


# ************************************************************
# * Utils
# ************************************************************

def _isatty(stream):
    return hasattr(stream, 'isatty') and stream.isatty()


@unique
class _Color(Enum):
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6


def _colorize(string, color=None):
    string = str(string)
    color_lookup = {
        _Color.RED:     '\033[31m',
        _Color.GREEN:   '\033[32m',
        _Color.YELLOW:  '\033[33m',
        _Color.BLUE:    '\033[34m',
        _Color.MAGENTA: '\033[35m',
        _Color.CYAN:    '\033[36m',
    }
    end_color = '\033[0m'
    if color and color not in color_lookup:
        raise RuntimeError('Unavailable color: {}'.format(color))
    string = color_lookup[color] + string + end_color
    return string


class _Logger:
    def __init__(self, verbose, stream=None):
        self.verbose = verbose
        if stream is None:
            self.stream = sys.stdout
        else:
            self.stream = stream

    def log(self, string, end='\n'):
        if self.verbose:
            print(string, file=self.stream, end=end)


# ************************************************************
# * Core (private)
# ************************************************************

_DEFAULT_ALPHABET = '#_23456789abcdefghijklmnopqrstuvwxyz'


class _State:
    def __init__(self, S, i, j, r, y, pt, ct):
        self.S = S
        self.i = i
        self.j = j
        self.r = r
        self.y = y
        self.pt = pt
        self.ct = ct

    def stringify(self, alphabet, colorize=False):
        output = ''
        rows, cols = self.S.shape
        at_symbol = '@'
        if colorize:
            at_symbol = _colorize(at_symbol, _Color.RED)
        for i in range(rows):
            for j in range(cols):
                val = str(alphabet[self.S[i, j]])
                if colorize and (i == self.r or j == self.y):
                    val = _colorize(val, _Color.GREEN)
                output += val
                if (i, j) == (self.i, self.j):
                    output += at_symbol
                elif j < cols - 1:
                    output += ' '
                output += ' ' if j < cols - 1 else '\n'
        return output


class _LC4History(list):
    """LC4History is a list of _States"""
    def stringify(self, alphabet, colorize=False):
        output = ''
        for idx, state in enumerate(self):
            if idx > 0: output += '\n'
            step_val = str(idx)
            if colorize: step_val = _colorize(step_val, _Color.YELLOW)
            output += 'step: {}\n'.format(step_val)
            output += '----------------\n'
            output += state.stringify(alphabet, colorize=colorize)
            output += '----------------\n'
            if state.pt is not None and state.ct is not None:
                pt_val = alphabet[state.pt]
                if colorize: pt_val = _colorize(pt_val, _Color.MAGENTA)
                ct_val = alphabet[state.ct]
                if colorize: ct_val = _colorize(ct_val, _Color.MAGENTA)
                output += ' pt: {}    ct: {}\n'.format(pt_val, ct_val)
        return output


class _LC4Runner:
    def __init__(self, K):
        S = np.empty((6, 6), dtype=int)
        for k in range(36):
            S[divmod(k, 6)] = K[k]
        self.state = _State(S, 0, 0, None, None, None, None)
        self.history = _LC4History((self.state,))

    def _step(self, r, x, y, ct, pt):
        state = self.state
        S, i, j = state.S.copy(), state.i, state.j
        S[r, :] = np.roll(S[r, :], 1)
        y = (y + (x == r)) % 6
        j = (j + (i == r)) % 6
        S[:, y] = np.roll(S[:, y], 1)
        i = (i + (j == y)) % 6
        i = (i + ct // 6) % 6
        j = (j + ct % 6) % 6
        self.state = _State(S, i, j, r, y, pt, ct)
        self.history.append(self.state)

    def encrypt(self, P):
        n = P.shape[0]
        C = np.empty(n, dtype=int)
        for idx, pt in enumerate(P):
            S = self.state.S
            i = self.state.i
            j = self.state.j
            where = np.where(S == pt)
            r = where[0][0]
            c = where[1][0]
            x = (r + S[i, j] // 6) % 6
            y = (c + S[i, j] % 6) % 6
            ct = S[x, y]
            C[idx] = ct
            self._step(r, x, y, ct, pt)
        return C

    def decrypt(self, C):
        n = C.shape[0]
        P = np.empty(n, dtype=int)
        for idx, ct in enumerate(C):
            S = self.state.S
            i = self.state.i
            j = self.state.j
            where = np.where(S == ct)
            x = where[0][0]
            y = where[1][0]
            r = (x - S[i, j] // 6) % 6
            c = (y - S[i, j] % 6) % 6
            pt = S[r, c]
            P[idx] = pt
            self._step(r, x, y, ct, pt)
        return P


# ************************************************************
# * Core (public)
# ************************************************************

def encrypt(key, text, nonce='', alphabet=_DEFAULT_ALPHABET, verbose=False):
    logger = _Logger(verbose)
    colorize = _isatty(logger.stream)
    index_lookup = {c: idx for idx, c in enumerate(alphabet)}
    K = np.array([index_lookup[x] for x in key.lower()])
    logger.log('*'*30 + '\n* LC4 Encryption\n' + '*'*30 + '\n')
    lc4_runner = _LC4Runner(K)
    lc4_runner.encrypt(np.array([index_lookup[x] for x in nonce]))
    C = lc4_runner.encrypt(np.array([index_lookup[x] for x in text]))
    logger.log(lc4_runner.history.stringify(alphabet, colorize=colorize))
    encrypted = ''.join(alphabet[x] for x in C)
    logger.log('Encrypted: {}\n'.format(
        _colorize(encrypted, _Color.BLUE) if colorize else encrypted))
    return encrypted


def decrypt(key, text, nonce='', alphabet=_DEFAULT_ALPHABET, verbose=False):
    logger = _Logger(verbose)
    colorize = _isatty(logger.stream)
    index_lookup = {c: idx for idx, c in enumerate(alphabet)}
    K = np.array([index_lookup[x] for x in key.lower()])
    logger.log('*'*30 + '\n* LC4 Decryption\n' + '*'*30 + '\n')
    lc4_runner = _LC4Runner(K)
    lc4_runner.encrypt(np.array([index_lookup[x] for x in nonce]))
    P = lc4_runner.decrypt(np.array([index_lookup[x] for x in text]))
    logger.log(lc4_runner.history.stringify(alphabet, colorize=colorize))
    decrypted = ''.join(alphabet[x] for x in P)
    logger.log('Decrypted: {}\n'.format(
        _colorize(decrypted, _Color.BLUE) if colorize else decrypted))
    return decrypted


# ************************************************************
# * Interactive Command Line Interface
# ************************************************************

def _input_loop(prompt, strip=True, required=True):
    try:
        import readline
    except:
        pass
    while True:
        try:
            selection = input(prompt)
            if strip:
                selection = selection.strip()
        except EOFError:
            sys.exit(1)
        except KeyboardInterrupt:
            # With readline, stdin is flushed after a KeyboarInterrupt.
            # Otherwise, exit.
            if 'readline' not in sys.modules:
                sys.exit(1)
            print()
            continue
        if required and not selection:
            continue
        break
    return selection


def _parse_args(argv):
    def positive_int_arg_type(val):
        int_val = int(val)
        if int_val <= 0:
            raise argparse.ArgumentTypeError('invalid positive int value: \'{}\''.format(val))
        return int_val

    def alphabet_arg_type(val):
        if len(val) != 36:
            raise argparse.ArgumentTypeError('alphabet must have 36 characters')
        if len(val) != len(set(val)):
            raise argparse.ArgumentTypeError('characters in alphabet must be unique')
        return val

    parser = argparse.ArgumentParser(
        prog='lc4',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--version', action='version', version='lc4 {}'.format(__version__))
    parser.add_argument(
        '-a', '--alphabet',
        default=_DEFAULT_ALPHABET,
        type=alphabet_arg_type,
        metavar='STRING',
        help='A string of 36 characters representing the alphabet.'
    )
    parser.add_argument(
        '-n', '--nonce-length',
        default=6,
        type=positive_int_arg_type,
        metavar='INTEGER',
        help='The number of characters in randomly generated nonces when using option 2.'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enables status logging to stdout.'
    )
    args = parser.parse_args(argv[1:])
    return args


def main(argv=sys.argv):
    args = _parse_args(argv)
    def print_(message, color=None):
        if _isatty(sys.stdout): message = _colorize(message, color)
        print(message)
    error_color = _Color.RED
    output_color = _Color.GREEN

    while True:
        print('1. Generate Key')
        print('2. Generate Nonce')
        print('3. Encrypt')
        print('4. Decrypt')
        print('5. Quit')
        selection = _input_loop('>>> ')
        if selection == '1':
            print_(''.join(random.sample(args.alphabet, 36)), color=output_color)
        elif selection == '2':
            nonce_chars = []
            for _ in range(args.nonce_length):
                nonce_chars.extend(random.sample(args.alphabet, 1))
            print_(''.join(nonce_chars), color=output_color)
        elif selection in ('3', '4'):
            def validated_input(prompt, valid_chars):
                while True:
                    val = _input_loop(prompt)
                    diff = set(val) - valid_chars
                    if not diff:
                        return val
                    print_('Unsupported characters: {}'.format(''.join(diff)), color=error_color)

            valid_chars = set(args.alphabet)
            while True:
                key = validated_input('Key: ', valid_chars)
                valid_key = True
                if len(key) != len(args.alphabet):
                    valid_key = False
                    print_('Key must include exactly 36 characters.', color=error_color)
                missing_chars = set(args.alphabet) - set(key)
                if len(missing_chars) > 0:
                    valid_key = False
                    print_('Missing characters: {}'.format(''.join(missing_chars)), color=error_color)
                if valid_key:
                    break
            nonce = validated_input('Nonce: ', valid_chars)
            text = validated_input('Text: ', valid_chars)
            if selection == '3':
                print_(encrypt(key, text, nonce=nonce, verbose=args.verbose), color=output_color)
            else:
                print_(decrypt(key, text, nonce=nonce, verbose=args.verbose), color=output_color)
        elif selection == '5':
            pass
        else:
            print_('Invalid selection: {}'.format(selection), color=error_color)
            continue
        break

    return 0


if __name__ == '__main__':
    sys.exit(main())
