#!/usr/bin/python -O
# -*- coding: utf-8 -*-

# 2014 Stephan Boyer
# 2017, 2021 Kardi Teknomo 

from prover import *

##############################################################################
# Command-line interface
##############################################################################

class InvalidInputError(Exception):
  def __init__(self, message):
    self.message = message

def lex(inp):
  # perform a lexical analysis
  tokens = []
  pos = 0
  while pos < len(inp):
    # skip whitespace
    if inp[pos] == ' ':
      pos += 1
      continue

    # identifiers
    identifier = ''
    while pos < len(inp) and inp[pos].isalnum():
      identifier += inp[pos]
      pos += 1
    if len(identifier) > 0:
      tokens.append(identifier)
      continue

    # symbols
    tokens.append(inp[pos])
    pos += 1

  # return the tokens
  return tokens

def parse(tokens):
  # keywords
  keywords = ['not', 'implies', 'and', 'or', 'forall', 'exists']
  tokens = [(token.lower() if token in keywords else token)
    for token in tokens]

  # empty formula
  if len(tokens) == 0:
    raise InvalidInputError('Empty formula.')

  # ForAll
  if tokens[0] == 'forall':
    dot_pos = None
    for i in range(1, len(tokens)):
      if tokens[i] == '.':
        dot_pos = i
        break
    if dot_pos is None:
      raise InvalidInputError('Missing \'.\' in FORALL quantifier.')
    args = []
    i = 1
    while i <= dot_pos:
      end = dot_pos
      depth = 0
      for j in range(i, dot_pos):
        if tokens[j] == '(':
          depth += 1
          continue
        if tokens[j] == ')':
          depth -= 1
          continue
        if depth == 0 and tokens[j] == ',':
          end = j
          break
      if i == end:
        raise InvalidInputError('Missing variable in FORALL quantifier.')
      args.append(parse(tokens[i:end]))
      i = end + 1
    if len(tokens) == dot_pos + 1:
      raise InvalidInputError('Missing formula in FORALL quantifier.')
    formula = parse(tokens[dot_pos + 1:])
    for variable in reversed(args):
      formula = ForAll(variable, formula)
    return formula

  # ThereExists
  if tokens[0] == 'exists':
    dot_pos = None
    for i in range(1, len(tokens)):
      if tokens[i] == '.':
        dot_pos = i
        break
    if dot_pos is None:
      raise InvalidInputError('Missing \'.\' in exists quantifier.')
    if dot_pos == 1:
      raise InvalidInputError('Missing variable in exists quantifier.')
    args = []
    i = 1
    while i <= dot_pos:
      end = dot_pos
      depth = 0
      for j in range(i, dot_pos):
        if tokens[j] == '(':
          depth += 1
          continue
        if tokens[j] == ')':
          depth -= 1
          continue
        if depth == 0 and tokens[j] == ',':
          end = j
          break
      if i == end:
        raise InvalidInputError('Missing variable in exists quantifier.')
      args.append(parse(tokens[i:end]))
      i = end + 1
    if len(tokens) == dot_pos + 1:
      raise InvalidInputError('Missing formula in exists quantifier.')
    formula = parse(tokens[dot_pos + 1:])
    for variable in reversed(args):
      formula = ThereExists(variable, formula)
    return formula

  # Implies
  implies_pos = None
  depth = 0
  for i in range(len(tokens)):
    if tokens[i] == '(':
      depth += 1
      continue
    if tokens[i] == ')':
      depth -= 1
      continue
    if depth == 0 and tokens[i] == 'implies':
      implies_pos = i
      break
  if implies_pos is not None:
    quantifier_in_left = False
    depth = 0
    for i in range(implies_pos):
      if tokens[i] == '(':
        depth += 1
        continue
      if tokens[i] == ')':
        depth -= 1
        continue
      if depth == 0 and (tokens[i] == 'forall' or tokens[i] == 'exists'):
        quantifier_in_left = True
        break
    if not quantifier_in_left:
      if implies_pos == 0 or implies_pos == len(tokens) - 1:
        raise InvalidInputError('Missing formula in IMPLIES connective.')
      return Implies(parse(tokens[0:implies_pos]),
        parse(tokens[implies_pos+1:]))

  # Or
  or_pos = None
  depth = 0
  for i in range(len(tokens)):
    if tokens[i] == '(':
      depth += 1
      continue
    if tokens[i] == ')':
      depth -= 1
      continue
    if depth == 0 and tokens[i] == 'or':
      or_pos = i
      break
  if or_pos is not None:
    quantifier_in_left = False
    depth = 0
    for i in range(or_pos):
      if tokens[i] == '(':
        depth += 1
        continue
      if tokens[i] == ')':
        depth -= 1
        continue
      if depth == 0 and (tokens[i] == 'forall' or tokens[i] == 'exists'):
        quantifier_in_left = True
        break
    if not quantifier_in_left:
      if or_pos == 0 or or_pos == len(tokens) - 1:
        raise InvalidInputError('Missing formula in OR connective.')
      return Or(parse(tokens[0:or_pos]), parse(tokens[or_pos+1:]))

  # And
  and_pos = None
  depth = 0
  for i in range(len(tokens)):
    if tokens[i] == '(':
      depth += 1
      continue
    if tokens[i] == ')':
      depth -= 1
      continue
    if depth == 0 and tokens[i] == 'and':
      and_pos = i
      break
  if and_pos is not None:
    quantifier_in_left = False
    depth = 0
    for i in range(and_pos):
      if tokens[i] == '(':
        depth += 1
        continue
      if tokens[i] == ')':
        depth -= 1
        continue
      if depth == 0 and (tokens[i] == 'forall' or tokens[i] == 'exists'):
        quantifier_in_left = True
        break
    if not quantifier_in_left:
      if and_pos == 0 or and_pos == len(tokens) - 1:
        raise InvalidInputError('Missing formula in AND connective.')
      return And(parse(tokens[0:and_pos]), parse(tokens[and_pos+1:]))

  # Not
  if tokens[0] == 'not':
    if len(tokens) < 2:
      raise InvalidInputError('Missing formula in NOT connective.')
    return Not(parse(tokens[1:]))

  # Function
  if tokens[0].isalnum() and tokens[0].lower() not in keywords and \
    len(tokens) > 1 and not any([c.isupper() for c in tokens[0]]) and \
    tokens[1] == '(':
    if tokens[-1] != ')':
      raise InvalidInputError('Missing \')\' after function argument list.')
    name = tokens[0]
    args = []
    i = 2
    if i < len(tokens) - 1:
      while i <= len(tokens) - 1:
        end = len(tokens) - 1
        depth = 0
        for j in range(i, len(tokens) - 1):
          if tokens[j] == '(':
            depth += 1
            continue
          if tokens[j] == ')':
            depth -= 1
            continue
          if depth == 0 and tokens[j] == ',':
            end = j
            break
        if i == end:
          raise InvalidInputError('Missing function argument.')
        args.append(parse(tokens[i:end]))
        i = end + 1
    return Function(name, args)

  # Predicate
  if tokens[0].isalnum() and tokens[0].lower() not in keywords and \
    len(tokens) == 1 and any([c.isupper() for c in tokens[0]]):
    return Predicate(tokens[0], [])
  if tokens[0].isalnum() and tokens[0].lower() not in keywords and \
    len(tokens) > 1 and any([c.isupper() for c in tokens[0]]) and \
    tokens[1] == '(':
    if tokens[-1] != ')':
      raise InvalidInputError('Missing \')\' after predicate argument list.')
    name = tokens[0]
    args = []
    i = 2
    if i < len(tokens) - 1:
      while i <= len(tokens) - 1:
        end = len(tokens) - 1
        depth = 0
        for j in range(i, len(tokens) - 1):
          if tokens[j] == '(':
            depth += 1
            continue
          if tokens[j] == ')':
            depth -= 1
            continue
          if depth == 0 and tokens[j] == ',':
            end = j
            break
        if i == end:
          raise InvalidInputError('Missing predicate argument.')
        args.append(parse(tokens[i:end]))
        i = end + 1
    return Predicate(name, args)

  # Variable
  if tokens[0].isalnum() and tokens[0].lower() not in keywords and \
    len(tokens) == 1 and not any([c.isupper() for c in tokens[0]]):
    return Variable(tokens[0])

  # Group
  if tokens[0] == '(':
    if tokens[-1] != ')':
      raise InvalidInputError('Missing \')\'.')
    if len(tokens) == 2:
      raise InvalidInputError('Missing formula in parenthetical group.')
    return parse(tokens[1:-1])

  raise InvalidInputError('Unable to parse: %s...' % tokens[0])

def typecheck_term(term):
  if isinstance(term, Variable):
    return
  if isinstance(term, Function):
    for subterm in term.terms:
      typecheck_term(subterm)
    return
  raise InvalidInputError('Invalid term: %s.' % term)

def typecheck_formula(formula):
  if isinstance(formula, Predicate):
    for term in formula.terms:
      typecheck_term(term)
    return
  if isinstance(formula, Not):
    typecheck_formula(formula.formula)
    return
  if isinstance(formula, And):
    typecheck_formula(formula.formula_a)
    typecheck_formula(formula.formula_b)
    return
  if isinstance(formula, Or):
    typecheck_formula(formula.formula_a)
    typecheck_formula(formula.formula_b)
    return
  if isinstance(formula, Implies):
    typecheck_formula(formula.formula_a)
    typecheck_formula(formula.formula_b)
    return
  if isinstance(formula, ForAll):
    if not isinstance(formula.variable, Variable):
      raise InvalidInputError('Invalid bound variable in ' \
        'FORALL quantifier: %s.' % formula.variable)
    typecheck_formula(formula.formula)
    return
  if isinstance(formula, ThereExists):
    if not isinstance(formula.variable, Variable):
      raise InvalidInputError('Invalid bound variable in ' \
        'exists quantifier: %s.' % formula.variable)
    typecheck_formula(formula.formula)
    return
  raise InvalidInputError('Invalid formula: %s.' % formula)

def check_formula(formula):
  try:
    typecheck_formula(formula)
  except InvalidInputError as formula_error:
    try:
      typecheck_term(formula)
    except InvalidInputError as term_error:
      raise formula_error
    else:
      raise InvalidInputError('Enter a formula, not a term.')


def help():
    s=""
    s=s+'First-Order Logic Theorem Prover'+'\n'
    s=s+'2014 Stephan Boyer'+'\n'
    s=s+'2017,2021 Kardi Teknomo'+'\n'
    s=s+''+'\n'
    s=s+'Terms:'+'\n'
    s=s+''+'\n'
    s=s+'  x               (variable)'+'\n'
    s=s+'  f(term, ...)    (function)'+'\n'
    s=s+''+'\n'
    s=s+'Formulae:'+'\n'
    s=s+''+'\n'
    s=s+'  P(term)        (predicate)'+'\n'
    s=s+'  not P          (complement)'+'\n'
    s=s+'  P or Q         (disjunction)'+'\n'
    s=s+'  P and Q        (conjunction)'+'\n'
    s=s+'  P implies Q    (implication)'+'\n'
    s=s+'  forall x. P(x) (universal quantification)'+'\n'
    s=s+'  exists x. P(x) (existential quantification)'+'\n'
    s=s+''+'\n'
    s=s+'Enter formulae at the prompt. The following commands ' \
    'are also available for manipulating axioms:'+'\n'
    s=s+''+'\n'
    s=s+'  axioms              (list axioms)'+'\n'
    s=s+'  lemmas              (list lemmas)'+'\n'
    s=s+'  axiom <formula>     (add an axiom)'+'\n'
    s=s+'  lemma <formula>     (prove and add a lemma)'+'\n'
    s=s+'  remove <formula>    (remove an axiom or lemma)'+'\n'
    s=s+'  reset               (remove all axioms and lemmas)'+'\n'
    s=s+'  quit                (quit the program)'+'\n'
    print(s)
    return s

def interactive():
  axioms = set()
  lemmas = {}

  while True:
    try:
      inp = input('\n> ')
      commands = ['axiom', 'lemma', 'axioms', 'lemmas', 'remove', 'reset']
      tokens = [(token.lower() if token in commands else token)
        for token in lex(inp)]
      for token in tokens[1:]:
        if token in commands:
          raise InvalidInputError('Unexpected keyword: %s.' % token)
      if len(tokens) > 0 and tokens[0] == 'axioms':
        if len(tokens) > 1:
          raise InvalidInputError('Unexpected: %s.' % tokens[1])
        for axiom in axioms:
          print(axiom)
      elif len(tokens) > 0 and tokens[0] == 'lemmas':
        if len(tokens) > 1:
          raise InvalidInputError('Unexpected: %s.' % tokens[1])
        for lemma in lemmas:
          print(lemma)
      elif len(tokens) > 0 and tokens[0] == 'axiom':
        formula = parse(tokens[1:])
        check_formula(formula)
        axioms.add(formula)
        print('Axiom added: %s.' % formula)
      elif len(tokens) > 0 and tokens[0] == 'lemma':
        formula = parse(tokens[1:])
        check_formula(formula)
        result = proveFormula(axioms | set(lemmas.keys()), formula)
        if result:
          lemmas[formula] = axioms.copy()
          print('Lemma proven: %s.' % formula)
        else:
          print('Lemma unprovable: %s.' % formula)
      elif len(tokens) > 0 and tokens[0] == 'remove':
        formula = parse(tokens[1:])
        check_formula(formula)
        if formula in axioms:
          axioms.remove(formula)
          bad_lemmas = []
          for lemma, dependent_axioms in lemmas.items():
            if formula in dependent_axioms:
              bad_lemmas.append(lemma)
          for lemma in bad_lemmas:
            del lemmas[lemma]
          print('Axiom removed: %s.' % formula)
          if len(bad_lemmas) == 1:
            print('This lemma was proven using that ' \
              'axiom and was also removed:')
            for lemma in bad_lemmas:
              print('  %s' % lemma)
          if len(bad_lemmas) > 1:
            print('These lemmas were proven using that ' \
              'axiom and were also removed:')
            for lemma in bad_lemmas:
              print('  %s' % lemma)
        elif formula in lemmas:
          del lemmas[formula]
          print('Lemma removed: %s.' % formula)
        else:
          print('Not an axiom: %s.' % formula)
      elif len(tokens) > 0 and tokens[0] == 'reset':
        if len(tokens) > 1:
          raise InvalidInputError('Unexpected: %s.' % tokens[1])
        axioms = set()
        lemmas = {}
      elif len(tokens) > 0 and (tokens[0] == 'quit' or tokens[0] == 'exit') :
          print('now I exit interactive mode')
          break
      else:
        formula = parse(tokens)
        check_formula(formula)
        result = proveFormula(axioms | set(lemmas.keys()), formula)
        if result:
          print('Formula proven: %s.' % formula)
        else:
          print('Formula unprovable: %s.' % formula)
    except InvalidInputError as e:
      print(e.message)
    except KeyboardInterrupt:
      pass
    except EOFError:
      print('')
      break


# wrapper to receive a list of axioms and lemmas in a statement
def prove(statement):

  axioms = set()
  lemmas = {}
  output=""
  for inp in statement:
    try:
      commands = ['axiom', 'lemma', 'axioms', 'lemmas', 'remove', 'reset']
      tokens = [(token.lower() if token in commands else token)
        for token in lex(inp)]
      for token in tokens[1:]:
        if token in commands:
          raise InvalidInputError('Unexpected keyword: %s.' % token)
      if len(tokens) > 0 and tokens[0] == 'axioms':
        if len(tokens) > 1:
          raise InvalidInputError('Unexpected: %s.' % tokens[1])
        for axiom in axioms:
          output=output+axiom+"\n"
          print(axiom)
      elif len(tokens) > 0 and tokens[0] == 'lemmas':
        if len(tokens) > 1:
          raise InvalidInputError('Unexpected: %s.' % tokens[1])
        for lemma in lemmas:
          output=output+lemma+'\n'
          print(lemma)
      elif len(tokens) > 0 and tokens[0] == 'axiom':
        formula = parse(tokens[1:])
        check_formula(formula)
        axioms.add(formula)
        output=output+ 'Axiom added: %s.' % formula+'\n'
        print('Axiom added: %s.' % formula)
      elif len(tokens) > 0 and tokens[0] == 'lemma':
        formula = parse(tokens[1:])
        check_formula(formula)
        result,proof = proveFormula(axioms | set(lemmas.keys()), formula)
        if result:
          lemmas[formula] = axioms.copy()
          output=output+'Lemma proven: %s.' % formula+'\n'
          print('Lemma proven: %s.' % formula)
        else:
          output=output+'Lemma unprovable: %s.' % formula+'\n'
          print('Lemma unprovable: %s.' % formula)
      elif len(tokens) > 0 and tokens[0] == 'remove':
        formula = parse(tokens[1:])
        check_formula(formula)
        if formula in axioms:
          axioms.remove(formula)
          bad_lemmas = []
          for lemma, dependent_axioms in lemmas.items():
            if formula in dependent_axioms:
              bad_lemmas.append(lemma)
          for lemma in bad_lemmas:
            del lemmas[lemma]
          output=output+'Axiom removed: %s.' % formula+'\n'
          print('Axiom removed: %s.' % formula)
          if len(bad_lemmas) == 1:
            output=output+'This lemma was proven using that ' \
              'axiom and was also removed:'+'\n'
            print('This lemma was proven using that ' \
              'axiom and was also removed:')
            for lemma in bad_lemmas:
              output=output+'  %s' % lemma+'\n'
              print('  %s' % lemma)
          if len(bad_lemmas) > 1:
            print('These lemmas were proven using that ' \
              'axiom and were also removed:')
            for lemma in bad_lemmas:
              output=output+'  %s' % lemma+'\n'
              print('  %s' % lemma)
        elif formula in lemmas:
          del lemmas[formula]
          output=output+'Lemma removed: %s.' % formula+'\n'
          print('Lemma removed: %s.' % formula)
        else:
          output=output+'Not an axiom: %s.' % formula+'\n'
          print('Not an axiom: %s.' % formula)
      elif len(tokens) > 0 and tokens[0] == 'reset':
        if len(tokens) > 1:
          raise InvalidInputError('Unexpected: %s.' % tokens[1])
        axioms = set()
        lemmas = {}
      else:
        formula = parse(tokens)
        check_formula(formula)
        result,proof = proveFormula(axioms | set(lemmas.keys()), formula)
        if result:
          output=output+'Formula proven: %s.' % formula+'\n'
          print('Formula proven: %s.' % formula)
        else:
          output=output+'Formula unprovable: %s.' % formula+'\n'
          print('Formula unprovable: %s.' % formula)
    except InvalidInputError as e:
      output=e.message
      print(e.message)
    except KeyboardInterrupt:
      pass
    except EOFError:
      output=""
      print('')
      break
  return output,proof



if __name__ == '__main__':
  help()
  interactive()
