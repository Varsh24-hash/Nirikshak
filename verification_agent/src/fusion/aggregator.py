from typing import Dict, Any
from src.schemas.input_schemas import FullVerificationRequest

def _process_payload(payload_data: Dict[str, Any], required_fields: list) -> Dict[str, Any]:
    """
    Validates a payload dictionary against a list of required fields.
    If a required field is missing or None, marks it explicitly as "missing".
    """
    processed = {}
    for field in required_fields:
        val = payload_data.get(field)
        if val is None:
            processed[field] = "missing"
        else:
            processed[field] = val
    return processed

def aggregate_data(request: FullVerificationRequest) -> Dict[str, Any]:
    """
    Aggregates the incoming multimodal data sources into a single structured format
    ("case" object) for downstream processing.
    Validates that required upstream fields are present; if not, marks them as "missing".
    """
    
    contract_required = [
        "milestone", "quantity", "unit", "deadline", 
        "specification", "source_reference"
    ]
    
    evidence_required = [
        "claim_record", "gps", "timestamp", "coordinates_in_boundary", 
        "cv_relevance_score", "detected_stage"
    ]
    
    forensics_required = [
        "is_duplicate", "similarity_score", "manipulation_flag", 
        "ai_generated_flag", "metadata_consistency_flag", "forensics_confidence_score"
    ]
    
    contract_data = _process_payload(request.contract.model_dump(mode='json'), contract_required)
    evidence_data = _process_payload(request.evidence.model_dump(mode='json'), evidence_required)
    forensics_data = _process_payload(request.forensics.model_dump(mode='json'), forensics_required)
    
    # Try to extract milestone ID for matching/tracking (assuming milestone name is the ID for now)
    milestone_id = contract_data.get("milestone")
    if milestone_id == "missing" and evidence_data.get("detected_stage") != "missing":
        milestone_id = evidence_data.get("detected_stage")
        
    case_object = {
        "milestone_id": milestone_id,
        "sources": {
            "contract": contract_data,
            "evidence": evidence_data,
            "forensics": forensics_data
        }
    }
    
    return case_object
