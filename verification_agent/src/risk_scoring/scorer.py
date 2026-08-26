from typing import List, Tuple
from src.schemas.output_schemas import RiskLevel, AnomalyFinding, VerificationStatus

def calculate_risk(
    status: VerificationStatus, 
    anomalies: List[AnomalyFinding],
    forensics_score: float,
    cv_score: float,
    metadata_consistent: bool
) -> Tuple[RiskLevel, int]:
    """
    Computes a transparent, explainable risk score (0-100) based on weighted inputs.
    
    Weighting Logic (Defensible for non-technical evaluation):
    - Base Risk Score: 0
    - Verification Status: 
        - DISPUTED: +35 points
        - INSUFFICIENT_EVIDENCE: +25 points
        - PARTIALLY_VERIFIED: +10 points
    - Evidence Confidence (CV): If CV relevance < 0.5, adds +20 points (indicates wrong construction stage).
    - Evidence Confidence (Forensics): If forensics confidence < 0.5, adds +20 points (indicates possible tampering/error).
    - Metadata Consistency: If EXIF metadata is inconsistent (False), adds +15 points.
    - Anomalies: Each anomaly found by the rule engine adds +10 points.
    
    --- EXTENSION POINT: ML CALIBRATION ---
    Once labeled data (approved/rejected claims) is collected, the static weights above 
    can be replaced by a logistic regression or XGBoost model that outputs a calibrated probability.
    ----------------------------------------
    
    Returns:
        Tuple[RiskLevel, int]: The categorized risk level and a rank for inspection 
                               (1 = highest priority, 100 = lowest priority).
    """
    
    raw_score = 0
    
    # 1. Verification Status Weight
    if status == VerificationStatus.DISPUTED:
        raw_score += 35
    elif status == VerificationStatus.INSUFFICIENT_EVIDENCE:
        raw_score += 25
    elif status == VerificationStatus.PARTIALLY_VERIFIED:
        raw_score += 10
        
    # 2. Evidence Confidence (CV) Weight
    if isinstance(cv_score, (int, float)) and cv_score < 0.5:
        raw_score += 20
        
    # 3. Evidence Confidence (Forensics) Weight
    if isinstance(forensics_score, (int, float)) and forensics_score < 0.5:
        raw_score += 20
        
    # 4. Metadata Consistency Weight
    if metadata_consistent is False:
        raw_score += 15
        
    # 5. Anomalies Weight (Linear additive)
    raw_score += (len(anomalies) * 10)
    
    # Cap score at 100
    raw_score = min(raw_score, 100)
    
    # Map raw numeric score to Categorical RiskLevel
    if raw_score >= 80:
        risk_level = RiskLevel.CRITICAL
    elif raw_score >= 50:
        risk_level = RiskLevel.HIGH
    elif raw_score >= 20:
        risk_level = RiskLevel.MEDIUM
    else:
        risk_level = RiskLevel.LOW
        
    # Inspection Priority Rank (Lower number = higher priority)
    # A score of 100 maps to rank 1. A score of 0 maps to rank 100.
    inspection_priority_rank = max(1, 100 - int(raw_score))
    
    return risk_level, inspection_priority_rank
