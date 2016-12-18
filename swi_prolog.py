import pexpect


def get_output(prolog, command):
    """
    :param prolog: prolog process
    :param command: command to execute
    :return: tuple (ret, result): ret = 'true.' or 'false.', result = prolog output with out 'true.'/'false.' in the end
    """
    expects = ['true.', 'false.']
    prolog.sendline(command + b'\n')
    try:
        ret = prolog.expect(expects, timeout=5)
        result = prolog.before.decode()
        # print(result)
        return expects[ret], result[result.rfind('.') + 3:result.rfind('\n') + 1].replace('\r\n', '\n')
    except pexpect.TIMEOUT:
        return -1, -1


def test(source, commands):
    """
    :param source: name of source prolog file
    :param commands: massive of commands in form [input, output]
    :return: tuple(output, debug): output is True or False, debug is massive with information about failed commands
    """
    prolog = pexpect.spawn('prolog ' + source)
    prolog.expect('.\r\n\r\n\?-')

    output = True
    debug = []
    for command in commands:
        ret, result = get_output(prolog, command[0].encode())

        if ret == -1:
            output = False
            debug.append('Command: ' + command[0] + '\nTimeout exception while executing command')
            break

        if command[1].find('true.') >= 0 or command[1].find('false.') >= 0:
            result += ret
        else:
            command[1] += '\n'

        if not result == command[1]:
            output = False
            debug.append('Command: ' + command[0] + '\nExpected result: ' + command[1] + '\nObtained result: ' + result)
            break

    prolog.kill(0)
    return output, debug

'''
file = open('cmds')
text = file.read()
data = text.split('***')

commands = []
for d in data:
    commands.append(d.split('>'))

output, debug = test('/home/enot/Desktop/AI2.pl', commands)
print(output)
print(debug)

prolog = pexpect.spawn('prolog /home/enot/Desktop/BOS2.pl')
prolog.expect('.\r\n\r\n\?-')

print(get_output(prolog, b'create_object(s1, o10, t2).'))
print(get_output(prolog, b'create_object(s1, o10, t2).'))
print(get_output(prolog, b'create_subject(s2, new_subject, t1).'))

prolog.kill(0)
'''
