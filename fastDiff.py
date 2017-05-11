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
    assert y.size is np.prod(self.yshape)
 
    DTDy = idct(self.dctFilter * dct(y))
    DTDy[np.logical_and(DTDy>=-self.thresh,DTDy<=self.thresh] = 0.
    return DTDy

  def diffFilter(self):
    '''
     DCT-II filter for DT D
    '''
    yshape = self.yshape
    axis = self.axis
    
    # sort axis
    if axis is None:
        axis = tuple(np.arange(ndim))
    axis = tuple(np.array(axis).flatten())
    ndim = len(axis)
    # initialise Lambda
    Lambda = np.zeros(yshape)
    
    # normalisation factor
    n = 0.
    for i in axis:
        # create a 1 x d array (so e.g. [1,1] for a 2D case
        siz0 = np.ones((1,ndim))[0]
        siz0[i] = yshape[i]
        
        Lambda = Lambda + \
                np.cos(np.pi*(arange(1,yshape[i]+1) - 1.)/yshape[i]).reshape(siz0)
        n += yshape[i]
      Lambda = -(len(axis)-Lambda)
      return (Lambda/n)


