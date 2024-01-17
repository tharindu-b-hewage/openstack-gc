import scipy.stats


def pickRandom(dist):
    kde = scipy.stats.gaussian_kde(dist)
    return kde.resample(size=1)
