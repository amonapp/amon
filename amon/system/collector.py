import subprocess
import sys

if sys.platform == 'darwin':
    from amon.system._macos import MacOSSystemCollector
    system_info_collector = MacOSSystemCollector()
else:
    from amon.system._linux import LinuxSystemCollector
    system_info_collector = LinuxSystemCollector()


class ProcessInfoCollector(object):

    def __init__(self):
        memory = system_info_collector.get_memory_info()
        self.total_memory = memory['memtotal']

    def check_process(self, name=None):
        # get the process info, remove grep from the result, print cpu, memory
        # ps aux |grep 'postgres' | grep -v grep | awk '{print $3","$4}' 

        ps = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE, close_fds=True)
        grep = subprocess.Popen(['grep', str(name)], stdin=ps.stdout, stdout=subprocess.PIPE, close_fds=True)
        remove_grep = subprocess.Popen(['grep', '-v','grep'], stdin=grep.stdout, stdout=subprocess.PIPE, close_fds=True)
        awk = subprocess.Popen(['awk', '{print $3","$4}'], stdin=remove_grep.stdout,\
        stdout=subprocess.PIPE, close_fds=True).communicate()[0]    

        lines = [0,0]
        for line in awk.splitlines():
            cpu_memory = line.split(',')
            cpu_memory = map(lambda x:  float(x), cpu_memory)
            lines[0] = lines[0]+cpu_memory[0]
            lines[1] = lines[1]+cpu_memory[1]
        lines  = map(lambda x:  "{0:.2f}".format(x), lines)
        
        cpu, memory = lines[0], lines[1]

        process_memory_mb = float(self.total_memory/100) * float(memory) # Convert the % in MB
        memory = "{0:.3}".format(process_memory_mb)
        process_info = {'cpu': cpu, 'memory': memory}
        
        return process_info
    
process_info_collector = ProcessInfoCollector()

