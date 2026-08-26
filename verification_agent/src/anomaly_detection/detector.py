from typing import List, Dict, Any, Callable
from pydantic import BaseModel
from datetime import datetime
from dateutil.parser import parse as parse_date

from src.schemas.output_schemas import AnomalyFinding

RuleType = Callable[[Dict[str, Any]], List[AnomalyFinding]]

def rule_claimed_progress_vs_evidence(case: Dict[str, Any]) -> List[AnomalyFinding]:
    """Detects if claimed progress percentage exceeds what evidence supports."""
    # Since our schema uses 'quantity' and CV score, we can mock a check here.
    # E.g., if quantity is very high but cv_relevance_score is very low.
    findings = []
    contract = case["sources"].get("contract", {})
    evidence = case["sources"].get("evidence", {})
    
    quantity = contract.get("quantity")
    cv_score = evidence.get("cv_relevance_score")
    
    if isinstance(quantity, (int, float)) and isinstance(cv_score, (int, float)):
        # arbitrary logic: if quantity > 100 but cv score < 0.6
        if quantity > 100 and cv_score < 0.6:
            findings.append(AnomalyFinding(
                reason=f"Claimed quantity ({quantity}) seems too high for the low CV evidence support ({cv_score}).",
                triggered_fields=["contract.quantity", "evidence.cv_relevance_score"]
            ))
    return findings

def rule_insufficient_evidence(case: Dict[str, Any]) -> List[AnomalyFinding]:
    """Detects insufficient or missing evidence for a claimed milestone."""
    findings = []
    evidence = case["sources"].get("evidence", {})
    
    missing_fields = [f for f in ["claim_record", "gps", "timestamp"] if evidence.get(f) == "missing"]
    if missing_fields:
        findings.append(AnomalyFinding(
            reason=f"Insufficient evidence. Missing fields: {', '.join(missing_fields)}.",
            triggered_fields=[f"evidence.{f}" for f in missing_fields]
        ))
    return findings

def rule_duplicate_evidence(case: Dict[str, Any]) -> List[AnomalyFinding]:
    """Detects if evidence is flagged as duplicate/near-duplicate."""
    findings = []
    forensics = case["sources"].get("forensics", {})
    
    is_dup = forensics.get("is_duplicate")
    sim_score = forensics.get("similarity_score")
    
    if is_dup is True:
        findings.append(AnomalyFinding(
            reason=f"Evidence flagged as duplicate (Similarity: {sim_score}).",
            triggered_fields=["forensics.is_duplicate", "forensics.similarity_score"]
        ))
    return findings

def rule_gps_boundary(case: Dict[str, Any]) -> List[AnomalyFinding]:
    """Detects if GPS coordinates are outside the project boundary."""
    findings = []
    evidence = case["sources"].get("evidence", {})
    
    in_boundary = evidence.get("coordinates_in_boundary")
    if in_boundary is False:
        findings.append(AnomalyFinding(
            reason="GPS coordinates are outside the approved project boundary.",
            triggered_fields=["evidence.coordinates_in_boundary", "evidence.gps"]
        ))
    return findings

def rule_timestamp_consistency(case: Dict[str, Any]) -> List[AnomalyFinding]:
    """Detects if capture timestamp is inconsistent with claim date or milestone deadline."""
    findings = []
    contract = case["sources"].get("contract", {})
    evidence = case["sources"].get("evidence", {})
    
    deadline = contract.get("deadline")
    timestamp = evidence.get("timestamp")
    
    if deadline != "missing" and timestamp != "missing" and deadline and timestamp:
        try:
            d_date = parse_date(deadline) if isinstance(deadline, str) else deadline
            t_date = parse_date(timestamp) if isinstance(timestamp, str) else timestamp
            
            # If evidence was captured after the deadline
            if t_date > d_date:
                findings.append(AnomalyFinding(
                    reason=f"Evidence timestamp ({t_date}) is past the contract deadline ({d_date}).",
                    triggered_fields=["evidence.timestamp", "contract.deadline"]
                ))
        except Exception:
            pass # Ignore parsing errors for now
            
    # Also flag if metadata consistency is false
    forensics = case["sources"].get("forensics", {})
    if forensics.get("metadata_consistency_flag") is False:
        findings.append(AnomalyFinding(
            reason="Image EXIF metadata timestamp/location is inconsistent with the claim.",
            triggered_fields=["forensics.metadata_consistency_flag"]
        ))
        
    return findings

def rule_forensics_flags(case: Dict[str, Any]) -> List[AnomalyFinding]:
    """Detects forensics manipulation or AI-generation flags."""
    findings = []
    forensics = case["sources"].get("forensics", {})
    
    if forensics.get("manipulation_flag") is True:
        findings.append(AnomalyFinding(
            reason="Forensics flagged possible image manipulation.",
            triggered_fields=["forensics.manipulation_flag"]
        ))
        
    if forensics.get("ai_generated_flag") is True:
        findings.append(AnomalyFinding(
            reason="Forensics flagged image as potentially AI-generated.",
            triggered_fields=["forensics.ai_generated_flag"]
        ))
        
    return findings

def rule_cv_relevance(case: Dict[str, Any]) -> List[AnomalyFinding]:
    """Detects low CV relevance score for the claimed construction stage."""
    findings = []
    evidence = case["sources"].get("evidence", {})
    
    cv_score = evidence.get("cv_relevance_score")
    if isinstance(cv_score, (int, float)) and cv_score < 0.5:
        findings.append(AnomalyFinding(
            reason=f"Computer Vision relevance score is suspiciously low ({cv_score}).",
            triggered_fields=["evidence.cv_relevance_score", "evidence.detected_stage"]
        ))
        
    return findings

# Registry of all anomaly detection rules
ANOMALY_RULES: List[RuleType] = [
    rule_claimed_progress_vs_evidence,
    rule_insufficient_evidence,
    rule_duplicate_evidence,
    rule_gps_boundary,
    rule_timestamp_consistency,
    rule_forensics_flags,
    rule_cv_relevance
]

def detect_anomalies(case_object: Dict[str, Any]) -> List[AnomalyFinding]:
    """
    Runs all registered anomaly detection rules against the fused case object.
    """
    all_findings = []
    for rule in ANOMALY_RULES:
        all_findings.extend(rule(case_object))
        
    return all_findings
