from os.path import join, abspath, dirname

PROJECT_ROOT = abspath(dirname(__file__))
TEMPLATES_DIR =  join(PROJECT_ROOT, 'templates')


server_metrics = {"1": "CPU",
                "2": "Memory",
                "3": "Loadavg",
                "5": "Disk"
                }

process_metrics = {"1": "CPU", "2": "Memory"}

common_metrics = ["KB", "MB", "GB", "%"]

