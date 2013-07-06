from amonone.core.collector.runner import runner
from amonone.web.apps.api.models import api_model

system_info = runner.system()
process_info = runner.processes()

api_model.store_system_entries(system_info)
api_model.store_process_entries(process_info)

