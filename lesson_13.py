# lesson 13

class Var:
    def __init__(self, name, typ):
        self.typ = typ
        self.name = name
    def run(self, ctx):
        val = ctx.getvalue(self.name)
        if self.typ == 'unknown':
            return val
        if val.typ != self.typ:
            pass
        assert val.typ == self.typ
        return val

class CodeBlock:
    def __init__(self, owner):
        self.vars = {}
        self.stmts = []
        self.owner = owner
    def DefineOrAssign(self, name, val):
        var = self.vars.get(name)
        if var is None:
            var = Var(name, val.typ)
            self.vars[name] = var
        stmt = LiuL.newstmt_assign(var, val)
        self.stmts.append(stmt)
        return var

    def FuncCall(self, fn, args):
        stmt = LiuL.newstmt_funccall(fn, args)
        self.stmts.append(stmt)

    def Return(self, val):
        stmt = LiuL.newstmt_return(val)
        self.stmts.append(stmt)

    def getvar(self, name):
        var = self.vars.get(name)
        if var:
            return var
        var = self.owner.getvar(name)
        assert var
        return var

    def run(self, ctx):
        ctx1 = RunContext(ctx)
        for v in self.stmts:
            if isinstance(v, LiuL_stmt_return):
                return v.run(ctx1)
            v.run(ctx1)

class DefinedFunc:
    def __init__(self, funcname, args, owner):
        self.name = funcname
        self.args = args
        self.block = CodeBlock(self)
        self.owner = owner
        self.vars = {}
        for name in args:
            var = Var(name, 'unknown')
            self.vars[name] = var
    def getvar(self, name):
        var = self.vars.get(name)
        if var:
            return var
        return self.owner.getvar(name)
    def run(self, args, ctx0):
        ctx = RunContext(ctx0)
        assert len(self.args) == len(args)
        for name, value in zip(self.args, args):
            ctx.setvalue(name, value)
        result = self.block.run(ctx)
        return result

class Value:
    def __init__(self, typ, val):
        self.typ = typ
        self.val = val
    def run(self, ctx):
        return self

class Operate2:
    def __init__(self, op, val1, val2):
        typ1,typ2 = val1.typ, val2.typ
        if typ1 == typ2:
            self.typ = typ1
        elif 'unknown' in (typ1, typ2):
            self.typ = 'unknown'
        else:
            assert False
        self.op = op
        self.val1 = val1
        self.val2 = val2
    def run(self, ctx):
        v1 = self.val1.run(ctx)
        v2 = self.val2.run(ctx)
        if self.op == '+':
            v3 = v1.val + v2.val
            return Value(self.typ, v3)
        elif self.op == '*':
            v3 = v1.val * v2.val
            return Value(self.typ, v3)
        assert False

class LiuL_stmt_assign:
    def __init__(self, dest, src):
        self.dest = dest
        self.src = src
    def run(self, ctx):
        value = self.src.run(ctx)
        ctx.setvalue(self.dest.name, value)

class LiuL_stmt_funccall:
    def __init__(self, fn, args):
        self.fn = fn
        self.args = args
    def run(self, ctx):
        argvalues = [v.run(ctx) for v in self.args]
        if isinstance(self.fn, GlobalFunc):
            return self.fn.run(argvalues)
        assert False

class LiuL_stmt_return:
    def __init__(self, val):
        self.val = val
    def run(self, ctx):
        value = self.val.run(ctx)
        return value

class GlobalFunc:
    def __init__(self, name):
        self.name = name
    def run(self, values):
        if self.name == 'print':
            lst = [v.val for v in values]
            print lst
            return
        assert False

class LiuL:
    def __init__(self):
        self.funcs = {}
        self.global_funcs = {
            'print' : GlobalFunc('print')
        }
    def def_func(self, funcname, args):
        the = DefinedFunc(funcname, args, self)
        self.funcs[funcname] = the
        return the
    def run(self, fn, args):
        tovalue = [Value('int', val) for val in args]
        return fn.run(tovalue, None)
    def getvar(self, name):
        v = self.funcs.get(name)
        if v:
            return v
        return self.global_funcs.get(name)

    @staticmethod
    def ConstantInt(n):
        return Value('int', n)
    @staticmethod
    def Add(val1, val2):
        return Operate2('+', val1, val2)
    @staticmethod
    def Multi(val1, val2):
        return Operate2('*', val1, val2)
    @staticmethod
    def newstmt_assign(dest, src):
        return LiuL_stmt_assign(dest, src)
    @staticmethod
    def newstmt_funccall(fn, args):
        return LiuL_stmt_funccall(fn, args)
    @staticmethod
    def newstmt_return(val):
        return LiuL_stmt_return(val)

class RunContext:
    def __init__(self, owner):
        self.owner = owner
        self.values = {}
    def setvalue(self, name, val):
        assert isinstance(val, Value)
        self.values[name] = val
    def getvalue(self, name):
        if name in self.values:
            val = self.values.get(name)
            return val
        return self.owner.getvalue(name)

def make_func1(liul):
    f = liul.def_func('func1', ['b1', 'b2'])

    a1 = LiuL.ConstantInt(3)
    i = f.block.DefineOrAssign('i', a1)

    a1 = LiuL.ConstantInt(2)
    a1 = LiuL.Add(i, a1)
    j = f.block.DefineOrAssign('j', a1)

    a1 = LiuL.ConstantInt(2)
    a1 = LiuL.Multi(j, a1)
    a1 = LiuL.Add(i, a1)

    a2 = f.block.getvar('b2')

    fn = f.block.getvar('print')
    f.block.FuncCall(fn, [a1,a2])

    f.block.Return(LiuL.ConstantInt(55))

    return f
    '''
    def func1(b1, b2):
        i = 3
        j = i + 2
        print(i+j*2, b2)
        return 55
        '''

import unittest
class Test(unittest.TestCase):
    def test1(self):
        liul = LiuL()
        f = make_func1(liul)
        result = liul.run(f, [5,7])
        print result.val
        self.assertEqual(result.val, 55)


if __name__ == '__main__':
    the = Test(methodName='test1')
    the.test1()
    print 'good'
