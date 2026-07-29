"""
Unified AI Platform REST API Router
Covers all 10 missions: ML Prediction, Digital Twin, Blockchain,
Federated Learning, Multi-Agent, Enhanced Quantum, IoT, Analytics, Synthetic Data
"""
import io
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.core.database import get_db
from backend.app.core.security import RoleChecker
from backend.app.services.ml_prediction_service import MLPredictionService
from backend.app.services.digital_twin_service import DigitalTwinService
from backend.app.services.blockchain_service import BlockchainService
from backend.app.services.federated_learning_service import FederatedLearningService
from backend.app.services.multi_agent_system import MultiAgentSystem
from backend.app.services.research_analytics_service import ResearchAnalyticsService
from backend.app.services.synthetic_data_generator import SyntheticDataGenerator
from backend.app.models.domain import TransplantPrediction

router = APIRouter(prefix="/ai", tags=["AI Platform — All 10 Missions"])


# ─── MISSION 1: ML Prediction ────────────────────────────────────────────────

@router.post("/predict")
def predict_transplant(payload: dict, db: Session = Depends(get_db)):
    """M1 · AI Graft Survival & Rejection Prediction (XGBoost + LightGBM + RF Ensemble)"""
    result = MLPredictionService.predict_transplant_outcome(payload, db=db)
    return result


@router.get("/predictions/history")
def get_prediction_history(db: Session = Depends(get_db)):
    """M1 · List all stored AI predictions."""
    records = db.query(TransplantPrediction).order_by(
        TransplantPrediction.created_at.desc()).limit(50).all()
    return [
        {
            "id": r.id,
            "organ_type": r.organ_type,
            "patient_age": r.patient_age,
            "blood_type": r.blood_type,
            "one_year_survival": r.one_year_survival,
            "five_year_survival": r.five_year_survival,
            "rejection_probability": r.rejection_probability,
            "mortality_risk": r.mortality_risk,
            "overall_success": r.overall_success,
            "confidence_score": r.confidence_score,
            "created_at": r.created_at.isoformat() if r.created_at else ""
        }
        for r in records
    ]


@router.post("/predict/pdf")
def download_prediction_pdf(payload: dict):
    """M1 · Generate & Download AI Prediction Report as PDF."""
    prediction = MLPredictionService.predict_transplant_outcome(payload)
    pdf_bytes = MLPredictionService.generate_pdf_report(prediction)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=qtransplant_ai_report.pdf"}
    )


# ─── MISSION 2: Digital Twin ─────────────────────────────────────────────────

@router.get("/digital-twin/live")
def get_digital_twin_state(mode: str = Query("ambulance", description="Transport mode: ambulance | drone")):
    """M2 · Real-Time Digital Twin state: GPS, ETA, Temp, Cold Ischemia countdown."""
    return DigitalTwinService.get_live_twin_state(mode=mode)


@router.get("/digital-twin/replay")
def get_twin_replay():
    """M2 · Historical replay of Digital Twin transport frames."""
    return DigitalTwinService.get_historical_replay()


# ─── MISSION 3: Blockchain Audit ─────────────────────────────────────────────

@router.get("/blockchain/chain")
def get_blockchain_chain(db: Session = Depends(get_db)):
    """M3 · Full blockchain audit ledger."""
    return BlockchainService.get_chain(db)


@router.post("/blockchain/add-block")
def add_blockchain_block(payload: dict, db: Session = Depends(get_db)):
    """M3 · Add a new audit block to the chain."""
    return BlockchainService.add_block(
        db=db,
        actor=payload.get("actor", "System"),
        hospital=payload.get("hospital", "Q-Transplant Platform"),
        action=payload.get("action", "SYSTEM_ACTION"),
        details=payload.get("details", "")
    )


@router.get("/blockchain/verify")
def verify_blockchain(db: Session = Depends(get_db)):
    """M3 · Verify chain integrity — detect tampering."""
    return BlockchainService.verify_chain_integrity(db)


@router.get("/blockchain/export")
def export_blockchain(db: Session = Depends(get_db)):
    """M3 · Export full blockchain to JSON."""
    chain = BlockchainService.get_chain(db)
    import json
    content = json.dumps(chain, indent=2)
    return StreamingResponse(
        io.BytesIO(content.encode()),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=blockchain_export.json"}
    )


# ─── MISSION 4: Federated Learning ───────────────────────────────────────────

@router.post("/federated/run-round")
def run_federated_round(db: Session = Depends(get_db)):
    """M4 · Execute one Federated Learning round across 4 hospital nodes (FedAvg)."""
    return FederatedLearningService.run_federated_round(db)


@router.get("/federated/history")
def get_federated_history(db: Session = Depends(get_db)):
    """M4 · Federated Learning session history."""
    return FederatedLearningService.get_session_history(db)


@router.get("/federated/nodes")
def get_federated_nodes():
    """M4 · List all hospital federated learning nodes."""
    return FederatedLearningService.HOSPITAL_NODES


# ─── MISSION 5: Multi-Agent System ───────────────────────────────────────────

@router.post("/agents/run-cycle")
def run_agent_cycle(db: Session = Depends(get_db)):
    """M5 · Execute one autonomous multi-agent coordination cycle."""
    return MultiAgentSystem.run_agent_cycle(db)


@router.get("/agents/list")
def list_agents():
    """M5 · List all autonomous agents and their roles."""
    return MultiAgentSystem.AGENTS


@router.get("/agents/logs")
def get_agent_logs(db: Session = Depends(get_db)):
    """M5 · Agent communication history."""
    return MultiAgentSystem.get_agent_logs(db)


# ─── MISSION 6: Enhanced Quantum Matching (in quantum_matching.py) ───────────
# See /api/v1/matches endpoints for quantum matching — already wired.

# ─── MISSION 9: Research Analytics ───────────────────────────────────────────

@router.get("/analytics")
def get_research_analytics(db: Session = Depends(get_db)):
    """M9 · Comprehensive research analytics dashboard data."""
    return ResearchAnalyticsService.get_comprehensive_analytics(db)


# ─── MISSION 10: Synthetic Data Generation ────────────────────────────────────

@router.get("/synthetic/generate")
def generate_synthetic_data(
    count: int = Query(1000, description="Number of records (100–100000)"),
    format: str = Query("json", description="Export format: json | csv | sql")
):
    """M10 · Generate synthetic transplant dataset and export in the requested format."""
    count = max(100, min(count, 100000))
    records = SyntheticDataGenerator.generate_dataset(count)
    stats = SyntheticDataGenerator.get_benchmark_stats(records)

    if format == "csv":
        csv_bytes = SyntheticDataGenerator.export_csv(records)
        return StreamingResponse(
            io.BytesIO(csv_bytes),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=qtransplant_synthetic_{count}.csv"}
        )
    elif format == "sql":
        sql_bytes = SyntheticDataGenerator.export_sql(records)
        return StreamingResponse(
            io.BytesIO(sql_bytes),
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename=qtransplant_synthetic_{count}.sql"}
        )

    json_bytes = SyntheticDataGenerator.export_json(records[:min(count, 5000)])
    return StreamingResponse(
        io.BytesIO(json_bytes),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=qtransplant_synthetic_{count}.json"}
    )


@router.get("/synthetic/stats")
def get_synthetic_stats(count: int = Query(1000)):
    """M10 · Generate synthetic dataset and return benchmark statistics only."""
    records = SyntheticDataGenerator.generate_dataset(min(count, 10000))
    return SyntheticDataGenerator.get_benchmark_stats(records)
