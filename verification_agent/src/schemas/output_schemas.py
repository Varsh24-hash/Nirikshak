from pydantic import BaseModel, Field
from typing import List
from enum import Enum

class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    DISPUTED = "DISPUTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AnomalyFinding(BaseModel):
    reason: str = Field(..., description="The reason for the anomaly")
    triggered_fields: List[str] = Field(..., description="The specific fields that triggered this anomaly")

class VerificationOutput(BaseModel):
    verification_status: VerificationStatus = Field(..., description="Overall decision of the verification process")
    evidence_confidence: float = Field(..., description="Calculated confidence score based on multimodal evidence (0.0 to 1.0)")
    explanation: List[str] = Field(..., description="Human-readable explanations for the decision")
    risk_level: RiskLevel = Field(..., description="Calculated risk level of the claim")
    inspection_priority_rank: int = Field(..., description="Priority rank for manual inspection (lower number = higher priority)")
    contributing_factors: List[AnomalyFinding] = Field(..., description="Key factors that contributed to the risk level and status")
