import math


def get_prefer_non_empty_machines_score(used_gc, free_gc, used_rc, free_rc):
    if used_gc + used_rc > 0:
        return 1
    else:
        return 0


def get_prefer_most_unused_green_cores_score(used_gc, free_gc, used_rc, free_rc):
    if free_gc + used_gc == 0:
        return 0
    else:
        return free_gc / (free_gc + used_gc)


def get_prefer_guranteed_renewable_draw_score(used_gc, free_gc, used_rc, free_rc, type, vm_vcpus):
    if type == 'regular':
        return 0

    overflow = vm_vcpus - free_rc
    if 0 < overflow <= free_gc:
        return 1
    else:
        return 0


def get_worst_fit_on_green_cores_score(used_gc, free_gc, used_rc, free_rc, type, vm_vcpus):
    if free_gc + used_gc == 0:
        return 0
    overflow = vm_vcpus - free_rc
    if 0 < overflow <= free_gc:
        return free_gc / (free_gc + used_gc)
    else:
        return 0


def get_best_fit_on_green_cores_score(used_vcpu, free_vcpu):
    return 1 - (free_vcpu / (used_vcpu + free_vcpu))


def get_cpu_attrs(host_state):
    vcpus_used = host_state.vcpus_used
    vcpus_free = (host_state.vcpus_total * 1.0 - host_state.vcpus_used)
    rcpus_used = host_state.rcpus_used
    rcpus_free = (host_state.rcpus_total * 1.0 - host_state.rcpus_used)
    gcpus_used = host_state.gcpus_used
    gcpus_free = (host_state.gcpus_total * 1.0 - host_state.gcpus_used)
    return gcpus_free, gcpus_used, rcpus_free, rcpus_used, vcpus_free, vcpus_used

def get_final_weight(gcpus_free, gcpus_used, rcpus_free, rcpus_used, type, vcpus_free, vcpus_used,
                     vm_vcpus):
    w1 = math.pow(3, 4) * get_prefer_non_empty_machines_score(gcpus_used, gcpus_free, rcpus_used, rcpus_free)
    w2 = math.pow(3, 3) * get_prefer_most_unused_green_cores_score(gcpus_used, gcpus_free, rcpus_used, rcpus_free)
    w3 = math.pow(3, 2) * get_prefer_guranteed_renewable_draw_score(gcpus_used, gcpus_free, rcpus_used, rcpus_free,
                                                                    type, vm_vcpus)
    w4 = math.pow(3, 1) * get_worst_fit_on_green_cores_score(gcpus_used, gcpus_free, rcpus_used, rcpus_free, type,
                                                             vm_vcpus)
    w5 = math.pow(3, 0) * get_best_fit_on_green_cores_score(vcpus_used, vcpus_free)
    final_weight = w1 + w2 + w3 + w4 + w5
    return final_weight