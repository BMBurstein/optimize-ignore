from __future__ import annotations

import itertools
import random
import re

def randChar():
    return random.choice('qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890._-')

def randString(len = 10, avoid = ''):
    s = []
    for _ in range(len):
        s.append(randChar())
        while s[-1] in avoid:
            s[-1] = randChar()
    return ''.join(s)
        
class RuleError(Exception):
    def __init__(self, reason):
        self.reason = reason
    
    def __str__(self):
        return self.reason

class Rule:
    def __init__(self, rule:str):
        self.rule = rule
        self.isDir = rule.endswith('/')
        self.isRooted = rule.find('/', 0, -1) >= 0
        # self.isWild = '*' in rule
        self.makeRe()

    def __str__(self):
        return self.rule

    def makeRe(self):
        rooted = self.isRooted
        isdir = self.isDir
        rule = self.rule
        if rule[0] == '/':
            rule = rule[1:]
        if rule[:3] == '**/':
            rooted = False
            rule = rule[3:]
        if rule[-3:] == '/**':
            isdir = True
            rule = rule[:-2]
        rule = rule.replace('/**', '\0')
        if rule[-1] == '/':
            rule = rule[:-1]
        escape = False
        build = []
        if not rooted:
            build.append('(.*/|)')
        for c in rule:
            if escape or c in '.+}{()|^$':
                build.append('\\')
                build.append(c)
                escape = False
            elif c == '\\':
                escape = True
            elif c == '*':
                build.append('[^/]*')
            elif c == '\0':
                build.append('(/.+|)')
            elif c == '?':
                build.append('[^/]')
            elif c in '[]!':
                raise RuleError("'{}' is not supported".format(c))
            else:
                build.append(c)
        if isdir:
            build.append('/.*')
        else:
            build.append('(/.*|)')
        self.re = re.compile(''.join(build))
        
        self.dummys = []
        if not rooted:
            rule = '\0' + rule
        tempDirs = '/' + '/'.join([randString() for _ in range(5)])
        temp = randString()
        dummy = rule.replace('\0', tempDirs + '/').replace('*', temp).replace('?', randChar())
        self.dummys.append(dummy)
        dummy = rule.replace('\0', '/').replace('*', randString(avoid=temp)).replace('?', randChar()) + tempDirs
        self.dummys.append(dummy)

    
    def contains(self, other:Rule):
        return all(self.re.fullmatch(d) for d in other.dummys)


def analyze(f):
    rules = []
    for i, line in enumerate(f, 1):
        line = line.strip()
        try:
            rule = Rule(line)
            rules.append((i, rule))
        except RuleError as e:
            raise RuntimeError("Could not process rule at line {}: {}\n{}\n".format(i, line, e))
    ret = []
    for r1,r2 in itertools.combinations(rules, 2):
        if not r1[1].contains(r2[1]):
            if r2[1].contains(r1[1]):
                r1,r2 = r2,r1
            else:
                continue
        ret.append((r1,r2))
    return ret

def report(path):
    with open(path) as f:
        result = analyze(f)
    for r1,r2 in result:
        print('Rule at line {1[0]} is redundant. See line {0[0]}\n  {0[0]} - {0[1]}\n  {1[0]} - {1[1]}\n'
                .format(r1,r2)
        )


import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        report(sys.argv[1])
