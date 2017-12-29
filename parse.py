import argparse, importlib, dis, subprocess, os
import src.opscodes as ops

parser = argparse.ArgumentParser(add_help=True)
parser.add_argument('-f', type=str, help="file to convert")
args = parser.parse_args()

with open('pyscripts/'+args.f+'.py') as f:
	s = compile(f.read(), args.f, 'exec')

# Write PlusCal
b = ops.OpsCode(s, args.f)
b.convert()

with open('tla/%s.tla' % (args.f, ), 'w') as of:
	of.write(b.output.assemble())

# Open Vim to add tests
cmd =  '%s tla/%s.tla' % (os.environ.get('EDITOR', 'vi'), args.f)
subprocess.call(cmd, shell=True)

# Translate PlusCal to TLA
subprocess.call('pcal tla/%s.tla' % (args.f,), shell=True)

# Run Models
subprocess.call('tlc tla/%s.tla' % (args.f,), shell=True)

