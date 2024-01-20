import csv


class OsManager:
    '''OsManager encapsulate vm lifecycle management based on the trace information.
    It further provides an insight on core utilization.
    '''

    def __init__(self):
        self.local_tracking_total_cores = 26
        self.local_tracking_used_cores = 0
        self.created_vms = {}
        self.evictedVMs = []
        self.uninterruptedVMs = []

    def dispatch(self, vm_rqs, clk):
        self.create_vms(vm_rqs, clk)

    def handle_expired_vms(self, clk):
        for vm_name, vm in self.created_vms.items():
            if vm['end-of-life'] <= clk:
                resp = self.delete_vm(vm_name)
                if resp is None:
                    # VM does not exist. Must be evicted.
                    vm = self.created_vms[vm_name]
                    vm['is-evicted'] = True

    def create_vms(self, vm_rqs, clk):
        for vm in vm_rqs:
            resp = self.create_vm(vm, clk)
            if resp is not None:
                vm['end-of-life'] = clk + vm['lifetime']
                vm['is-evicted'] = False  # assume vm is going to live a full life.
                self.created_vms[vm['name']] = vm
                self.local_tracking_used_cores += vm['vcpu']

    def create_vm(self, vm, clk):
        return True

    def delete_vm(self, vm_name):
        return True

    def get_utilization(self):
        return self.local_tracking_used_cores / self.local_tracking_total_cores

    def dump(self, file_path):
        header = ['name', 'type', 'is-evicted']

        with open(file_path, 'w', encoding='UTF8') as f:
            writer = csv.writer(f)

            # write the header
            writer.writerow(header)

            for vm in self.created_vms.values():
                writer.writerow([
                    vm['name'],
                    vm['type'],
                    vm['is-evicted']
                ])
