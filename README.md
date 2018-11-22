# xSLHA

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
print("\Gamma(h) [GeV]: ",spc.Value('WIDTH',25))
print("BR(h->W^+W^-): ",spc.Value('BR',[25,[-13,13]]))
```
produces the following output
```
tan(beta):  16.870458
T_u(3,3):  954.867627
m_h [GeV]:  117.758677
\\Gamma(h) [GeV]:  0.00324670136
BR(h->W^+W^-):  0.000265688227
```
Thus, the conventions are:
* for information given in the different SLHA blocks is returned by using using the name of the block as input as well as the numbers in the block as list
* the widths of particles are returned via the keyword ``WIDHT`` and the pdg of the particle
* for branching ratios, the keyword ``BR``is used together with a nested list which states the pdg of the decay particle as well as of the final states

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
list_spc_fast=xslha.read_dir("~/Documents/spc1000",entries=["# m0","# m12","# hh_1"])`
```
``entries`` defines a list of strings which can be used to extract the necessary lines from the SLHA file by using ``grep``. The speed improvement can be easily an order of magnitude if only some entries from a SLHA file are actually needed.





