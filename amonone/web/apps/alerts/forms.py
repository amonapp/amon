import formencode
from formencode import validators



class EditServerRuleForm(formencode.Schema):
	allow_extra_fields = True
	metric_value = formencode.All(validators.Number(not_empty=True))
	threshold = formencode.All(validators.Number(not_empty=True))

class AddServerRuleForm(formencode.Schema):
	allow_extra_fields = True
	metric = formencode.All(validators.PlainText(not_empty=True))
	metric_value = formencode.All(validators.Number(not_empty=True))
	threshold = formencode.All(validators.Number(not_empty=True))


class EditProcessRuleForm(formencode.Schema):
	allow_extra_fields = True
	metric_value = formencode.All(validators.Number(not_empty=True))
	threshold = formencode.All(validators.Number(not_empty=True))

class AddProcessRuleForm(formencode.Schema):
	allow_extra_fields = True
	process = formencode.All(validators.PlainText(not_empty=True))
	check = formencode.All(validators.PlainText(not_empty=True))
	metric_value = formencode.All(validators.Number(not_empty=True))
	threshold = formencode.All(validators.Number(not_empty=True))