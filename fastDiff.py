#!/usr/bin/env python


import numpy as np
from scipy.fftpack.realtransforms import dct,idct


class fastDiff(object):
  '''
  fastDiff: class for fast 2nd O differentiation of a gridded dataset


  '''

  def __init__(self,y,thresh=1e-10,yshape=None,smoothOrder=1.0,axis=None):
    '''
    load gridded dataset y  and yshape (in case y is flattened)

    thresh:
      method has some rounding issues so threshold as thresh

    '''
    self.yshape = yshape or y.shape
    self.y = y
    self.axis = axis
    self.thresh = thresh
    self.smoothOrder = smoothOrder # not used at present    
    self.dctFilter = self.diffFilter()

  def diff(self,y=None):
    '''
    differentiate y (or loaded y)
    '''
    if y:
      assert y.size is np.prod(self.yshape)
    else:
      y = self.y.reshape(self.yshape)
 
    DTDy = self.dctND(self.dctFilter * self.dctND(y,f=dct),f=idct)
    DTDy[np.logical_and(DTDy>=-self.thresh,DTDy<=self.thresh)] = 0.
    return DTDy

  def dctND(self,data,f=dct,axis=None):
    if axis is not None:
      nd = len(data.shape)
      for i in xrange(nd):
        data = f(data,norm='ortho',type=2,axis=axis[i])
      return data
    else:
      nd = len(data.shape)
      if nd == 1:
        return f(data,norm='ortho',type=2)
      elif nd == 2:
        return f(f(data,norm='ortho',type=2).T,norm='ortho',type=2).T
      elif nd ==3:
        return f(f(f(data,norm='ortho',type=2,axis=0)\
                         ,norm='ortho',type=2,axis=1)\
                         ,norm='ortho',type=2,axis=2)

  def diffFilter(self):
    '''
     DCT-II filter for DT D
    '''
    yshape = self.yshape
    axis = self.axis
    ndim = len(yshape)
 
    # sort axis
    if axis is None:
        axis = tuple(np.arange(ndim))
    axis = tuple(np.array(axis).flatten())
    ndim = len(yshape)
    # initialise Lambda
    Lambda = np.zeros(yshape).astype(float)
    
    # normalisation factor
    n = 0.
    naxis = []
    for i in axis:
        # correct for -ves
        if i < 0:
          i = i + len(yshape) + 1
        naxis.append(i)
    axis = tuple(naxis)

    for c,i in enumerate(axis):
        # create a 1 x d array (so e.g. [1,1] for a 2D case
        siz0 = np.ones((1,ndim)).astype(int)[0]
        siz0[i] = yshape[i]

        this = np.cos(np.pi*(np.arange(1.,yshape[i]+1.) - 1.)/float(yshape[i])).reshape(siz0)
        Lambda = Lambda + this
        n += yshape[i]
    Lambda = -(len(axis)-Lambda)
    return (2*Lambda)

import sys

def main(argv):
  case1()
  case2()
  case3()

def case1():
   '''
   generate test dataset: impulse response
   '''
   import pylab as plt

   x = np.arange(100)
   y= np.zeros(100)
   y[50] = 1.0

   dtd = fastDiff(y)
   dtdy = dtd.diff()

   plt.figure(figsize=(10,3))
   plt.title('case 1: impulse response')
   plt.plot(x,y,'k-',label='signal $y$: impulse')
   plt.plot(x,dtdy,'r--',label='$D^T D y$: impulse response')
   plt.legend(loc='best')
   plt.show()
   plt.savefig('images/case1.png')

def case2():
  # case 2 image
  from PIL import Image
  import urllib2
  import pylab as plt

  url='https://upload.wikimedia.org/wikipedia/en/0/04/TCF_centre.jpg'

  im = np.array(Image.open(urllib2.urlopen(url)).convert("L")).astype(float)
  im /= im.max()
 
  dtd = fastDiff(im,axis=(0,1))  
  dtdy = dtd.diff()
  dtd1 = fastDiff(im,axis=(0,))
  dtdy1 = dtd1.diff()
  dtd2 = fastDiff(im,axis=(1,))
  dtdy2 = dtd2.diff()

  fig = plt.figure(figsize=(15,15))
  a=fig.add_subplot(231)
  a.set_title('Before')
  imgplot = plt.imshow(im,interpolation='nearest',cmap='gray')
  plt.colorbar(orientation ='horizontal')

  a=fig.add_subplot(232)
  b=plt.imshow(dtdy*1000,interpolation='nearest',cmap='gray')
  a.set_title('After x 1000')
  plt.colorbar(orientation ='horizontal',use_gridspec=True)

  a=fig.add_subplot(233)
  plt.imshow(dtdy1*1000,interpolation='nearest',cmap='gray')
  a.set_title('After x 1000: axis 0')
  plt.colorbar(orientation ='horizontal')

  a=fig.add_subplot(234)
  plt.imshow(dtdy2*1000,interpolation='nearest',cmap='gray')
  a.set_title('After x 1000: axis 1')
  plt.colorbar(orientation ='horizontal')

  a=fig.add_subplot(236) 
  a.set_title('DCT Filter x 1000')
  imgplot = plt.imshow(dtd.dctFilter*1000,interpolation='nearest',cmap='gray')
  plt.colorbar(orientation ='horizontal')
  plt.show()
  plt.savefig('images/case2.png')

def case3():
  # case 2 image in colour
  from PIL import Image
  import urllib2
  import pylab as plt

  url='https://upload.wikimedia.org/wikipedia/en/0/04/TCF_centre.jpg'

  im = np.array(Image.open(urllib2.urlopen(url))).astype(float)
  im /= im.max()

  dtd = fastDiff(im,axis=(0,1))
  dtdy = dtd.diff()
  dtd1 = fastDiff(im,axis=(0,))
  dtdy1 = dtd1.diff()
  dtd2 = fastDiff(im,axis=(1,))
  dtdy2 = dtd2.diff()

  fig = plt.figure(figsize=(15,15))
  a=fig.add_subplot(231)
  a.set_title('Before')
  imgplot = plt.imshow(im,interpolation='nearest',cmap='gray')

  a=fig.add_subplot(232)
  f = dtdy
  b=plt.imshow((255*f/f.max()).astype(int),interpolation='nearest',cmap='gray')
  a.set_title('After')

  a=fig.add_subplot(233)
  f = dtdy1
  plt.imshow((255*f/f.max()).astype(int),interpolation='nearest',cmap='gray')
  a.set_title('After: axis 0')

  a=fig.add_subplot(234)
  f = dtdy2
  plt.imshow((255*f/f.max()).astype(int),interpolation='nearest',cmap='gray')
  a.set_title('After: axis 1')

  a=fig.add_subplot(236)
  a.set_title('negative DCT Filter')
  f = ((-(dtd.dctFilter)))
  f = (255*f/f.max()).astype(int)
  imgplot = plt.imshow(f,interpolation='nearest')
  plt.show()
  plt.savefig('images/case3.png')

  
if __name__ == "__main__":
  main(sys.argv)
