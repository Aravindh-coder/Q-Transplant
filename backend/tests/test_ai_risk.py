from backend.app.services.ai_risk_service import AIRiskService


def test_ai_query_match_explanation():
    response = AIRiskService.answer_ai_query("Explain donor match scoring algorithm", {})
    assert "HLA" in response or "ABO" in response


def test_ai_query_urgent_alert():
    response = AIRiskService.answer_ai_query("Show urgent priority cases", {})
    assert "Urgent" in response or "Urgency" in response or "urgency" in response.lower()


def test_ai_query_telemetry():
    response = AIRiskService.answer_ai_query("Check cold box temperature telemetry", {})
    assert "°C" in response or "Telemetry" in response


def test_predict_eta_short_distance():
    result = AIRiskService.predict_transport_eta(distance_km=10.0)
    assert result["total_eta_minutes"] > 0
    assert result["distance_km"] == 10.0


def test_predict_eta_long_distance():
    result = AIRiskService.predict_transport_eta(distance_km=100.0)
    assert result["total_eta_minutes"] > result["base_eta_minutes"]
