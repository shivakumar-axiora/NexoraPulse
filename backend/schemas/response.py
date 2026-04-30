from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

class ResponseCreate(BaseModel):
    survey_id: UUID
    session_token: Optional[str] = None
    respondent_email: Optional[str] = None
    status: str = "in_progress"
    resp_metadata: Optional[dict] = Field(None, validation_alias="metadata_dict", serialization_alias="metadata")
    
    # Demographics
    age: Optional[str] = Field(None, description="Age range (e.g., '18-24', '25-34')")
    gender: Optional[str] = Field(None, description="Gender (e.g., 'Male', 'Female', 'Non-binary', 'Prefer not to say')")
    city: Optional[str] = None
    occupation: Optional[str] = Field(None, description="Occupation (e.g., 'Student', 'Professional', 'Unemployed', 'Retired')")

    model_config = {"populate_by_name": True}

class ResponseUpdate(BaseModel):
    respondent_email: Optional[str] = None
    status: Optional[str] = None
    last_saved_at: Optional[datetime] = None
    resp_metadata: Optional[dict] = Field(None, validation_alias="metadata_dict", serialization_alias="metadata")
    
    # Demographics
    age: Optional[str] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    occupation: Optional[str] = None

    model_config = {"populate_by_name": True}

class AnswerIn(BaseModel):
    question_id: UUID
    answer_value: Optional[str] = None
    answer_json: Optional[Any] = None

class AnswerOut(BaseModel):
    id: UUID
    response_id: UUID
    question_id: UUID
    answer_value: Optional[str] = None
    answer_json: Optional[Any] = None

    model_config = {"from_attributes": True}

class ResponseOut(BaseModel):
    id: UUID
    survey_id: UUID
    session_token: Optional[str] = None
    respondent_email: Optional[str] = None
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_saved_at: Optional[datetime] = None
    resp_metadata: Optional[dict] = Field(None, validation_alias="metadata_dict", serialization_alias="metadata")
    
    # Demographics
    age: Optional[str] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    occupation: Optional[str] = None
    client_ip: Optional[str] = None

    survey_answers: List = []

    model_config = {"from_attributes": True, "populate_by_name": True}

class SubmitResponse(BaseModel):
    action: str = "submit"
    response_id: UUID
    resp_metadata: Optional[dict] = Field(None, validation_alias="metadata_dict", serialization_alias="metadata")

    model_config = {"populate_by_name": True}
