import subprocess
import os
from six import string_types
import numpy

# SLHA parser
# by Florian Staub (florian.staub@gmail.com)

#----------------------------------------------------------
# SLHA Class
#----------------------------------------------------------

class SLHA():
    def __init__(self):
      self.blocks={}
      self.br={}
      self.widths={}
      self.br1L={}
      self.widths1L={}
      self.xsections={}

      self.block_name=None
      self.entries={}
      self.reading_block=False
      self.reading_decay=False
      self.reading_xsection=False
      self.reading_hb_fermion=False
      self.reading_hb_boson=False
      self.decay1L=False
      self.decay_part=0

    # return wdith and BR
    def BR(self,init,final):
      # frozenset: make sure that the final states are order-less
      return self.br[init][tuple(sorted(final))]

    def Width(self,pdg):
      return self.widths[pdg]


    # return value of a parameter defined by block and entry or the width or an BR
    def Value(self,block,number):
      if block == 'WIDTH':
        return self.widths[number]
      elif block == 'BR':
        return self.br[number[0]][tuple(sorted(number[1]))]
      elif block == 'WIDTH1L':
        return self.widths1L[number]
      elif block == 'BR1L':
        return self.br1L[number[0]][tuple(sorted(number[1]))]
      elif block == 'XSECTION':
        xs=self.xsections[tuple(number)]
        return [[x,xs[x]] for x in xs.keys()]
      else:
        return self.blocks[block.upper()][str(number)[1:-1].replace(" ", "")]

    def start_decay(self,li):
      parsed=list(filter(None,li.split(' ')))
      self.decay1L = li.upper().startswith("DECAY1L")
      self.decay_part=int(parsed[1])
      if self.decay1L:
         self.widths1L[self.decay_part]=float(parsed[2])
      else:
         self.widths[self.decay_part]=float(parsed[2])
      self.entries={}
      self.reading_block, self.reading_decay,self.reading_xsection = False, True, False


    def start_block(self,li):
      self.block_name=(list(filter(None,li.split(' ')))[1]).upper()
      self.entries={}
      self.reading_block, self.reading_decay,self.reading_xsection = True, False, False
      self.reading_hb_boson = self.block_name == "HIGGSBOUNDSINPUTHIGGSCOUPLINGSBOSONS"
      self.reading_hb_fermion = self.block_name =="HIGGSBOUNDSINPUTHIGGSCOUPLINGSFERMIONS"

    def start_xsection(self,li):
          parsed=list(filter(None,li.split(' ')))
          if "#" in parsed: parsed=parsed[:parsed.index("#")] # remove comments
          self.xs_head = tuple([float(parsed[1]),tuple([int(parsed[2]),int(parsed[3])]),tuple([int(parsed[-2]),int(parsed[-1])])])
          self.entries={}
          self.reading_block, self.reading_decay,self.reading_xsection = False, False, True


    # store the information once a block is completely parsed
    def flush(self):
        if len(self.entries)>0:
         if self.reading_block:
            self.blocks[self.block_name]=self.entries
         if self.reading_decay:
            if self.decay1L:
                self.br1L[self.decay_part]=self.entries
            else:
                self.br[self.decay_part]=self.entries
         if self.reading_xsection:
            self.xsections[self.xs_head]=self.entries

#----------------------------------------------------------
# Reading
#----------------------------------------------------------


# now the main function to read the SLHA file
def read(file,separator=None,verbose=False):
  spc = SLHA()
  if separator is not None:
        all_files=[]
        count=1

  with open(file) as infile:
    for line in infile:
       li=line.strip().upper()

       if li.startswith("#"):
          continue

       if separator is not None:
            if li.startswith(separator):
                spc.flush()
                if len(spc.blocks.keys())>0 or len(spc.widths.keys())>0:
                  all_files.append(spc)

                # start next point
                spc = SLHA()
                count=count+1
                if verbose: print("Read spc file:",count)
                continue

       # New block started
       if li.startswith("BLOCK"):
            spc.flush() # store information which was read
            spc.start_block(li)
       elif li.startswith("DECAY"):
            spc.flush() # store information which was read
            spc.start_decay(li)
       elif li.startswith("XSECTION"):
                    spc.flush() # store information which was read
                    spc.start_xsection(li)

          # Reading and parsing values
       else:
            parsed=list(filter(None,li.split(' ')))
            if "#" in parsed: parsed=parsed[:parsed.index("#")] # remove comments
            if spc.reading_block:
              if spc.reading_hb_fermion:
                 spc.entries[",".join(parsed[3:])]=[float(parsed[0]),float(parsed[1])]
              elif spc.reading_hb_boson:
                 spc.entries[",".join(parsed[2:])]=float(parsed[0])
              else:
                 # Value might be a string like in SPINFO block
                 try:
                     value=float(parsed[-1])
                 except:
                      value=parsed[-2]
                 spc.entries[",".join(parsed[0:-1])]=value

            if spc.reading_decay:
                spc.entries[tuple(sorted(eval("["+",".join(parsed[2:])+"]")))]=float(parsed[0])

            if spc.reading_xsection:
                spc.entries[tuple(eval("["+",".join(parsed[0:-2])+"]"))]=float(parsed[-2])

  spc.flush()  # save the very last block in the file

  if verbose:
        print("Read %i blocks and %i decays" % (len(spc.blocks),len(spc.br)))
  if separator is None:
        return spc
  else:
        if len(spc.entries)>0: all_files.append(spc)
        return all_files


# wrapper for faster read-in of multiple files
# squeeze the file (just keeping the necessary entries) to make the reading more efficient
# example: read_small_spc(filename,["# m0","# m12","# relic"],separator="ENDOF")
def read_small(file,entries,sep):
    if entries==None:
        out=read(file,separator=sep)
    else:
        string="--regexp=\""+sep+"\" --regexp=\"Block\" "
        for i in entries:
            string=string+"--regexp=\""+i+"\" "
        subprocess.call("rm temp.spc",shell=True)
        subprocess.call("cat "+file+" | grep -i "+string+" > temp_read_small.spc",shell=True)
        out=read("temp_read_small.spc",separator=sep)
        subprocess.call("rm temp_read_small.spc",shell=True)

    return out

# # read all files from a directory
# def read_dir(dir,entries=None):
#     subprocess.call("rm temp.spc",shell=True)
#     if entries != None:
#        string="--regexp=\""+"THEEND"+"\" --regexp=\"Block\" "
#        for i in entries:
#            string=string+"--regexp=\""+i+"\" "
#
#     for filename in os.listdir(dir):
#         # print(dir+filename)
#         if entries != None:
#             subprocess.call("cat "+dir+"/"+filename+" | grep "+string+" >> temp.spc",shell=True)
#         else:
#             subprocess.call("cat "+dir+"/"+filename+" >> temp.spc",shell=True)
#         subprocess.call("echo \"THEEND\" >> temp.spc",shell=True)
#     out=read("temp.spc",separator="THEEND")
#     subprocess.call("rm temp.spc",shell=True)
#     return out

#
# def read_dir_list(dir,entries):
#      subprocess.call("rm temp.spc",shell=True)
#      string=""
#      for i in entries:
#          string=string+"--regexp=\""+i+"\" "
#
#      for filename in os.listdir(dir):
#         subprocess.call("cat "+dir+"/"+filename+" | grep "+string+" |  sed  -ne 's/.*[ ]*\\([0-9]\\.[0-9eE\\+\\-]*\\)[ ]*.*/\\1/p' | sed -e ':a;N;$!ba;s/\\n/,/g' >> temp.spc",shell=True)
#
#      return numpy.loadtxt("temp.spc", delimiter=',')


def read_dir(dir,entries=None):
    subprocess.call("rm temp_read_dir.spc",shell=True)
    subprocess.check_call("cat "+dir+"/* > temp_read_dir.spc",shell=True)
    out=read_small("temp_read_dir.spc",entries,"BLOCK SPINFO")
    subprocess.call("rm temp_read_dir.spc",shell=True)

    return out




#----------------------------------------------------------
# Writing
#----------------------------------------------------------

def write(blocks,file):
    with open(file,'w+') as f:
        for b in blocks:
            write_block_head(b,f)
            write_block_entries(blocks[b],f)

def write_block_entries(values,file):
       for v in values.keys():
           file.write(' %s %10.4e # \n' % (v, float(values[v])))


def write_les_houches(block,values,point,file):
        write_block_head(block,file)
        write_block_numbers(values,point,file)

def write_block_head(name,file):
        file.write("Block "+name.upper()+" # \n")

def write_block_numbers(values,Variable,file):
       for v in values.keys():
        # if type(values[v]) is string_types:
         if isinstance(values[v], string_types): # to be 2 and 3 compatible
           file.write(' %s %10.4e # \n' % (v,  float(eval(values[v]))))
         else:
           file.write(' %s %10.4e # \n' % (v, float(values[v])))
