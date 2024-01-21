import scipy.stats


def pick_random(dst):
    is_uniform = len(set(dst)) == 1
    if is_uniform:
        return dst[0]

    lower_bd = min(dst)
    upper_bd = max(dst)
    kde = scipy.stats.gaussian_kde(dst)

    # kde can include out of range.
    sample = kde.resample(size=1)
    val = sample[0][0]
    while lower_bd >= val >= upper_bd:
        sample = kde.resample(size=1)
        val = sample[0][0]
    return val
