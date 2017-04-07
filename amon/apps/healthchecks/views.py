from amon.apps.core.views import *
from amon.utils.dates import unix_utc_now


from amon.apps.healthchecks.models import health_checks_model



@login_required
def view(request):
    now = unix_utc_now()
    sort_by = request.GET.get('sort_by')
    filter_by = request.GET.get('filter_by')

    result = health_checks_model.sort_and_filter(sort_by=sort_by, filter_by=filter_by)

    return render(request, 'healthchecks/view.html', {
        "all_checks": result.all_checks,
        "now": now,
        "sort_by": sort_by,
        "filter_by": filter_by,
        "sorted_result": result.sorted_result,
        "flat_list": result.flat_list,
        "count_statuses": result.count_statuses,
    })
