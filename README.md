# xSLHA
``xSLHA`` is a ``python`` parser for files written in the SLHA format. It is optimised for fast reading of a large sample of files.

## Installation
The package can be installed via
```
pip install xslha
```
and is loaded in python by 
```
import xslha
```

## Reading a single spectrum file
Reading a spectrum file ``file`` and stroing the information in a class object ``spc`` is done via the command
```
spc=xslha.read(file)
```
One has afterwards access to the different information by using the ``Value`` command, e.g
```
print("tan(beta): ",spc.Value('MINPAR',[3]))
print("T_u(3,3): ",spc.Value('TU',[3,3]))
print("m_h [GeV]: ",spc.Value('MASS',[25]))
print("Gamma(h) [GeV]: ",spc.Value('WIDTH',25))
print("BR(h->W^+W^-): ",spc.Value('BR',[25,[-13,13]]))
print("Sigma(pp->N1 N1,Q=8TeV): ",spc.Value('XSECTION',[8000,(2212,2212),(1000021,1000021)]))
```
produces the following output
```
tan(beta):  16.870458
T_u(3,3):  954.867627
m_h [GeV]:  117.758677
Gamma(h) [GeV]:  0.00324670136
BR(h->W^+W^-):  0.000265688227
Sigma(pp->N1 N1,Q=8TeV): [[(0, 2, 0, 0, 0, 0), 0.00496483158]]
```
Thus, the conventions are:
* for information given in the different SLHA blocks is returned by using using the name of the block as input as well as the numbers in the block as list
* the widths of particles are returned via the keyword ``WIDHT`` and the pdg of the particle
* for branching ratios, the keyword ``BR``is used together with a nested list which states the pdg of the decay particle as well as of the final states
* for cross-sections the keyword ``XSECTION`` is used together with a nested list which states the center-of-mass energy and the pdgs of the initial/final states. The result is a list containing all calculated cross-sections for the given options for the renormalisation scheme, the QED & QCD order, etc. (see the SLHA recommendations for details). 

Another possibility to access the information in the spectrum file is to look at the different dictionaries
```
spc.blocks
spc.widths
spc.br
spc.xsctions
```
which contain all information

## Reading all spectrum files from a directory
In order to read several spectrum files located in a directory ``dir``, one can make use of the command
```
list_spc=xslha.read_dir(dir)
```
This generates a list ``list_spc`` where each entry corresponds to one spectrum. Thus, one can for instance use 
```
[[x.Value('MINPAR',[1]),x.Value('MASS',[25])] for x in list_spc]
```
to extract the input for a 2D-scatter plot. 

## Fast read-in of many files
Reading many spectrum files can be time consuming. However, many of the information which is given in a SLHA file is often not needed for a current study. Therefore, one can speed up the reading by extracting first all relevant information. This generates smaller files which are faster to read in. This can be done via the optional argument ``entries`` for ``read_dir``:
```
list_spc_fast=xslha.read_dir("/home/$USER/Documents/spc1000",entries=["# m0","# m12","# hh_1"])`
```
``entries`` defines a list of strings which can be used to extract the necessary lines from the SLHA file by using ``grep``. The speed improvement can be easily an order of magnitude if only some entries from a SLHA file are actually needed.

### Speed
The impact of this optimisation for reading 1000 files is as follows:
```
%%time
list_spc=xslha.read_dir("/home/$USER/Documents/spc1000")

CPU times: user 5.05 s, sys: 105 ms, total: 5.15 s
Wall time: 5.51 s
```
compared to 
```
%%time
list_spc_fast=xslha.read_dir("/home/$USER/Documents/spc1000",entries=["# m0","# m12","# hh_1"])

CPU times: user 147 ms, sys: 132 ms, total: 280 ms
Wall time: 917 ms
```
One can also compares this with other available python parser:
* ``pylha``:
```
%%time
all_spc=[]
for filename in os.listdir("/home/$USER/Documents/spc1000/"): 
  with open("~/Documents/spc1000/"+filename) as f:
    input=f.read()
    all_spc.append(pylha.load(input))
    
CPU times: user 21.5 s, sys: 174 ms, total: 21.7 s
Wall time: 21.7 s    
```
* ``pyslha``{
```
%%time
all_spc=[]
for filename in os.listdir("/home/$USER/Documents/spc1000/"): 
    all_spc.append(pyslha.read(("/home/$USER/Documents/spc1000/"+filename)))

CPU times: user 13.3 s, sys: 152 ms, total: 13.5 s
Wall time: 13.5 s
 ```

## Reading spectra stored in one file
Another common approach for saving spectrum files is to produce one huge file in which the different spectra are separated by a keyword. ``xSLHA`` can read such files by setting the optional argument ``separator`` for ``read``:
```
list_spc=xslha.read(file,separator=keyword)
```
In order to speed up the reading of many spectra also in this case, it is possible to define the entries as well which are need:
```
list_spc=xslha.read(file,separator=keyword,entries=list)
```
In this case``xSLHA`` will produce first a smaller spectrum file using ``cat`` and ``grep``. For instance, in order to read efficiently files produced with [``SSP``](https://sarah.hepforge.org/SSP), one can use:
```
list_spc=xslha.read("SpectrumFiles.spc",separator="ENDOFPARAMETERFILE",entries=["# m0", "# m12", "# hh_1"])
```

## Special blocks
There are some programs which use blocks that are not supported by the official SLHA conventions:
* [``HiggsBounds``](https://higgsbounds.hepforge.org/) expects the effective coupling ratios in blocks ``HIGGSBOUNDSINPUTHIGGSCOUPLINGSBOSONS`` and ``HIGGSBOUNDSINPUTHIGGSCOUPLINGSFERMIONS`` which are differently order compared to other blocks (first the numerical entries are stated before the PDGs of the involved particles follow)
* [``SPheno``](spheno.hepforge.org) version generated by [``SARAH``](sarah.hepforge.org) can calculate one-loop corrections to the decays. The results are given in the blocks ``DECAY1L`` which appear in parallel to ``DECAY`` containing the standard calculation. ``xSLHA`` will distinguish these cases when reading the file and offer the two following options for ``Values`` in addtion:
```
spc.Values('WIDTH1L',1000022)
spc.Values('BR1L',[1000023,[25,1000022]])
```

## Writing files
Files in the SLHA format can be written via
```
xslha.write(blocks,file)
```
where it might be the best to use ordered dictionaries to define the blocks and the values in the blocks. For instance 
```
import collections
out_blocks=collections.OrderedDict([
              ('MODSEL',collections.OrderedDict([('1', 1), ('2', 2),('6',0)])),
              ('MINPAR',collections.OrderedDict([('1', 1000.),('2', 2000),('3',10),('4',1),('5',0)]))
])
xslha.write(out_blocks,"/home/$USER/Documents/LH.in")
```

