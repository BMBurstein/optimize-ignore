from __future__ import annotations

import collections
import itertools
import os.path
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
        rule = rule.strip()
        self.rule = rule
        self.isComment = False
        self.isEmpty = False
        if not rule:
            self.isEmpty = True
        elif rule[0] == '#':
            self.isComment = True
            self.isEmpty = True
        else:
            self.isDir = rule.endswith('/')
            self.isRooted = rule.find('/', 0, -1) >= 0
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
        if escape:
            raise RuleError('Trailing whitespace is not supported')
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
        if self.isEmpty:
            return False
        return all(self.re.fullmatch(d) for d in other.dummys)


def analyze(f):
    RuleInfo = collections.namedtuple('RuleInfo', ['line', 'rule'])
    rules = []
    for i, line in enumerate(f, 1):
        line = line.strip()
        try:
            rule = Rule(line)
            rules.append(RuleInfo(i, rule))
        except RuleError as e:
            raise RuntimeError("Could not process rule at line {}: {}\n{}\n".format(i, line, e))
    pairs = []
    redundant = set()
    for r1,r2 in itertools.combinations(rules, 2):
        if not r1.rule.contains(r2.rule):
            if r2.rule.contains(r1.rule):
                r1,r2 = r2,r1
            else:
                continue
        pairs.append((r1,r2))
        redundant.add(r2.line)
    pairs = [x for x in pairs if x[0].line not in redundant]
    return pairs, redundant, rules

def optimize(path, report):
    with open(path) as f:
        pairs, redundant, rules = analyze(f)
    if report:
        for r1,r2 in pairs:
            print('Rule at line {1.line} is redundant. See line {0.line}\n  {0.line} - {0.rule}\n  {1.line} - {1.rule}\n'.format(r1,r2))
        print('Total rules: {}\nRedundant:   {}'.format(len(rules), len(redundant)))
    else:
        for r in rules:
            if r.line not in redundant:
                print(r.rule)


import sys

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == '--report':
        optimize(sys.argv[2], True)
    elif len(sys.argv) == 2 and sys.argv[1] != '--report':
        optimize(sys.argv[1], False)
    else:
        print("Usage: {} [--report] file".format(sys.argv[0]))
