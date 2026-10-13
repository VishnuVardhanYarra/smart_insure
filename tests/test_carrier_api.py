import sys
import os
import pytest

# Add root path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from carrier_api import fetch_live_carrier_quotes, bind_policy_proposal, CARRIER_REGISTRY

def test_fetch_live_carrier_quotes():
    user_data = {
        'name': 'Live Carrier Candidate',
        'age': '38',
        'annual_income': '1200000',
        'dependents': '2'
    }
    risk_score = 45
    quotes = fetch_live_carrier_quotes(user_data, risk_score)
    
    assert len(quotes) == len(CARRIER_REGISTRY)
    for q in quotes:
        assert 'quote_id' in q
        assert 'carrier_name' in q
        assert 'total_monthly_inr' in q
        assert 'gst_18_inr' in q
        assert q['binding_status'] == "REAL_TIME_VERIFIED"
        assert q['total_monthly_inr'] == q['base_monthly_inr'] + q['gst_18_inr']

def test_bind_policy_proposal():
    res = bind_policy_proposal("QTL-HDFC-998811", "Live Carrier Candidate")
    assert res['status'] == "SUCCESS"
    assert "PROP-IRDAI-" in res['proposal_id']
    assert "POL-" in res['policy_number']
    assert res['quote_id'] == "QTL-HDFC-998811"
