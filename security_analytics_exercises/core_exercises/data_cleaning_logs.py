"""
Data Cleaning (Cybersecurity Alerts)
Question: Given a list of dictionaries representing log entries, remove duplicates and filter out alerts that have a severity lower than 'High'.
python
logs = [
    {'id': 1, 'severity': 'Low', 'msg': 'Login'},
    {'id': 2, 'severity': 'High', 'msg': 'Port Scan'},
    {'id': 1, 'severity': 'Low', 'msg': 'Login'},
    {'id': 3, 'severity': 'Critical', 'msg': 'Payload'}
]
# Expected: Unique high/critical logs
Concepts: Dictionaries, List comprehensions, Sets for deduplication.
"""
from typing import List

def clean_logs(logs: List[dict]) -> List[dict]:
    # cleaned_logs = []
    # for log in logs:
    #     if log['severity'] == "High":
    #         clean_logs = cleaned_logs.append(log)
    # return cleaned_logs
    return [log for log in logs if log['severity'] == "High"]

if __name__ == "__main__":
    logs = [
        {'id': 1, 'severity': 'Low', 'msg': 'Login'},
        {'id': 2, 'severity': 'High', 'msg': 'Port Scan'},
        {'id': 1, 'severity': 'Low', 'msg': 'Login'},
        {'id': 3, 'severity': 'Critical', 'msg': 'Payload'}
    ]
    print(clean_logs(logs))