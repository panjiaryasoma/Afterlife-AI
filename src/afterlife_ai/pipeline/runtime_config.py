"""Typed loader for Afterlife AI runtime configuration."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field
from yaml.nodes import MappingNode

from afterlife_ai.contracts.enums import (
    ActionType,
    BusinessType,
    ProductCategory,
)


class _UniqueKeySafeLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""

    def construct_mapping(
        self,
        node: MappingNode,
        deep: bool = False,
    ) -> dict[Any, Any]:
        mapping = {}

        for key_node, value_node in node.value:
            key = self.construct_object(
                key_node,
                deep=deep,
            )

            if key in mapping:
                raise ValueError(
                    f"Duplicate YAML key: {key}"
                )

            value = self.construct_object(
                value_node,
                deep=deep,
            )

            mapping[key] = value

        return mapping


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
    manifest_path: Path


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


class InternalRepurposeCapability(BaseModel):
    """Static internal-repurpose limits for the MVP."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    maximum_quantity: Decimal = Field(
        ge=Decimal("0")
    )
    estimated_completion_hours: Decimal = Field(
        ge=Decimal("0")
    )
    capacity_scope: Literal[
        "SHARED_ACROSS_ALL_PLANNING_LOTS"
    ]
    destination_id: str
    destination_type: str
    selling_price_per_unit: Decimal = Field(
        ge=Decimal("0")
    )
    direct_action_cost: Decimal = Field(
        ge=Decimal("0")
    )


class BundleCapability(BaseModel):
    """Static bundle limits for the MVP."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    maximum_quantity: Decimal = Field(
        ge=Decimal("0")
    )
    estimated_completion_hours: Decimal = Field(
        ge=Decimal("0")
    )
    supported_categories: list[ProductCategory]
    supported_source_skus: list[str]
    destination_id: str
    destination_type: str
    selling_price_per_unit: Decimal = Field(
        ge=Decimal("0")
    )
    direct_action_cost: Decimal = Field(
        ge=Decimal("0")
    )


class LocalDiscountCapability(BaseModel):
    """Static local-discount parameters for the MVP."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    price_fraction_of_normal: Decimal = Field(
        gt=Decimal("0"),
        le=Decimal("1"),
    )
    estimated_completion_hours: Decimal = Field(
        ge=Decimal("0")
    )
    destination_id: str
    destination_type: str
    direct_action_cost: Decimal = Field(
        ge=Decimal("0")
    )


class SafeDisposalCapability(BaseModel):
    """Static safe-disposal parameters for the MVP."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    estimated_completion_hours: Decimal = Field(
        ge=Decimal("0")
    )

class RuntimeCapabilityConfig(BaseModel):
    """Static business capabilities used by local MVP planning."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    profile_version: str
    provenance: str
    real_world_validated: bool

    supported_actions: dict[ActionType, bool]

    internal_repurpose: InternalRepurposeCapability
    bundle: BundleCapability
    local_discount: LocalDiscountCapability
    safe_disposal: SafeDisposalCapability


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
    capabilities: RuntimeCapabilityConfig


def load_runtime_config(
    path: Path,
) -> RuntimeConfig:
    """Load and validate the typed runtime YAML configuration."""

    if not path.is_file():
        raise FileNotFoundError(
            f"Runtime config tidak ditemukan: {path}"
        )

    payload = yaml.load(
        path.read_text(
            encoding="utf-8"
        ),
        Loader=_UniqueKeySafeLoader,
    )

    if not isinstance(payload, dict):
        raise ValueError(
            "Runtime config harus berupa YAML mapping."
        )

    return RuntimeConfig.model_validate(payload)


__all__ = [
    "BundleCapability",
    "InternalRepurposeCapability",
    "LocalDiscountCapability",
    "RuntimeCapabilityConfig",
    "RuntimeConfig",
    "RuntimeTriageConfig",
    "SafeDisposalCapability",
    "TriageCategoryPolicy",
    "load_runtime_config",
]








