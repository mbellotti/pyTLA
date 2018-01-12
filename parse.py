import argparse, importlib, dis, subprocess, os, ast
import src.opscodes as ops

parser = argparse.ArgumentParser(add_help=True)
parser.add_argument('-f', type=str, help="file to convert")
args = parser.parse_args()

print('#################### INPUT ####################\n')
subprocess.call('cat pyscripts/%s.py' % (args.f,), shell=True)
print('\n')

with open('pyscripts/'+args.f+'.py') as f:
	c = f.read()
	a = ast.parse(c, args.f, 'exec')
	s = compile(a, args.f, 'exec')
	#print([ord(b) for b in s.co_code])

# Write PlusCal
b = ops.OpsCode(s, a, args.f)
b.convert()

with open('tla/%s.tla' % (args.f, ), 'w') as of:
	of.write(b.output.assemble())

print('\n#################### OUTPUT ####################\n')
subprocess.call('cat tla/%s.tla' % (args.f,), shell=True)
print('\n')

# Open Vim to add tests
#cmd =  '%s tla/%s.tla' % (os.environ.get('EDITOR', 'vi'), args.f)
#subprocess.call(cmd, shell=True)

# Translate PlusCal to TLA
#subprocess.call('pcal tla/%s.tla' % (args.f,), shell=True)

# Run Models
#subprocess.call('tlc tla/%s.tla' % (args.f,), shell=True)

