from trading.risk.decision import RiskDecision

def expect_rejection(decision):
    try:
        decision.validate()
    except ValueError:
        return True
    return False

assert RiskDecision(True, "ALLOW", "OK", "allowed", 0.01, 100).validate() is True
assert RiskDecision(False, "REDUCE", "LIMIT", "reduced", 0.005, 50).validate() is True
assert RiskDecision(False, "REJECT", "NO", "rejected").validate() is True
assert expect_rejection(RiskDecision(False, "BAD", "X", "invalid"))
assert expect_rejection(RiskDecision(False, "REJECT", "", "missing code"))
assert expect_rejection(RiskDecision(False, "REJECT", "X", ""))
assert expect_rejection(RiskDecision(False, "REJECT", "X", "negative risk", -0.1, 0))
assert expect_rejection(RiskDecision(False, "REJECT", "X", "negative notional", 0, -1))
assert expect_rejection(RiskDecision(False, "ALLOW", "X", "invalid allowed state"))
assert expect_rejection(RiskDecision(True, "REJECT", "X", "invalid allowed state"))
print("RISK_DECISION_CONTRACT_TESTS: PASS")
