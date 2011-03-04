"""
photUtils - 

$Id$

ljones@astro.washington.edu  (and ajc@astro.washington.edu)

Collection of utilities to aid usage of Sed and Bandpass with dictionaries.

"""

import os
import lsst.sims.catalogs.measures.photometry.Sed as Sed
import lsst.sims.catalogs.measures.photometry.Bandpass as Bandpass

# Handy routines for handling Sed/Bandpass routines with sets of dictionaries.
def loadSeds(sedList, dataDir = "./"):
    """Generate dictionary of SEDs required for generating magnitudes

    Given a dataDir and a list of seds return a dictionary with sedName and sed as key, value
    """
    sedDict={}
    for sedName in sedList:
        if sedName in sedDict:
            continue
        else:
            sed = Sed()
            sed.readSED_flambda(os.path.join(dataDir, sedName)
            if sed.needResample():
                sed.resampleSED()             
            sedDict[sedName] = sed
    return sedDict

def loadBandpasses(filterlist=('u', 'g', 'r', 'i', 'z', 'y'), dataDir=None, filterroot='total_'):
    """ Generate dictionary of bandpasses for the LSST nominal throughputs

    Given a list of filter keys (like u,g,r,i,z,y), return a dictionary of the total bandpasses.
    dataDir is the directory where these bandpasses are stored; leave blank to use environment
     variable 'LSST_THROUGHPUTS_DEFAULT' which is set if throughputs is setup using eups.
    This routine uses the 'total' bandpass values by default, but can be changed (such as to 'filter') using
     the filterroot option (filename = filterroot + filterkey + '.dat'). 
    """
    bandpassDict = {}
    if dataDir == None:
        dataDir = os.getenv("LSST_THROUGHPUTS_DEFAULT")
        if dataDir == None:
            raise Exception("dataDir not given and unable to access environment variable 'LSST_THROUGHPUTS_DEFAULT'")
    for f in filterlist:
        bandpassDict[f] = Bandpass()
        bandpassDict[f].readThroughput(os.path.join(dataDir, filterroot + f + ".dat")
    return bandpassDict

def setupPhiArray_dict(bandpassDict, bandpassKeys):
    """ Generate 2-dimensional numpy array for Phi values in the bandpassDict.

    You must pass in bandpassKeys so that the ORDER of the phiArray and the order of the magnitudes returned by
    manyMagCalc can be preserved. You only have to do this ONCE and can then reuse phiArray many times for many
    manyMagCalculations."""
    # Make a list of the bandpassDict for phiArray - in the ORDER of the bandpassKeys
    bplist = []
    for f in bandpassKeys:
        bplist.append(lsstbp[f])
    sedobj = Sed()
    phiArray, wavelenstep = sedobj.setupPhiArray(bplist)
    return phiArray, wavelenstep

def manyMagCalc_dict(sedobj, phiArray, wavelenstep, bandpassDict, bandpassKeys):
    """Return a dictionary of magnitudes for a single Sed object.

    You must pass the sed itself, phiArray and wavelenstep for the manyMagCalc itself, but
    you must also pass the bandpassDictionary and keys so that the sedobj can be resampled onto
    the correct wavelength range for the bandpass (i.e. maybe you redshifted sedobj??) and so that the
    order of the magnitude calculation / dictionary assignment is preserved from the phiArray setup previously.
    Note that THIS WILL change sedobj by resampling it onto the required wavelength range. """
    # Set up the SED for using manyMagCalc - note that this CHANGES sedobj
    # Have to check that the wavelength range for sedobj matches bandpass - this is why the dictionary is passed in.
    if sedobj.needResample(wavelen=wavelen, wavelen_match=bandpassDict[bandpassKeys[0]].wavelen):
        sedobj.resampleSED(wavelen_match=bandpassDict[bandpassKeys[0]].wavelen)
    sedobj.flambdaTofnu()
    magArray = sedobj.calcManyMag(phiArray, wavelenstep)
    magDict = {}
    i = 0
    for f in bandpassKeys:
        magDict[f] = magArray[i]
        i = i + 1
    return magDict

