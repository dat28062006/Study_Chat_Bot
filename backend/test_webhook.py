import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.tools.n8n_tool import export_plan_to_n8n

print(export_plan_to_n8n('test@test.com', 'subject', '[{"day": 1}]'))
