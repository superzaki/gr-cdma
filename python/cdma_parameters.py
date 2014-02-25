#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2014 Achilleas Anastasopoulos, Zhe Feng.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.

import random
import numpy
from gnuradio import digital
#from gnuradio.digital.utils import tagged_streams


class cdma_parameters:

    def __init__(self):
	"""
 Description:
 This file contains most of the basic design parameters of the cdma system. Users can modify these parameters for their applications. 
 
 header parameters:
 length_tag_name is the length tag key used in the packet header generator. 
 num_tag_name is the num tag key used in the packet header generator. 
 bits_per_header denotes the number of bits per header. 
 header_mod denotes the modulation scheme for header symbols. In this CDMA system, the header is BPSK modulated. 
 header_formatter generates the header by using these above parameters. 
 To avoid evaluation error in symbols per header, bits per header and then symbols per header are automatically adjusted if error occurs. 

 payload parameters:
 payload_bytes_per_frame denotes the number of payload bytes per frame. 
 crc_bytes denotes the number of crc bytes per frame generated by the stream crc32 generator. 
 coded_payload_bytes_per_frame denotes the number of payload bytes per frame after crc coding. 
 payload_mod denotes the modulation scheme for payload symbols. In this CDMA system, the payload is QPSK modulated. 
 coded_payload_symbols_per_frame denotes the number of payload symbols per frame after modulation.
 symbols_per_frame denotes the total number of symbols per frame including both the header and payload symbols. 
 Similarly, to avoid evaluation error in payload symbols per frame, all these payload parameters are automatically adjusted if error occurs.
 
 training parameters:
 training_long denotes the randomly generated training sequence with the same length to symbols_per_frame. 
 training is the adjusted training sequence (maybe shorter than one frame) 
 training_percent is the percentage of power for training at the transmitter. It takes value in (0,100). 
 
 cdma parameters:
 chips_per_symbol denotes the spreading factor which is ratio of the chip rate to baseband symbol rate.
 chips_per_frame denotes the total number of chips per frame. 
 pulse_training denotes the spreading pulse sequence for the training channel. 
 pulse_data denotes the spreading pulse sequence for the data channel. Pulse_training and pulse_data should be orthogonal. 

 timing parameters:
 peak_o_var denotes the output correlation peak over variance value of the matched filter in frequency timing estimator. It is used for the rise and fall threshold factor of the peak detector in the frequency timing estimator. 
 EsN0dBthreshold is the SNR threshold of switching between Acquisition and Tracking mode when auto switch mode is selected. If the estimated SNR is greater than EsN0dBthreshold, the system switches to tracking mode automatically and vice versa. 
 epsilon is a small number used in estimating the SNR to avoid division by zero, etc. 
 n_filt denotes the number of matched filters used in the frequency timing estimator. 
 freqs denotes the center frequencies of the matched filters in the frequency timing estimator. These freqs values are normalized to the symbol rate. 

	"""


print "CDMA PARAMETERS"

length_tag_name = "packet_len"
num_tag_name = "packet_num"


# header info
bits_per_header=12+16+8;
header_mod = digital.constellation_bpsk();
symbols_per_header = bits_per_header/header_mod.bits_per_symbol()
if (1.0*bits_per_header)/header_mod.bits_per_symbol() != symbols_per_header:
  print "Error in evaluating symbols per header; adjusting bits per header"
  bits_per_header=(symbols_per_header+1)*header_mod.bits_per_symbol()
  symbols_per_header = bits_per_header/header_mod.bits_per_symbol()
header_formatter = digital.packet_header_default(bits_per_header,  length_tag_name,num_tag_name,header_mod.bits_per_symbol());


print "bits_per_header=",bits_per_header
print "symbols_per_header=",symbols_per_header
print "\n"


#payload info
payload_bytes_per_frame = 50;
crc_bytes=4;
coded_payload_bytes_per_frame = payload_bytes_per_frame+crc_bytes
payload_mod = digital.constellation_qpsk()
coded_payload_symbols_per_frame = (coded_payload_bytes_per_frame * 8)/payload_mod.bits_per_symbol()
if (coded_payload_bytes_per_frame * 8.0)/payload_mod.bits_per_symbol() != coded_payload_symbols_per_frame:
  print "Error in evaluating payload symbols per frame; adjusting payload bytes per frame"
  k = coded_payload_bytes_per_frame / payload_mod.bits_per_symbol()
  coded_payload_bytes_per_frame = (k+1)*payload_mod.bits_per_symbol()
  payload_bytes_per_frame = coded_payload_bytes_per_frame - crc_bytes
  coded_payload_symbols_per_frame = (coded_payload_bytes_per_frame * 8)/payload_mod.bits_per_symbol()

symbols_per_frame = symbols_per_header + coded_payload_symbols_per_frame

print "payload_bytes_per_frame=", payload_bytes_per_frame
print "coded_payload_bytes_per_frame=", coded_payload_bytes_per_frame
print "coded_payload_symbols_per_frame=", coded_payload_symbols_per_frame
print "symbols_per_frame=", symbols_per_frame
print "\n"

# training info
numpy.random.seed(666)
training_long = (2*numpy.random.randint(0,2,symbols_per_frame)-1+0j)

training_length = symbols_per_frame; # number of non-zero training symbols
if training_length > symbols_per_frame:
  print "Error in training length evaluation"
  training_length = symbols_per_frame
training=training_long[0:training_length];
training_percent = 50; # percentage of transmitted power for training
print "training_length =", training_length
print "\n"

# cdma parameters
chips_per_symbol=8;	
chips_per_frame = chips_per_symbol*symbols_per_frame
pulse_training = numpy.array((1,1,1,1,-1,1,1,-1))+0j
pulse_data =numpy.array((-1,1,-1,1,-1,-1,-1,-1))+0j

#timing parameters
peak_o_var = training_percent*symbols_per_frame*chips_per_symbol/(100+training_percent) #peak over variance for matched filter output 
EsN0dBthreshold = 10; 	# the threshold of switching from Acquisition to Tracking mode automatically.
epsilon = 1e-6; 	#tolerance
n_filt = 51;		# numbers of filters for the frequency/timing acquisition block
df1=1.0/(2*symbols_per_frame*chips_per_symbol) # Normalized (to chip rate) frequency interval due to training length
pll_loop_bw=0.005 # normailzed to symbol rate
df2=pll_loop_bw/chips_per_symbol # Normalized (to chip rate) frequency interval due to PLL
#df=max(df1,df2) # either a different frequency branch or the PLL will correct for it
df=df1
freqs=[(2*k-n_filt+1)*df/2 for k in range(n_filt)];	#Normalized frequency list.

#print "Normalized frequency interval = max(", df1, " , ", df2, ")=", df
print "Normalized frequency interval = ", df
print "Normalized frequency unsertainty range = [", freqs[0], " , ", freqs[-1], "]"
