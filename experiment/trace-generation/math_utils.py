import scipy.stats


def pick_random(dst):
    is_uniform = len(set(dst)) == 1
    if is_uniform:
        return dst[0]
    kde = scipy.stats.gaussian_kde(dst)
    sample = kde.resample(size=1)
    return sample[0][0]
