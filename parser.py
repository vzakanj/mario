#!/usr/bin/env python3
# Copyright (c) 2015 Damir Jelić
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from pyparsing import *


def make_parser():
    ParserElement.setDefaultWhitespaceChars("")

# TODO make whitespace less strict
    EOL    = LineEnd().suppress()
    Space  = Literal(' ').suppress()
    Tab    = Literal('\t').suppress()
    WS     = OneOrMore(Space)
    indent = OneOrMore(Space) | OneOrMore(Tab)

# TODO SkipTo(EOL) Word -> Regex?
    ArgTxt   = Word(printables)('arg')
    NameTxt  = Word(alphas + nums + '-' + '_')
    Variable = Combine('{' + NameTxt + '}')
    MatchArg = Group(ArgTxt + ZeroOrMore(EOL + indent + ArgTxt))

    KindObjects = Keyword('kind')
    KindVerbs   = Keyword('is')
    KindArgs    = Keyword('url')  | \
                  Keyword('raw')

# TODO change the grammar when the kind changes
    KindMatchRule = Group(KindObjects('object') + WS + \
                          KindVerbs('verb')     + WS + \
                          KindArgs('args'))

    MatchObjects = Keyword('arg')
    MatchVerbs   = Keyword('is')      | \
                   Keyword('istype')  | \
                   Keyword('matches') | \
                   Keyword('rewrite')

    ArgMatchRule = Group(MatchObjects('object') + WS + \
                         MatchVerbs('verb')     + WS + \
                         Variable('var')        + WS + \
                         MatchArg('args'))
    ArgMatchRule = ArgMatchRule('match-rule')

# TODO make the ArgMatchRule as well optional
    MatchLines = Group(Optional(KindMatchRule('kind-rule') + EOL) + \
                       ArgMatchRule + ZeroOrMore(EOL + ArgMatchRule))

    ActionObject = Keyword('plumb')
    ActionVerb   = Keyword('open')     | \
                   Keyword('download')

    ActionArg = Combine(Word(printables) + SkipTo(EOL))

    ActionRule = Group(ActionObject('object') + WS + \
                       ActionVerb('verb')     + WS + \
                       ActionArg('arg'))

    ActionRule = ActionRule('act-rule')

    ActionLines = Group(ActionRule + ZeroOrMore(EOL + ActionRule))

    RuleName = Suppress('[') + NameTxt + Suppress(']') + EOL

    Rule = Group(RuleName('name') + \
                 MatchLines('match-lines') + EOL + \
                 ActionLines('act-lines'))

    RuleFile = Rule('rule') + ZeroOrMore(EOL + Rule('rule')) + StringEnd()
    RuleFile = RuleFile('rules')

    return RuleFile


def extract_parse_result(result):
    rules = []

    for rule in result.asList():
        rules += [[rule[0], (rule[1], rule[2])]]

    return rules


def parse_rule_file(parser, rule_file):
    result = parser.parseFile(rule_file)
    return extract_parse_result(result)


def parse_rule_string(parser, rule_string):
    result = parser.parseString(rule_string)
    return extract_parse_result(result)
