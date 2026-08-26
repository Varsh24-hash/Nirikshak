from fastapi import FastAPI, HTTPException
from src.schemas.input_schemas import FullVerificationRequest
from src.schemas.output_schemas import VerificationOutput, VerificationStatus, RiskLevel
from src.fusion.aggregator import aggregate_data
from src.verification.verifier import generate_verification_report
from src.anomaly_detection.detector import detect_anomalies
from src.risk_scoring.scorer import calculate_risk

app = FastAPI(
    title="Multimodal Fusion + Verification Agent",
    description="Person 4 of the NIRIKSHAK Pipeline",
    version="1.0.0"
)

def orchestrate_verification(request: FullVerificationRequest) -> VerificationOutput:
    """
    Single orchestration function that wires:
    Fusion -> Anomaly Detection -> Verification Agent -> Risk Scoring
    """
    # Step 1: Fusion
    case_object = aggregate_data(request)
    
    # Step 2: Anomaly Detection
    anomalies = detect_anomalies(case_object)
    
    # Step 3: LLM Verification Reasoning
    status, explanations = generate_verification_report(case_object, anomalies)
    
    # Combine explanations and anomalies
    all_factors = explanations + [a.reason for a in anomalies]
    
    # Step 4: Risk Scoring
    evidence = case_object["sources"].get("evidence", {})
    forensics = case_object["sources"].get("forensics", {})
    
    cv_score = evidence.get("cv_relevance_score", 1.0) # default safe if missing
    forensics_score = forensics.get("forensics_confidence_score", 1.0)
    metadata_consistent = forensics.get("metadata_consistency_flag", True)
    
    risk_level, priority_rank = calculate_risk(
        status=status,
        anomalies=anomalies,
        forensics_score=forensics_score,
        cv_score=cv_score,
        metadata_consistent=metadata_consistent
    )
    
    # Step 5: Final Output formulation
    evidence_confidence = 1.0 - (len(anomalies) * 0.1)
    evidence_confidence = max(0.0, evidence_confidence)
    
    return VerificationOutput(
        verification_status=status,
        evidence_confidence=evidence_confidence,
        explanation=all_factors,
        risk_level=risk_level,
        inspection_priority_rank=priority_rank,
        contributing_factors=anomalies
    )

@app.post("/verify", response_model=VerificationOutput)
async def verify_endpoint(request: FullVerificationRequest):
    try:
        return orchestrate_verification(request)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
