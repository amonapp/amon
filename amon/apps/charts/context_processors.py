from amon.apps.charts.forms import (
        DurationForm, 
        SystemChartsForm,
        ProcessChartsForm
)
from amon.apps.servers.models import server_model


def charts_global_variables(request):

    if request.user.is_authenticated:
        all_servers = server_model.get_all(account_id=request.account_id)

        global_variables_dict = {
            'duration_form': DurationForm(),
            'system_charts_form': SystemChartsForm(), 
            'process_charts_form': ProcessChartsForm(),
            'all_servers': all_servers
        }
    else:
        global_variables_dict = {
            'duration_form': DurationForm(),
        }


    return global_variables_dict