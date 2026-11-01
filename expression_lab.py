"""A bounded AST interpreter for expression exercises. No eval, exec or imports."""
import ast
import operator
from dataclasses import dataclass

@dataclass(frozen=True)
class LabTask:
    id: str
    topic: str
    difficulty: str
    target: str
    prompt: str
    context: dict
    required: str
    example: str
    comprehension_blank: bool = False

class ExpressionError(ValueError):pass

def evaluate(expression,context):
    if len(expression)>240:raise ExpressionError('Keep your expression under 240 characters.')
    try:tree=ast.parse(expression,mode='eval')
    except SyntaxError:raise ExpressionError('Use one valid Python expression, without print or an assignment.')
    if sum(1 for _ in ast.walk(tree))>80:raise ExpressionError('That expression is too complex.')
    functions={'len':len,'sum':sum,'min':min,'max':max,'abs':abs,'str':str,'int':int,'bool':bool,
               'list':list,'sorted':sorted,'round':round,'pow':pow}
    def bounded(value):
        if isinstance(value,int) and value.bit_length()>128:raise ExpressionError('That number is too large.')
        if isinstance(value,(str,list,tuple,range)) and len(value)>200:raise ExpressionError('Keep collections under 200 items.')
        return value
    def visit(node):
        if isinstance(node,ast.Expression):return visit(node.body)
        if isinstance(node,ast.Constant) and type(node.value) in (int,float,str,bool,type(None)):
            return bounded(node.value)
        if isinstance(node,ast.Name) and node.id in context:return context[node.id]
        if isinstance(node,(ast.List,ast.Tuple)):
            items=[visit(n) for n in node.elts];return bounded(items if isinstance(node,ast.List) else tuple(items))
        if isinstance(node,ast.BinOp):
            a,b=visit(node.left),visit(node.right)
            ops={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv,
                 ast.FloorDiv:operator.floordiv,ast.Mod:operator.mod,ast.Pow:operator.pow}
            if type(node.op) not in ops:raise ExpressionError('That operator is not supported.')
            if isinstance(node.op,ast.Pow) and (type(b) not in (int,float) or abs(b)>12):raise ExpressionError('Use an exponent between -12 and 12.')
            if isinstance(node.op,ast.Mult):
                if isinstance(a,(str,list,tuple)) and isinstance(b,int) and len(a)*abs(b)>200:raise ExpressionError('That repetition is too large.')
                if isinstance(b,(str,list,tuple)) and isinstance(a,int) and len(b)*abs(a)>200:raise ExpressionError('That repetition is too large.')
            if isinstance(node.op,ast.Mod) and isinstance(a,str):raise ExpressionError('String formatting is not part of these exercises.')
            return bounded(ops[type(node.op)](a,b))
        if isinstance(node,ast.UnaryOp):
            value=visit(node.operand)
            if isinstance(node.op,ast.Not):return not value
            if isinstance(node.op,ast.USub):return bounded(-value)
            if isinstance(node.op,ast.UAdd):return value
        if isinstance(node,ast.BoolOp):
            value=visit(node.values[0])
            for item in node.values[1:]:
                if isinstance(node.op,ast.And) and not value:return value
                if isinstance(node.op,ast.Or) and value:return value
                value=visit(item)
            return value
        if isinstance(node,ast.Compare):
            ops={ast.Eq:operator.eq,ast.NotEq:operator.ne,ast.Lt:operator.lt,ast.LtE:operator.le,
                 ast.Gt:operator.gt,ast.GtE:operator.ge,ast.In:lambda a,b:a in b,ast.NotIn:lambda a,b:a not in b}
            a=visit(node.left)
            for op,other in zip(node.ops,node.comparators):
                if type(op) not in ops:raise ExpressionError('That comparison is not supported.')
                b=visit(other)
                if not ops[type(op)](a,b):return False
                a=b
            return True
        if isinstance(node,ast.Subscript):
            value=visit(node.value)
            if not isinstance(value,(str,list,tuple,range)):raise ExpressionError('Only strings and sequences can be indexed.')
            index=node.slice
            if isinstance(index,ast.Slice):
                index=slice(*(visit(x) if x else None for x in (index.lower,index.upper,index.step)))
            else:index=visit(index)
            return bounded(value[index])
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name):
            name=node.func.id
            if node.keywords:raise ExpressionError('Use positional arguments in this exercise.')
            args=[visit(a) for a in node.args]
            if name=='range':
                if not all(type(a) is int for a in args):raise ExpressionError('Range uses integer arguments.')
                return bounded(range(*args))
            if name=='pow':
                if len(args)!=2 or type(args[1]) not in (int,float) or abs(args[1])>12:raise ExpressionError('Use pow with two arguments and a small exponent.')
            if name in functions:return bounded(functions[name](*args))
        raise ExpressionError('Use variables, arithmetic, comparisons, slices or the listed built-in functions. Attributes, imports and arbitrary calls are disabled.')
    try:return visit(tree)
    except ExpressionError:raise
    except (ValueError,TypeError,IndexError,ZeroDivisionError,OverflowError) as error:raise ExpressionError(str(error))

TASKS=[]
for n in (3,4,5):
    rows=[
        ('Arithmetic','Beginner',str(n*2),'Double n using arithmetic.',{'n':n},'n','n * 2'),
        ('Variables','Beginner',str(n+7),'Add seven to x.',{'x':n},'x','x + 7'),
        ('Strings','Beginner',repr('code'),'Take the first four characters of word.',{'word':'codequest'},'word','word[:4]'),
        ('Lists','Intermediate',str(n),'Return the last item of nums.',{'nums':[1,2,n]},'nums','nums[-1]'),
        ('Slicing','Intermediate',repr([n,n+1]),'Return the middle two items of nums.',{'nums':[0,n,n+1,9]},'nums','nums[1:3]'),
        ('Boolean logic','Intermediate','True','Check whether n is greater than zero.',{'n':n},'n','n > 0'),
        ('Functions','Advanced',str(n),'Use abs to return the magnitude of value.',{'value':-n},'value','abs(value)'),
        ('Nested expressions','Advanced',str(n),'Count the digits of number. Use str and len.',{'number':10**(n-1)},'number','len(str(number))'),
        ('List comprehensions','Advanced',repr([0,n,2*n]),'Complete this comprehension: [x * ___ for x in range(3)]. Enter only the missing expression, using factor.',{'factor':n},'factor','factor'),
    ]
    for topic,level,target,prompt,context,required,example in rows:
        TASKS.append(LabTask(f'lab-{topic}-{n}',topic,level,target,prompt,context,required,example,topic=='List comprehensions'))

def evaluate_task(expression,task):
    value=evaluate(expression,task.context)
    if task.comprehension_blank:
        if type(value) not in (int,float) or abs(value)>10000:
            raise ExpressionError('The missing multiplier must be a small number.')
        return [x*value for x in range(3)]
    return value

class LabRound:
    def __init__(self,question):
        self.question=question;self.submitted=False;self.hinted=False;self.actual='';self.error='';self.hints=set()
    def hint(self,kind='concept'):
        if kind not in self.hints:self.hints.add(kind)
        self.hinted=True
        return 'Use '+self.question.required+' and trace its value. Reward: 80 points.'
    def submit(self,answer,timed_out=False):
        if self.submitted:raise ValueError('This round has already been submitted.')
        if not answer.strip() and not timed_out:raise ValueError('Write an expression first.')
        self.submitted=True
        try:
            if timed_out:raise ExpressionError('Time ran out.')
            names={node.id for node in ast.walk(ast.parse(answer,mode='eval')) if isinstance(node,ast.Name)}
            if self.question.required not in names:raise ExpressionError('Use the provided variable '+self.question.required+'.')
            self.actual=repr(evaluate_task(answer,self.question))
            won=self.actual==self.question.target
        except (ExpressionError,SyntaxError) as error:
            self.error=str(error);self.actual='Error';won=False
        return won,(80 if self.hinted else 100) if won else 0
