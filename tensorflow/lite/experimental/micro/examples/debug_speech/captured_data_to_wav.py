# Copyright 2018 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Converts values pulled from the microcontroller into audio files."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import argparse
import os
import os.path
import re
import struct
# import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf

def check_file_existence(x):
  if not os.path.isfile(x):
    # Argparse uses the ArgumentTypeError to give a rejection message like:
    # error: argument input: x does not exist
    raise argparse.ArgumentTypeError('{0} does not exist'.format(x))
  return x



def new_data_to_array(fn):
  vals = []
  with open(fn) as f:
    for n, line in enumerate(f):
      if n != 0:
        vals.extend([int(v, 16) for v in line.split()])
  b = ''.join(map(chr, vals))
  y = struct.unpack('<' + 'h' * int(len(b) / 2), b)

  return y



def parse_file(inputfile, size):
 
  data = None
  bytes_written = 0
  frame_start = False
  frame_stop = False
  frame_list = list()

  # collect all pixel data into an int array
  for line in inputfile:
    
    #print("*****\n",line,"\n-----")
    if line == '+++ frame +++\n':
      frame_start = True
      data = np.zeros(size, dtype=np.int16)
      bytes_written = 0
      print("Found Start\n")
      continue
    elif line == '--- frame ---\n':
      frame_stop = True

    if frame_start and not frame_stop:
      linelist = re.findall(r"-?[0-9]+", line)
      #print(len(linelist))
      if len(linelist) != 17:
        # drop this frame
        #frame_start = False
        continue
      for item in linelist[1:]:
        data[bytes_written] = int(item, base=10)
        bytes_written += 1

    elif frame_stop:
      print("Bytes written: ", bytes_written, " Size: ", size)
      if bytes_written == size:
        frame_list.append(data)
        frame_start = False
        frame_stop = False

  return frame_list


def main():
  parser = argparse.ArgumentParser(
      description='This program converts raw data from HM01B0 to a bmp file.')

  parser.add_argument(
      '-i',
      '--input',
      dest='inputfile',
      required=True,
      help='input file',
      metavar='FILE',
      type=check_file_existence)



  args = parser.parse_args()

  #data = 'captured_data.txt'
  #values = np.array(new_data_to_array(data)).astype(float)

  ## plt.plot(values, 'o-')
  ## plt.show(block=False)

  #wav = values / np.max(np.abs(values))*/
  #sf.write('captured_data.wav', wav, 16000)


  frame_list = parse_file(open(args.inputfile), 16000)
  print(frame_list)
  wav = frame_list / np.max(np.abs(frame_list))
  print(wav)
  sf.write('captured_data.wav', wav[0], 16000)
  

if __name__ == '__main__':
  main()


