"""Actual OTTYG bytecode interpreted in Python, with modeled NBT and scheduler.
This is NOT JVM/Mixin execution or validation of a real Minecraft world.
"""
from pathlib import Path
import copy, hashlib, io, json, sys, zipfile
import argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--trees262',required=True,type=Path)
parser.add_argument('--trees263',required=True,type=Path)
parser.add_argument('--report',type=Path)
args=parser.parse_args()
from jawa.cf import ClassFile
class Compound(dict):pass
class ListTag(list):pass
class IntArray(list):pass
class MissingValue(Exception):pass
class Obj:
 def __init__(self,kind,**fields):self.kind=kind;self.__dict__.update(fields)
def invoke(owner,name,r,args):
 if name=='<init>':
  if owner.endswith('/IntArrayTag'):r.value=IntArray(args[0])
  elif owner.endswith('/BlockPos'):r.value=tuple(args)
  elif owner.endswith('/CompoundTag'):r.value=Compound()
  elif owner.endswith('/ListTag'):r.value=ListTag()
  else:raise AssertionError((owner,name))
  return None
 if name=='getScheduledRandomTicks':return r.ticks
 if name=='getReturnValue':return r.value
 if name=='structureData':return r.structureData
 if isinstance(r,Obj) and r.kind in ['CompoundTag','ListTag','IntArrayTag','BlockPos']:r=r.value
 if name=='isEmpty':return not r
 if name=='iterator':return Obj('iterator',items=r,index=0)
 if name=='hasNext':return r.index<len(r.items)
 if name=='next':v=r.items[r.index];r.index+=1;return v
 if name in ['getX','getY','getZ']:return r[['getX','getY','getZ'].index(name)]
 if name=='add':r.append(args[0]);return True
 if name=='put':old=r.get(args[0]);r[args[0]]=args[1];return old
 if name=='contains':return args[0] in r
 if name in ['getCompound','getList']:
  v=r.get(args[0]);u=v.value if isinstance(v,Obj) else v
  return Obj('optional',value=v if isinstance(u,Compound if name=='getCompound' else ListTag) else None)
 if name=='orElseThrow':
  if r.value is None:raise MissingValue('No value present')
  return r.value
 if name=='getAsIntArray':return r
 raise AssertionError(('unsupported call',owner,name))
def run(cf,method,local,patch=False):
 ins=list(method.code.disassemble());positions={i.pos:n for n,i in enumerate(ins)};stack=[];pc=0;steps=0
 while True:
  steps+=1;assert steps<100000;i=ins[pc];op=i.mnemonic;args=[v.value for v in i.operands];pc+=1
  if op.startswith('aload'):
   slot=int(op[-1]) if '_' in op else args[0]
   if patch and i.pos==41:slot=7
   stack.append(local[slot])
  elif op.startswith('astore'):local[int(op[-1]) if '_' in op else args[0]]=stack.pop()
  elif op=='getfield':stack.append(getattr(stack.pop(),cf.constants.get(args[0]).name_and_type.name.value))
  elif op=='ldc':stack.append(cf.constants.get(args[0]).string.value)
  elif op=='checkcast':pass
  elif op in ['ifeq','ifne']:
   if bool(stack.pop())==(op=='ifne'):pc=positions[i.pos+args[0]]
  elif op=='goto':pc=positions[i.pos+args[0]]
  elif op=='new':stack.append(Obj(cf.constants.get(args[0]).name.value.rsplit('/',1)[1]))
  elif op=='dup':stack.append(stack[-1])
  elif op=='pop':stack.pop()
  elif op.startswith('iconst_'):stack.append(int(op[-1]))
  elif op=='newarray':stack.append([0]*stack.pop())
  elif op=='iastore':v=stack.pop();index=stack.pop();stack.pop()[index]=v
  elif op=='iaload':index=stack.pop();stack.append(stack.pop()[index])
  elif op.startswith('invoke'):
   ref=cf.constants.get(args[0]);owner=ref.class_.name.value;name=ref.name_and_type.name.value;desc=ref.name_and_type.descriptor.value
   types=desc[1:desc.index(')')];count=0;n=0
   while n<len(types):
    while types[n]=='[':n+=1
    n=types.index(';',n)+1 if types[n]=='L' else n+1;count+=1
   values=[stack.pop() for _ in range(count)][::-1];r=stack.pop();result=invoke(owner,name,r,values)
   if not desc.endswith('V'):stack.append(result)
  elif op=='return':return
  else:raise AssertionError(('unsupported opcode',op))
def unwrap(v):
 if isinstance(v,Obj):return unwrap(v.value)
 if isinstance(v,dict):return {k:unwrap(x) for k,x in v.items()}
 if isinstance(v,list):return [unwrap(x) for x in v]
 return v
rows=[]
for target,path in [('26.2',args.trees262),('26.3',args.trees263)]:
 with zipfile.ZipFile(path) as jar:
  raw=jar.read('dev/corgitaco/ohthetreesyoullgrow/mixin/chunk/MixinChunkSerializer.class');cf=ClassFile(io.BytesIO(raw));meta=json.loads(jar.read('fabric.mod.json'))
 read=next(m for m in cf.methods if m.name.value=='readScheduledRandomTicks');write=next(m for m in cf.methods if m.name.value=='writeScheduledRandomTicks')
 assert write.access_flags.acc_static and not read.access_flags.acc_static
 ops=list(read.code.disassemble());assert ops[17].pos==41 and ops[17].mnemonic=='aload' and ops[17].operands[0].value==6
 assert ops[12].mnemonic=='astore' and ops[12].operands[0].value==7
 assert cf.constants.get(ops[19].operands[0].value).name_and_type.name.value=='getList'
 original=read.code._code;fixed=bytearray(original);assert fixed[41:43]==b'\x19\x06';fixed[42]=7
 assert [i for i,(a,b) in enumerate(zip(original,fixed)) if a!=b]==[42]
 cases=[]
 for points in [[],[(288,72,-608)],[(-848,-60,-128),(0,319,0),(110,80,-25),(110,80,-25)]]:
  scheduler=Obj('scheduler',ticks=[Obj('BlockPos',value=p) for p in points]);saved=Obj('serialized',structureData=Compound(unrelated=Compound(keep='unchanged')))
  run(cf,write,{0:None,1:scheduler,2:Obj('callback',value=saved)})
  before=copy.deepcopy(unwrap(saved.structureData));baseline=Obj('scheduler',ticks=[])
  try:run(cf,read,{0:saved,5:Obj('callback',value=baseline)})
  except MissingValue:assert points
  else:assert not points
  for cycle in range(3):
   restored=Obj('scheduler',ticks=[]);run(cf,read,{0:saved,5:Obj('callback',value=restored)},patch=True)
   assert [p.value for p in restored.ticks]==points and unwrap(saved.structureData)==before
   next_saved=Obj('serialized',structureData=Compound(unrelated=Compound(keep='unchanged')))
   run(cf,write,{0:None,1:restored,2:Obj('callback',value=next_saved)})
   assert unwrap(next_saved.structureData)==before;saved=next_saved
  cases.append({'ticks':len(points),'reopen_cycles':3,'status':'PASS'})
 for data in [Compound(),Compound(ohthetreesyoullgrow=Compound()),Compound(ohthetreesyoullgrow=Compound(scheduled_random_ticks=ListTag()))]:
  restored=Obj('scheduler',ticks=[]);before=copy.deepcopy(data)
  run(cf,read,{0:Obj('serialized',structureData=data),5:Obj('callback',value=restored)},patch=True)
  assert not restored.ticks and data==before
 bad=Compound(ohthetreesyoullgrow=Compound(scheduled_random_ticks='invalid'))
 try:run(cf,read,{0:Obj('serialized',structureData=bad),5:Obj('callback',value=Obj('scheduler',ticks=[]))},patch=True)
 except MissingValue:pass
 else:raise AssertionError('Malformed data silently accepted')
 rows.append({'minecraft':target,'ottyg':meta['version'],'jar_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),'serializer_sha256':hashlib.sha256(raw).hexdigest(),'actual_bytecode_delta':{'offset':42,'old_local':6,'new_local':7},'cases':cases,'absent_empty_tags':'PASS','malformed_tag_not_suppressed':'PASS'})
report={'status':'PASS','scope':'Python interpretation of actual upstream serializer bytecode, modeled NBT/scheduler calls. Not JVM/Mixin execution or a real-world test.','targets':rows}
if args.report:args.report.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
