import math
import os

import numpy as np
from mysql.connector import connect

PERCENTILE = 90

USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
DB = os.getenv("DB")
print("user: ", USER, "password: ", PASSWORD, "host: ", HOST, "db: ", DB)


def get_bounds_for_percentile(time_from, time_to):
    with connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DB,
    ) as connection:
        def run_query_for_many(qry):
            with connection.cursor() as cursor:
                cursor.execute(qry)
                result = cursor.fetchall()
                rs = []
                for row in result:
                    rs.append(row[0])
                return rs

        # request count.
        rq_count_dst_qry = "select count(*) as c from vm where starttime > " + str(
            time_from) + " and starttime < " + str(time_to) + " group by starttime;"
        count_max_val, count_min_val = get_min_max_for_percentile(rq_count_dst_qry, run_query_for_many)

        # vcpu count.
        vcpu_dst_qry = "select vmCPUCores as c from vm inner join vmTypeToCores on vm.vmTypeId = vmTypeToCores.vmTypeId where starttime > " + str(
            time_from) + " and starttime < " + str(time_to)
        vcpu_max_val, vcpu_min_val = get_min_max_for_percentile(vcpu_dst_qry, run_query_for_many)

        # lifetimes count.
        lifetimes_dst_qry = "select IFNULL(vm.endtime - vm.starttime, 14.0) as c from vm  where starttime > " + str(
            time_from) + " and starttime < " + str(time_to)
        lifetimes_max_val, lifetimes_min_val = get_min_max_for_percentile(lifetimes_dst_qry, run_query_for_many)

        max_vals = {
            "vcpu_max": vcpu_max_val,
            "vcpu_min": vcpu_min_val,
            "lifetime_max": lifetimes_max_val,
            "lifetime_min": lifetimes_min_val,
            "count_min": count_min_val,
            "count_max": count_max_val
        }
        print('min-max vals for percentile: ' + str(PERCENTILE), max_vals)

        return max_vals


def get_min_max_for_percentile(rq_count_dst_qry, run_query_for_many):
    dst = run_query_for_many(qry=rq_count_dst_qry)
    sorted_dst = sorted(dst)
    perc_val = np.percentile(sorted_dst, PERCENTILE)
    sorted_dst = list(filter(lambda x: x < perc_val, sorted_dst))
    max_val = max(sorted_dst)
    min_val = min(sorted_dst)
    return max_val, min_val


def get_time_after(time_in_days_fraction=0.0):
    with connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DB,
    ) as connection:
        qry = "select starttime from vm where starttime > " + str(
            time_in_days_fraction) + " order by starttime asc limit 1"
        with connection.cursor() as cursor:
            cursor.execute(qry)
            result = cursor.fetchall()
            for row in result:
                return row[0]


def get_trace_at(time_in_days_fraction=0.0, max_consts={}):
    with connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DB,
    ) as connection:
        qry = "select vmCPUCores, priority, starttime, endtime from vm inner join vmTypeToCores on vm.vmTypeId = vmTypeToCores.vmTypeId where starttime = " + str(
            time_in_days_fraction)
        with connection.cursor() as cursor:
            cursor.execute(qry)
            result = cursor.fetchall()
            request_count = 0
            regular_vm_count = 0
            evictable_vm_count = 0
            vcpu_dst = []
            lifetime_dst = []
            for row in result:
                is_valid = True
                vcpu = row[0]
                is_evictable = row[1] == 1
                endtime = row[3] if row[3] else math.inf
                lifetime = endtime - row[2]

                def collect(max, min, to_add, val):
                    if not max >= val >= min:
                        return False

                    # nrl_val = (val - min) / (max - min)
                    # vcpu can be 2 max an 1 min. normalize can yield impractical numbers.
                    to_add.append(val)
                    return True

                is_valid = is_valid and collect(max=max_consts['vcpu_max'], min=max_consts['vcpu_min'],
                                                to_add=vcpu_dst, val=vcpu)
                is_valid = is_valid and collect(max=max_consts['lifetime_max'], min=max_consts['lifetime_min'],
                                                to_add=lifetime_dst, val=lifetime)

                if is_valid:
                    request_count += 1

                # We treat evictable as a characterictic and is independent of other parameters. then, say omiting an
                # evictable vm because its vcpu is out of range, makes it dependent. so regardless of others,
                # we count this property.
                regular_vm_count += 1 if not is_evictable else 0
                evictable_vm_count += 1 if is_evictable else 0

            bkt = []
            if collect(max=max_consts['count_max'], min=max_consts['count_min'], to_add=bkt,
                       val=request_count):
                request_count = bkt[0]
                reg_portion = regular_vm_count / (regular_vm_count + evictable_vm_count)
                evict_portion = evictable_vm_count / (regular_vm_count + evictable_vm_count)
            else:
                request_count = 0  # outliers omitted.
                reg_portion = 0
                evict_portion = 0
                lifetime_dst = []
                vcpu_dst = []

            return {
                'time': time_in_days_fraction,
                'request_count': request_count,
                'regular_vm_count': reg_portion,
                'evictable_vm_count': evict_portion,
                'lifetime_distribution': lifetime_dst,
                'vcpu_distribution': vcpu_dst
            }


def get_headers():
    return ['time', 'request_count', 'regular_vm_count', 'evictable_vm_count', 'lifetime_distribution',
            'vcpu_distribution']
