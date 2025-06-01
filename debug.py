import pexpect
import sys

child = pexpect.spawn("claude", encoding='utf-8', logfile=sys.stdout)
child.expect(pexpect.EOF)
