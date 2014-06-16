# -*- coding: utf-8 -*-
"""
This is a python implementation of the Ultra High Entropy Pseudo Random Number Generator developed by
Steve Gibson of grc.com.  Steve was kind enough to release his javascript implementation as public domain
so I wish to do the same for my hacked together python version.

============================================================================
LICENSE AND COPYRIGHT:  THIS CODE IS HEREBY RELEASED INTO THE PUBLIC DOMAIN
Gibson Research Corporation releases and disclaims ALL RIGHTS AND TITLE IN
THIS CODE OR ANY DERIVATIVES. Anyone may be freely use it for any purpose.
============================================================================
This is GRC's cryptographically strong PRNG (pseudo-random number generator)
for JavaScript. It is driven by 1536 bits of entropy, stored in an array of
48, 32-bit JavaScript variables.  Since many applications of this generator,
including ours with the "Off The Grid" Latin Square generator, may require
the deteriministic re-generation of a sequence of PRNs, this PRNG's initial
entropic state can be read and written as a static whole, and incrementally
evolved by pouring new source entropy into the generator's internal state.
----------------------------------------------------------------------------
ENDLESS THANKS are due Johannes Baagoe for his careful development of highly
robust JavaScript implementations of JS PRNGs.  This work was based upon his
JavaScript "Alea" PRNG which is based upon the extremely robust Multiply-
With-Carry (MWC) PRNG invented by George Marsaglia. MWC Algorithm References:
http://www.GRC.com/otg/Marsaglia_PRNGs.pdf
http://www.GRC.com/otg/Marsaglia_MWC_Generators.pdf
----------------------------------------------------------------------------
The quality of this algorithm's pseudo-random numbers have been verified by
multiple independent researchers. It handily passes the fermilab.ch tests as
well as the "diehard" and "dieharder" test suites.  For individuals wishing
to further verify the quality of this algorithm's pseudo-random numbers, a
256-megabyte file of this algorithm's output may be downloaded from GRC.com,
and a Microsoft Windows scripting host (WSH) version of this algorithm may be
downloaded and run from the Windows command prompt to generate unique files
of any size:
The Fermilab "ENT" tests: http://fourmilab.ch/random/
The 256-megabyte sample PRN file at GRC: https://www.GRC.com/otg/uheprng.bin
The Windows scripting host version: https://www.GRC.com/otg/wsh-uheprng.js
----------------------------------------------------------------------------
Qualifying MWC multipliers are: 187884, 686118, 898134, 1104375, 1250205,
1460910 and 1768863. (We use the largest one that's < 2^21)
============================================================================
"""
import random
import math

class _Mash:
    """
    ============================================================================
    This is based upon Johannes Baagoe's carefully designed and efficient hash
    function for use with JavaScript.  It has a proven "avalanche" effect such
    that every bit of the input affects every bit of the output 50% of the time,
    which is good.    See: http://baagoe.com/en/RandomMusings/hash/avalanche.xhtml
    ============================================================================
    """
    def __init__(self):
        self.n = 0xefc8249d

    def masher(self, data=None):
	if (data): 
	    data = str(data)
            for i in range(0, len(data)):
                self.n += ord(data[i])
                h = 0.02519603282416938 * self.n
                self.n = h // pow(2, 0) 
                h -= self.n 
                h *= self.n 
                self.n = h // pow(2, 0) 
                h -= self.n 
                self.n += h * 0x100000000
	    return (self.n // pow(2, 0)) * 2.3283064365386963e-10
	else:
            self.n = 0xefc8249d 	

class UHEPRNG:
    def __init__(self):
        """
        arguments: none
        When our "uheprng" is initially invoked our PRNG state is initialized from
        pythons own PRNG. This is okay since although its generator might not
        be wonderful, it's useful for establishing large startup entropy for our usage.
        """
        self.o = 48 
        self.c = 1
        self.p = self.o
        self.s = list()
        self.mash = _Mash()
        for i in range(0, self.o):
            self.s.append(self.mash.masher(random.random))
            
    def random(self, range):
        """
        arguments: int range
        returns: a random int in the range 0 to range-1
        This EXPORTED function is the default function returned by this library.
        The values returned are integers in the range from 0 to range-1. We first
        obtain two 32-bit fractions (from rawprng) to synthesize a single high
        resolution 53-bit prng (0 to <1), then we multiply this by the caller's
        "range" param and take the "floor" to return a equally probable integer.
        """
        return int(math.floor(range * (self._rawprng() + (self._rawprng() * (0x200000 | 0)) * 1.1102230246251565e-16)))

    def string(self,count):
        """
        arguments: int count of printable chars required.
        returns: a string of chars count chracters long
        This EXPORTED function 'string(n)' returns a pseudo-random string of
        'n' printable characters ranging from chr(33) to chr(126) inclusive.
        """
        string=str()
        for i in range(0,count):
            string+=(chr(33+self.random(94)))
        return string;
    
    def bytes(self,count):
        """
        arguments: int count of bytes required.
        returns: a string of random bytes on the range 0x00 to 0xff
        This EXPORTED function 'bytes(n)' returns a pseudo-random string of
        'n' bytes ranging from chr(0) to chr(255) inclusive.
        """
        string=str()
        for i in range(0,count):
            string+=chr(self.random(256))
        return string;
            
                      
    def _hashString(self,inStr):
        """
        """
        inStr = inStr.strip()
        self.mash.masher(inStr)
        for i in range(0,len(inStr)):
            k = ord(inStr[i])
            for j  in range(0,self.o):
                self.s[j] -= self.mash.masher(k)
                if self.s[j] < 0:
                    self.s[j] += 1
            

    def _initState(self):
        """
        """
        self.mash.masher()
        for i in range(0, self.o):
            self.s[i]=self.mash.masher(' ')
        self.c = 1
        self.p = self.o

    def _rawprng(self):
        """
        This PRIVATE (internal access only) function is the heart of the multiply-with-carry
        (MWC) PRNG algorithm. When called it returns a pseudo-random number in the form of a
        32-bit JavaScript fraction (0.0 to <1.0) it is a PRIVATE function used by the default
        [0-1] return function, and by the random 'string(n)' function which returns 'n'
        characters from 33 to 126.
        """
        self.p += 1 
        if self.p >= self.o:
			self.p = 0
        t = 1768863 * self.s[self.p] + self.c * 2.3283064365386963e-10
        self.c = int(t) | 0
        self.s[self.p] = t - self.c
        return self.s[self.p]

   
