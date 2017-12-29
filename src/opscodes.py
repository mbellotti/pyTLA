import dis
BINARY_OPERATOR = {
	'BINARY_ADD' : '+',
	'BINARY_SUBTRACT': '-',
	'BINARY_MULTIPLY': '*'
}


class OpsCode():
	def __init__(self, opscodes, filename):
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
		print(str(o)+' -> '+ c)
		
		#######
		if o >= dis.HAVE_ARGUMENT:
			pos = self.codes.next() # varname stack position is the next code over
		if o in dis.hasconst:
			if type(self.constants[pos]).__name__ == 'code':#This is a function name
				pass
			else:
				try:
					self.set_variable(self.names[pos])
				except:
					print('Here is the error')
					print(self.varnames)
				self.type_variable(self.names[pos], self.constants[pos])
				self.stack.append(self.names[pos])
				return self.names[pos]
		elif o in dis.hasfree:
			print('Has Free')
			if pos < len(self.cellvars):
				arg = self.cellvars[pos]
			else:
				var_idx = pos - len(self.cellvars)
				arg = self.freevars[var_idx]
			return arg
		elif o in dis.hasname:
			print('Has Name')
			print(self.names[pos])
			self.set_variable(self.names[pos])
			return self.names[pos]
		elif o in dis.hasjrel:
			print('Has jrel')
			#arg = f.f_lasti + intArg
		elif o in dis.hasjabs:
			print('Has Jabs')
			return pos
		elif o in dis.haslocal:
			print('Has Local')
			print(self.varnames[pos])
			self.set_variable(self.varnames[pos])
			return self.varnames[pos]
		else:
			arg = pos
		######
				#
		# if c in ['LOAD_FAST', 'LOAD_CONST', 'LOAD_NAME']:
		# 	try:
		# 		self.tla_variables[self.names[pos]]
		# 	except:
		# 		self.tla_variables[self.names[pos]] = None
		#
		# 	if c == 'LOAD_CONST':
		# 		self.stack.append(self.constants[pos])
		# 		return self.constants[pos]
		# 	else:
		# 		self.stack.append(self.names[pos])
		# 		return self.names[pos]
		#
		#
		# if c in ['STORE_FAST', 'STORE_NAME']:
		# 	# Determine type and update self.tla_variables
		# 	pos = self.codes.next()
		# 	if type(self.constants[pos]) is int:
		# 		self.tla_variables[self.names[pos]] = 'int'
		# 	elif self.constants[pos] is None:
		# 		self.tla_variables[self.names[pos]] = 'return'
		# 	else:
		# 		self.tla_variables[self.names[pos]] = 'str'
		# 	return self.names[pos]
		#		
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
		if v == 'return':
			return 	'%s=0' % (k,)
		
		
	def add(self, command):
		'''Take a command string and add it to our algorithm'''
		self.lines.append(command)	
		
	def assemble(self):
		'''Return the finished TLA document'''
		r = '\n'.join(self.begin + self.lines + self.end)
		print(self.lines)
		return r