import dis, ast
BINARY_OPERATOR = {
	'BINARY_ADD' : '+',
	'BINARY_SUBTRACT': '-',
	'BINARY_MULTIPLY': '*'
}


class OpsCode():
	def __init__(self, opscodes, tree, filename):
		self.functions = self._function_and_arguments(tree)
		self.codes = (ord(b) for b in opscodes.co_code)
		self.names = opscodes.co_names
		self.varnames = opscodes.co_varnames
		self.constants = opscodes.co_consts
		self.cellvars = opscodes.co_cellvars
		self.freevars = opscodes.co_freevars
		self.tla_variables = {} # [variable_name] = variable_type
		self.output = TLA(filename) #Lines of TLA code
		self.lines = []
		self.step = 65
		self.stack = []
		self.fn = ('',[])
		self.fni = 0
	
	def _function_and_arguments(self, tree):
		for node in ast.walk(tree):
			if isinstance(node, ast.FunctionDef):
				yield (node.name, [a.id for a in node.args.args])

				
	
	def set_variable(self, name):
		try:
			self.tla_variables[name]
		except:
			self.tla_variables[name] = None
		return
		
	def type_variable(self, name, value):
		if type(value) is int:
			self.tla_variables[name] = 'int'
		elif value is None:
			self.tla_variables[name] = 'return'
		else:
			self.tla_variables[name] = 'str'
		return
			
			
	def define(self, o):
		arg = None#Placeholder
		pos = None
		c = dis.opname[o]
		if c == 'STOP_CODE':
			return
		#print(str(o)+' -> '+ c)
		
		#######
		if o == 132: # 132 is MAKE_FUNCTION
			self.fn = self.functions.next()
			
		if o == 83: # 83 is RETURN_VALUE
			pass
			#print(self.stack)
			
		if o >= dis.HAVE_ARGUMENT:
			pos = self.codes.next() # varname stack position is the next code over
		if o in dis.hasconst:
			if type(self.constants[pos]).__name__ == 'code':#This is a function name
				return self.names[pos]
			else:
				try:
					self.set_variable(self.names[pos])
					self.type_variable(self.names[pos], self.constants[pos])
					self.stack.append(self.names[pos])
					return self.names[pos]
				except:
					self.set_variable(self.fn[1][self.fni])
					self.type_variable(self.fn[1][self.fni], self.constants[pos])
					self.stack.append(self.fn[1][self.fni])
					self.fni += 1
					return self.fn[1][self.fni-1]
					
		elif o in dis.hasfree:
			#print('Has Free')
			if pos < len(self.cellvars):
				arg = self.cellvars[pos]
			else:
				var_idx = pos - len(self.cellvars)
				arg = self.freevars[var_idx]
			return arg
		elif o in dis.hasname:
			#print('Has Name')
			#print(self.names[pos])
			if type(self.constants[pos]).__name__ == 'code':#This is a function name
				return self.names[pos]
			else:
				self.set_variable(self.names[pos])
				return self.names[pos]
		elif o in dis.hasjrel:
			#print('Has jrel')
			#arg = f.f_lasti + intArg
			pass
		elif o in dis.hasjabs:
			#print('Has Jabs')
			return pos
		elif o in dis.haslocal:
			#print('Has Local')
			#print(self.varnames[pos])
			self.set_variable(self.varnames[pos])
			return self.varnames[pos]
		else:
			arg = pos
		
		if c in BINARY_OPERATOR.keys():
			v = self.define(self.codes.next())
			a1 = self.stack.pop()
			a2 =  self.stack.pop()
			self.lines.append('Step%s: %s := %s%s%s;'% (chr(self.step), v, a1,BINARY_OPERATOR[c], a2))
			return
	
		
	def convert(self):
		for o in self.codes:
			self.define(o)
		if self.tla_variables:
			self.output.compose(self.tla_variables, 'variables')
		if self.lines:
			self.output.compose(self.lines, 'lines')
		
			

class TLA():
	def __init__(self, filename):
		self.begin = [
			'---------------------------- MODULE %s ----------------------------' % (filename,),
		    'EXTENDS Naturals, TLC',
		    '(* --algorithm '+filename,
			'']
			
		self.end = [
			'', # Extra space
			'end algorithm *)',
			'',
			'\* Add tests either here or with assert statements throughout the algorithm',
			'',
		    '=============================================================================',
			]
			
		self.lines = []
		
	def compose(self, data, mode):
		if mode == 'variables':
			self.lines = self.lines + ['variables '+', '.join([self.fuzz(k,v) for k,v in data.iteritems()])+';','','begin']
		if mode == 'lines':
			self.lines = self.lines + data
	
	def fuzz(self, k, v):
		if v == 'int':
			return '%s \\in 1..100' % (k,)
		if v == 'bool':
			return 	'%s \\in {TRUE, FALSE}' % (k,)	
		if v == 'str':
			return 	'%s \\in {"foo", "bar"}' % (k,)
		else:
			return 	'%s=0' % (k,)
		
		
	def add(self, command):
		'''Take a command string and add it to our algorithm'''
		self.lines.append(command)	
		
	def assemble(self):
		'''Return the finished TLA document'''
		r = '\n'.join(self.begin + self.lines + self.end)
		return r