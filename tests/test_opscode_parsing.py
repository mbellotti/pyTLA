import pyTLA.src.opscodes as code

class TestsOpsCodeParsing(object):
	
	def test_hello_world(self):
		c ='x = 5 \ny = 3\nz = x+y'
		b = compile(c, 'hello_world', 'exec')
		o = code.OpsCode(b,'hello_world')
		o.convert()
		assert o.output.lines == ['variables y \\in 1..100, x \\in 1..100, z=0;', '', 'begin', 'StepA: z := y+x;']
		
	def test_hello_world_subtract(self):
		c ='x = 5 \ny = 3\nz = x-y'
		b = compile(c, 'hello_world_sub', 'exec')
		o = code.OpsCode(b,'hello_world_sub')
		o.convert()
		assert o.output.lines == ['variables y \\in 1..100, x \\in 1..100, z=0;', '', 'begin', 'StepA: z := y-x;']