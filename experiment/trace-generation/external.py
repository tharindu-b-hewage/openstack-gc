import csv
from openstack_client import create_flavours, create_vm, delete_vm


class RequestsManager:
    '''OsManager encapsulate vm lifecycle management based on the trace information.
    It further provides an insight on core utilization.
    '''

    def __init__(self):
        self.local_tracking_total_cores = 36
        self.local_tracking_used_cores = 0
        self.created_vms = {}
        self.evictedVMs = []
        self.uninterruptedVMs = []

    def dispatch(self, vm_rqs, clk):
        self.create_vms(vm_rqs, clk)

    def handle_expired_vms(self, clk):
        for vm_name, vm in self.created_vms.items():
            if vm['end-of-life'] <= clk:
                resp = self.delete_vm(vm)
                if not resp:
                    # VM does not exist. Must be evicted.
                    print('failed deletion. marking as evicted: ', vm['name'])
                    vm = self.created_vms[vm_name]
                    vm['is-evicted'] = True
                else:
                    vm['is-deleted'] = True
                    vm['end-of-life'] = 100  # a very large value that we will never reach

    def create_vms(self, vm_rqs, clk):
        for vm in vm_rqs:
            resp = self.create_vm(vm, clk)
            if resp:
                print('marked successful vm creation of: ', vm['name'])
                vm['end-of-life'] = clk + vm['lifetime']
                vm['is-evicted'] = False  # assume vm is going to live a full life.
                self.created_vms[vm['name']] = vm
                self.local_tracking_used_cores += vm['vcpu']

    def create_vm(self, vm, clk):
        return create_vm(vm)

    def delete_vm(self, vm):
        return delete_vm(vm)

    def get_utilization(self):
        return self.local_tracking_used_cores / self.local_tracking_total_cores

    def dump(self, file_path):
        header = ['name', 'type', 'vcpu', 'lifetime', 'is-evicted']

        with open(file_path, 'w', encoding='UTF8') as f:
            writer = csv.writer(f)

            # write the header
            writer.writerow(header)

            for vm in self.created_vms.values():
                writer.writerow([
                    vm['name'],
                    vm['type'],
                    vm['vcpu'],
                    vm['lifetime'],
                    vm['is-evicted']
                ])
