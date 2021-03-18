class DKIMStatus:
    def __init__(self, enabled=False, record_found=False, record_valid=False, current_record=''):
        self.enabled = enabled
        self.record_found = record_found
        self.record_valid = record_valid
        self.current_record = current_record


class DKIM:
    def __init__(self, status: DKIMStatus = None, expected_dns_record=None, current_dns_record=None):
        self.status = status
        self.expected_dns_record = expected_dns_record
        self.current_dns_record = current_dns_record
