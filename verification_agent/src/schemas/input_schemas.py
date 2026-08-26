from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, Optional

class ContractPayload(BaseModel):
    milestone: Optional[str] = Field(None, description="The name of the milestone")
    quantity: Optional[float] = Field(None, description="Quantity of the work done")
    unit: Optional[str] = Field(None, description="Unit of measurement for the quantity (e.g., cubic meters, percentage)")
    deadline: Optional[datetime] = Field(None, description="Deadline for the milestone")
    specification: Optional[str] = Field(None, description="Technical specifications or requirements")
    source_reference: Optional[str] = Field(None, description="Reference ID or URL to the original contract document")

class EvidencePayload(BaseModel):
    claim_record: Optional[Dict[str, Any]] = Field(None, description="Raw claim record data from the contractor")
    gps: Optional[str] = Field(None, description="GPS coordinates as a string (e.g., 'latitude, longitude')")
    timestamp: Optional[datetime] = Field(None, description="Timestamp of when the evidence was captured")
    coordinates_in_boundary: Optional[bool] = Field(None, description="True if the GPS coordinates are within the project boundary")
    cv_relevance_score: Optional[float] = Field(None, description="Computer Vision relevance score (0.0 to 1.0)")
    detected_stage: Optional[str] = Field(None, description="The stage detected by the Computer Vision model")

class ForensicsPayload(BaseModel):
    is_duplicate: Optional[bool] = Field(None, description="True if the evidence image is a duplicate of a past submission")
    similarity_score: Optional[float] = Field(None, description="Similarity score with previous images (0.0 to 1.0)")
    manipulation_flag: Optional[bool] = Field(None, description="True if image manipulation was detected")
    ai_generated_flag: Optional[bool] = Field(None, description="True if the image is suspected to be AI-generated")
    metadata_consistency_flag: Optional[bool] = Field(None, description="True if the EXIF metadata is consistent with the claim")
    forensics_confidence_score: Optional[float] = Field(None, description="Overall confidence score from the forensics model (0.0 to 1.0)")

class FullVerificationRequest(BaseModel):
    """Schema for an endpoint that receives all three payloads at once (for testing/simplification)"""
    contract: ContractPayload
    evidence: EvidencePayload
    forensics: ForensicsPayload
