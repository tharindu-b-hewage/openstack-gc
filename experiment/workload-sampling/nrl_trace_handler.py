import os
from mysql.connector import connect, Error

# vpu_max = 12
# count_max = 1002.0
# lifetime_max = 89.6387860183604

USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
DB = os.getenv("DB")
print("user: ", USER, "password: ", PASSWORD, "host: ", HOST, "db: ", DB)


def get_max_consts(time_from, time_to):
    with connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DB,
    ) as connection:
        vcpu_max_qry = "select vmCPUCores as c from vm inner join vmTypeToCores on vm.vmTypeId = vmTypeToCores.vmTypeId where starttime > " + str(time_from) + " and starttime < " + str(time_to) + " order by c desc limit 1"
        count_max_qry = "select count(*) as c from vm where starttime > " + str(time_from) + " and starttime < " + str(time_to) + " group by starttime order by c desc limit 1"
        lifetime_max_qry = "select vm.endtime - vm.starttime as c from vm  where starttime > " + str(time_from) + " and starttime < " + str(time_to) + " order by c desc limit 1"

        def run_query(qry):
            with connection.cursor() as cursor:
                cursor.execute(qry)
                result = cursor.fetchall()
                for row in result:
                    return row[0]

        return {
            "vcpu_max": run_query(vcpu_max_qry),
            "lifetime_max": run_query(lifetime_max_qry),
            "count_max": run_query(count_max_qry)
        }


def get_time_after(time_in_days_fraction=0.0):
    with connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DB,
    ) as connection:
        qry = "select starttime from vm where starttime > " + str(time_in_days_fraction) + " order by starttime asc limit 1"
        with connection.cursor() as cursor:
            cursor.execute(qry)
            result = cursor.fetchall()
            for row in result:
                return row[0]


def get_trace_at(time_in_days_fraction=0.0, vcpu_max=None, lifetime_max=None, count_max=None):
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
            nrl_vcpu_distribution = []
            nrl_lifetime_distribution = []
            for row in result:
                vcpu = row[0]
                isEvictable = row[1] == 1
                endtime = row[3] if row[3] else lifetime_max
                lifetime = endtime - row[2]

                request_count += 1
                regular_vm_count += 1 if not isEvictable else 0
                evictable_vm_count += 1 if isEvictable else 0
                nrl_vcpu_distribution.append(vcpu / vcpu_max)
                nrl_lifetime_distribution.append(lifetime / lifetime_max)
            nrl_request_count = request_count / count_max
            nrl_regular_count = regular_vm_count / request_count
            nrl_evictable_vm_count = evictable_vm_count / request_count
            return {
                'request_count': nrl_request_count,
                'regular_vm_count': nrl_regular_count,
                'evictable_vm_count': nrl_evictable_vm_count,
                'lifetime_distribution': nrl_lifetime_distribution,
                'vcpu_distribution': nrl_vcpu_distribution
            }


def get_headers():
    return ['request_count', 'regular_vm_count', 'evictable_vm_count', 'lifetime_distribution', 'vcpu_distribution']
