from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class InfrastructureOutputs(BaseModel):
    wazuh_instance_id: Optional[str] = None
    victim_instance_id: Optional[str] = None
    s3_bucket_name: Optional[str] = None
    s3_prefix: Optional[str] = None
    wazuh_instance_private_ip: Optional[str] = None
    ecr_victim_repository_url: Optional[str] = None
    raw: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_terraform_outputs(cls, outputs: Dict[str, Any]) -> "InfrastructureOutputs":
        return cls(
            wazuh_instance_id=cls._extract_value(outputs, "wazuh_instance_id"),
            victim_instance_id=cls._extract_value(outputs, "victim_instance_id"),
            s3_bucket_name=cls._extract_value(outputs, "s3_bucket_name"),
            s3_prefix=cls._extract_value(outputs, "s3_prefix"),
            wazuh_instance_private_ip=cls._extract_value(outputs, "wazuh_instance_private_ip"),
            ecr_victim_repository_url=cls._extract_value(outputs, "ecr_victim_repository_url"),
            raw=outputs or {},
        )

    @staticmethod
    def _extract_value(outputs: Dict[str, Any], key: str) -> Optional[str]:
        value = outputs.get(key)
        if isinstance(value, dict):
            return value.get("value")
        return value
