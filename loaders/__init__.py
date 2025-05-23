import six

if six.PY2:
    from madrid_budget_loader import MadridBudgetLoader
    from madrid_payments_loader import MadridPaymentsLoader
    from madrid_investments_loader import MadridInvestmentsLoader
    from madrid_main_investments_loader import MadridMainInvestmentsLoader
    from madrid_monitoring_loader import MadridMonitoringLoader
    from madrid_utils import MadridUtils
else:
    from .madrid_budget_loader import MadridBudgetLoader
    from .madrid_payments_loader import MadridPaymentsLoader
    from .madrid_investments_loader import MadridInvestmentsLoader
    from .madrid_main_investments_loader import MadridMainInvestmentsLoader
    from .madrid_monitoring_loader import MadridMonitoringLoader
    from .madrid_utils import MadridUtils
