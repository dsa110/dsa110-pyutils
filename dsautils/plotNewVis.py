import numpy as np, pyfits as pf, matplotlib.pyplot as plt, pylab


def plotTimeAmp(fl=None, f1=None, f2=None, tbin=1):
    if fl is None:
        fl = '/mnt/nfs/data/dsatest.fits'
    f = pf.open(fl, ignore_missing_end=True)[1]
    nrow = (f.header['NAXIS2'])
    tsamp = f.header['TSAMP']
    nchan = 1536  # f.header['NCHAN']
    fch1 = f.header['FCH1'] - (nchan * 2 - 1) * 250. / 2048.
    if1 = 0
    if2 = nchan
    if f1 is not None:
        if f2 is not None:
            if1 = np.floor((-fch1 + f1) / (500. / 2048.)).astype('int')
            if2 = np.floor((-fch1 + f2) / (500. / 2048.)).astype('int')

    t1 = 0
    t2 = nrow - 1

    data = np.flip(f.data['VIS'].reshape((nrow, 6, nchan, 2, 2)), axis=2)[t1:t2, :, if1:if2, :,
           :].mean(axis=2)
    tmax = np.floor((t2 - t1) / (tbin * 1.)).astype('int') * tbin
    tims = np.arange(nrow) * tsamp
    tims = tims[0:tmax]
    data = data[0:tmax, :, :, :]

    tims = tims.reshape((tmax / tbin, tbin)).mean(axis=1)
    data = data.reshape((tmax / tbin, tbin, 6, 2, 2)).mean(axis=1)
    amps = 5. * (np.log10(data[:, :, :, 0] ** 2. + data[:, :, :, 1] ** 2.))

    for i in range(3):
        for j in range(i + 1):
            bases.append(str(i) + '-' + str(j))

    plt.ion()
    for pl in range(6):
        pylab.subplot(3, 5, pl + 1)
        plt.plot(tims, amps[:, pl, 0], 'r-')
        plt.plot(tims, amps[:, pl, 1], 'b-')
        plt.title(bases[pl])

    return tims, amps


# tmid as a standard astropy time, tspan in seconds
def plotTimePhase(fl=None, tspan=None, f1=None, f2=None, tbin=1):
    if fl is None:
        fl = '/mnt/nfs/data/dsatest.fits'
    f = pf.open(fl, ignore_missing_end=True)[1]
    nrow = (f.header['NAXIS2'])
    tsamp = f.header['TSAMP']
    nchan = 1536  # f.header['NCHAN']
    fch1 = f.header['FCH1'] - (nchan * 2 - 1) * 250. / 2048.
    if1 = 0
    if2 = nchan
    if f1 is not None:
        if f2 is not None:
            if1 = np.floor((-fch1 + f1) / (500. / 2048.)).astype('int')
            if2 = np.floor((-fch1 + f2) / (500. / 2048.)).astype('int')

    t1 = 0
    t2 = nrow - 1

    data = np.flip(f.data['VIS'].reshape((nrow, 6, nchan, 2, 2)), axis=2)[t1:t2, :, if1:if2, :,
           :].mean(axis=2)
    tmax = np.floor((t2 - t1) / (tbin * 1.)).astype('int') * tbin
    tims = np.arange(nrow) * tsamp
    tims = tims[0:tmax]
    data = data[0:tmax, :, :, :]

    tims = tims.reshape((tmax / tbin, tbin)).mean(axis=1)
    data = data.reshape((tmax / tbin, tbin, 6, 2, 2)).mean(axis=1)
    angs = (180. / np.pi) * np.angle(data[:, :, :, 0] + data[:, :, :, 1] * 1j)

    bases = []
    for i in range(3):
        for j in range(i + 1):
            bases.append(str(i) + '-' + str(j))

    plt.ion()
    for pl in range(6):
        pylab.subplot(3, 2, pl + 1)
        plt.ylim(-180., 180.)
        plt.plot(tims, angs[:, pl, 0], 'r-')
        plt.plot(tims, angs[:, pl, 1], 'b-')
        plt.title(bases[pl])

    return (tims, angs)


# tmid as a standard astropy time, tspan in seconds
def plotFreqAmp(fl=None, tspan=None, f1=None, f2=None):
    if fl is None:
        fl = '/mnt/nfs/data/dsatest.fits'
    f = pf.open(fl, ignore_missing_end=True)[1]
    nrow = int((f.header['NAXIS2']))
    tsamp = f.header['TSAMP']
    nchan = 1536  # f.header['NCHAN']
    fch1 = f.header['FCH1'] - (nchan * 2 - 1) * 250. / 2048.
    if1 = 0
    if2 = nchan
    if f1 is not None:
        if f2 is not None:
            if1 = np.floor((-fch1 + f1) / (500. / 2048.)).astype('int')
            if2 = np.floor((-fch1 + f2) / (500. / 2048.)).astype('int')

    t1 = 0
    t2 = nrow - 1

    data = np.flip(f.data['VIS'].reshape((nrow, 6, nchan, 2, 2)), axis=2)[t1:t2, :, if1:if2, :, :]
    data = data.mean(axis=0)
    freqs = np.arange(nchan)  # (np.arange(nchan)*(250./8192.)+fch1)[if1:if2]

    amps = 5. * (np.log10(data[:, :, :, 0] ** 2. + data[:, :, :, 1] ** 2.))

    bases = []
    for i in range(3):
        for j in range(i + 1):
            bases.append(str(i) + '-' + str(j))

    plt.ion()
    for pl in range(6):
        pylab.subplot(3, 2, pl + 1)
        plt.xlim(freqs.min(), freqs.max())
        plt.plot(freqs, amps[pl, :, 0], 'r-')
        plt.plot(freqs, amps[pl, :, 1], 'b-')
        plt.title(bases[pl])

    return freqs, amps


# tmid as a standard astropy time, tspan in seconds
def plotFreqPhase(fl=None, tspan=None, f1=None, f2=None):
    if fl is None:
        fl = '/mnt/nfs/data/dsatest.fits'
    f = pf.open(fl, ignore_missing_end=True)[1]
    nrow = (f.header['NAXIS2'])
    tsamp = f.header['TSAMP']
    nchan = 1536  # f.header['NCHAN']
    fch1 = f.header['FCH1'] - (nchan * 2 - 1) * 250. / 2048.
    if1 = 0
    if2 = nchan
    if f1 is not None:
        if f2 is not None:
            if1 = np.floor((-fch1 + f1) / (500. / 2048.)).astype('int')
            if2 = np.floor((-fch1 + f2) / (500. / 2048.)).astype('int')

    t1 = 0
    t2 = nrow - 1

    data = np.flip(f.data['VIS'].reshape((nrow, 6, nchan, 2, 2)), axis=2)[t1:t2, :, if1:if2, :, :]
    data = data.mean(axis=0)
    freqs = np.arange(nchan)  # (np.arange(nchan)*(250./8192.)+fch1)[if1:if2]

    angs = (180. / np.pi) * np.angle(data[:, :, :, 0] + data[:, :, :, 1] * 1j)

    bases = []
    for i in range(3):
        for j in range(i + 1):
            bases.append(str(i) + '-' + str(j))

    plt.ion()
    for pl in range(6):
        pylab.subplot(3, 2, pl + 1)
        plt.ylim(-180., 180.)
        plt.xlim(freqs.min(), freqs.max())
        plt.plot(freqs, angs[pl, :, 0], 'r-')
        plt.plot(freqs, angs[pl, :, 1], 'b-')
        plt.title(bases[pl])

    return freqs, angs
