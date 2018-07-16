from numpy import *
dtype('int16') # using array-scalar type
# dtype('int16')
dtype([('f1', 'int16')]) # record, 1 field named 'f1', containing int16
# dtype([('f1', '<i2')])
dtype([('f1', [('f1', 'int16')])]) # record, 1 field named 'f1' containing a record that has 1 field.
# dtype([('f1', [('f1', '<i2')])])
dtype([('f1', 'uint'), ('f2', 'int32')]) # record with 2 fields: field 1 contains an unsigned int, 2nd field an int32
# dtype([('f1', '<u4'), ('f2', '<i4')])
dtype([('a','f8'),('b','S10')]) # using array-protocol type strings
# dtype([('a', '<f8'), ('b', '|S10')])
dtype("i4, (2,3)f8") # using comma-separated field formats. (2,3) is the shape
# dtype([('f0', '<i4'), ('f1', '<f8', (2, 3))])
dtype([('hello',('int',3)),('world','void',10)]) # using tuples. int is fixed-type: 3 is shape; void is flex-type: 10 is size.
# dtype([('hello', '<i4', 3), ('world', '|V10')])
dtype(('int16', {'x':('int8',0), 'y':('int8',1)})) # subdivide int16 in 2 int8, called x and y. 0 and 1 are the offsets in bytes
# dtype(('<i2', [('x', '|i1'), ('y', '|i1')]))
dtype({'names':['gender','age'], 'formats':['S1',uint8]}) # using dictionaries. 2 fields named 'gender' and 'age'
# dtype([('gender', '|S1'), ('age', '|u1')])
dtype({'surname':('S25',0),'age':(uint8,25)}) # 0 and 25 are offsets in bytes
# dtype([('surname', '|S25'), ('age', '|u1')])

a = dtype('int32')
a
# dtype('int32')
a.type # type object
# <type 'numpy.int32'>
a.kind # character code (one of 'biufcSUV') to identify general type
# 'i'
a.char # unique char code of each of the 21 built-in types
# 'l'
a.num # unique number of each of the 21 built-in types
# 7
a.str # array-protocol typestring
# '<i4'
a.name # name of this datatype
# 'int32'
a.byteorder # '=':native, '<':little endian, '>':big endian, '|':not applicable
# '='
a.itemsize # item size in bytes
# 4
a = dtype({'surname':('S25',0),'age':(uint8,25)})
list(a.fields.keys())
# ['age', 'surname']
list(a.fields.values())
# [(dtype('uint8'), 25), (dtype('|S25'), 0)]
a = dtype([('x', 'f4'),('y', 'f4'), # nested field
    ('nested', [('i', 'i2'),('j','i2')])])
a.fields['nested'] # access nested fields
# (dtype([('i', '<i2'), ('j', '<i2')]), 8)
a.fields['nested'][0].fields['i'] # access nested fields
# (dtype('int16'), 0)
a.fields['nested'][0].fields['i'][0].type
# <type 'numpy.int16'>

