"""Typed loader for Afterlife AI runtime configuration."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

from afterlife_ai.contracts.enums import (
    BusinessType,
    ProductCategory,
)


class RuntimeSourceOfTruth(BaseModel):
    """References to locked runtime source documents."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    feature_schema: Path
    domain_rules: Path


class RuntimeModelConfig(BaseModel):
    """Selected production model runtime paths."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    artifact_path: Path
    feature_schema_path: Path


class RuntimeBusinessConfig(BaseModel):
    """Business context used by the local MVP runtime."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    business_type: BusinessType


class TriageCategoryPolicy(BaseModel):
    """Static triage parameters for one supported category."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    effective_sales_window_days: Decimal = Field(
        ge=Decimal("0")
    )
    expiry_monitor_threshold_days: int = Field(ge=0)
    cold_chain_evidence_required: bool
    provenance: str


class RuntimeTriageConfig(BaseModel):
    """Deterministic triage runtime configuration."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    policy_version: str
    declared_surplus_allowed: bool
    unsupported_category_behavior: Literal["NEEDS_REVIEW"]

    category_policies: dict[
        ProductCategory,
        TriageCategoryPolicy,
    ]


class RuntimeConfig(BaseModel):
    """Complete local synchronous MVP configuration."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    config_name: str
    version: str
    status: Literal["MVP_STATIC_DEFAULTS"]

    runtime_mode: Literal["LOCAL_SYNCHRONOUS"]

    source_of_truth: RuntimeSourceOfTruth
    claim_boundary: str

    model: RuntimeModelConfig
    business: RuntimeBusinessConfig
    triage: RuntimeTriageConfig


def load_runtime_config(
    path: Path,
) -> RuntimeConfig:
    """Load and validate the typed runtime YAML configuration."""

    if not path.is_file():
        raise FileNotFoundError(
            f"Runtime config tidak ditemukan: {path}"
        )

    payload = yaml.safe_load(
        path.read_text(encoding="utf-8")
    )

    if not isinstance(payload, dict):
        raise ValueError(
            "Runtime config harus berupa YAML mapping."
        )

    return RuntimeConfig.model_validate(payload)


__all__ = [
    "RuntimeConfig",
    "RuntimeTriageConfig",
    "TriageCategoryPolicy",
    "load_runtime_config",
]