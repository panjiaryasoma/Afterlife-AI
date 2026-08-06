"""Enumerations defined by FEATURE_SCHEMA_FINAL_v2.0.yaml."""

from enum import StrEnum


class ValidationStatus(StrEnum):
    """Allowed values for ValidationStatus."""

    PASSED = "PASSED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


class InventoryStatus(StrEnum):
    """Allowed values for InventoryStatus."""

    HEALTHY_STOCK = "HEALTHY_STOCK"
    MONITOR = "MONITOR"
    SURPLUS_CANDIDATE = "SURPLUS_CANDIDATE"
    EXPIRED = "EXPIRED"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class SurplusSource(StrEnum):
    """Allowed values for SurplusSource."""

    CALCULATED = "CALCULATED"
    USER_DECLARED = "USER_DECLARED"
    RULE_TRIGGERED = "RULE_TRIGGERED"


class TriageConfidenceStatus(StrEnum):
    """Allowed values for TriageConfidenceStatus."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class VerificationStatus(StrEnum):
    """Allowed values for VerificationStatus."""

    LOW = "LOW"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    VERIFIED = "VERIFIED"
    PHYSICALLY_INSPECTED = "PHYSICALLY_INSPECTED"


class CoverageStatus(StrEnum):
    """Allowed values for CoverageStatus."""

    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    INSUFFICIENT_FEATURE_COVERAGE = "INSUFFICIENT_FEATURE_COVERAGE"


class SafetyStatus(StrEnum):
    """Allowed values for SafetyStatus."""

    ACCEPTABLE = "ACCEPTABLE"
    ACCEPTABLE_WITH_URGENCY = "ACCEPTABLE_WITH_URGENCY"
    UNVERIFIED = "UNVERIFIED"
    HARD_REJECT = "HARD_REJECT"


class FeasibilityStatus(StrEnum):
    """Allowed values for FeasibilityStatus."""

    FEASIBLE = "FEASIBLE"
    INFEASIBLE = "INFEASIBLE"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    UNSUPPORTED = "UNSUPPORTED"


class ModelScoringStatus(StrEnum):
    """Allowed values for ModelScoringStatus."""

    ALLOWED = "ALLOWED"
    SKIPPED = "SKIPPED"
    DEFERRED = "DEFERRED"
    BLOCKED = "BLOCKED"


class OptimizationObjective(StrEnum):
    """Allowed values for OptimizationObjective."""

    MAXIMIZE_RECOVERY_VALUE = "MAXIMIZE_RECOVERY_VALUE"
    MINIMIZE_WASTE = "MINIMIZE_WASTE"
    BALANCED = "BALANCED"


class ActionType(StrEnum):
    """Allowed values for ActionType."""

    LOCAL_DISCOUNT = "LOCAL_DISCOUNT"
    BUNDLE = "BUNDLE"
    PROMOTIONAL_BONUS = "PROMOTIONAL_BONUS"
    INTERNAL_REPURPOSE = "INTERNAL_REPURPOSE"
    INTERNAL_USE = "INTERNAL_USE"
    RETURN_TO_SUPPLIER = "RETURN_TO_SUPPLIER"
    BRANCH_TRANSFER = "BRANCH_TRANSFER"
    WHOLESALE = "WHOLESALE"
    EXTERNAL_PARTNER = "EXTERNAL_PARTNER"
    DONATION = "DONATION"
    SAFE_DISPOSAL = "SAFE_DISPOSAL"


class StorageType(StrEnum):
    """Allowed values for StorageType."""

    DRY_AMBIENT = "DRY_AMBIENT"
    ROOM_TEMPERATURE = "ROOM_TEMPERATURE"
    CHILLED = "CHILLED"
    FROZEN = "FROZEN"
    UNKNOWN = "UNKNOWN"


class StorageRequirementMode(StrEnum):
    """Allowed values for StorageRequirementMode."""

    NONE = "NONE"
    AMBIENT_ALLOWED = "AMBIENT_ALLOWED"
    CHILLED_PREFERRED = "CHILLED_PREFERRED"
    COLD_REQUIRED_FOR_QUALITY_WINDOW = "COLD_REQUIRED_FOR_QUALITY_WINDOW"
    SAFETY_CRITICAL_COLD_CHAIN = "SAFETY_CRITICAL_COLD_CHAIN"


class StorageHistoryStatus(StrEnum):
    """Allowed values for StorageHistoryStatus."""

    VERIFIED_ACCEPTABLE = "VERIFIED_ACCEPTABLE"
    VERIFIED_FAILURE = "VERIFIED_FAILURE"
    UNKNOWN = "UNKNOWN"
    UNRESOLVED = "UNRESOLVED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class ProductCondition(StrEnum):
    """Allowed values for ProductCondition."""

    GOOD = "GOOD"
    VISUALLY_NORMAL = "VISUALLY_NORMAL"
    COSMETIC_DEFECT = "COSMETIC_DEFECT"
    AMBIGUOUS = "AMBIGUOUS"
    DAMAGED = "DAMAGED"
    UNKNOWN = "UNKNOWN"


class PackagingCondition(StrEnum):
    """Allowed values for PackagingCondition."""

    INTACT = "INTACT"
    COSMETIC_LABEL_DAMAGE = "COSMETIC_LABEL_DAMAGE"
    AMBIGUOUS_DAMAGE = "AMBIGUOUS_DAMAGE"
    PRIMARY_BARRIER_DAMAGED = "PRIMARY_BARRIER_DAMAGED"
    LEAKING = "LEAKING"
    OPEN_SEAL = "OPEN_SEAL"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class DefectSeverity(StrEnum):
    """Allowed values for DefectSeverity."""

    NONE = "NONE"
    COSMETIC_ONLY = "COSMETIC_ONLY"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    SAFETY_CRITICAL = "SAFETY_CRITICAL"


class QualityInspectionStatus(StrEnum):
    """Allowed values for QualityInspectionStatus."""

    PASSED = "PASSED"
    FAILED = "FAILED"
    NOT_PERFORMED = "NOT_PERFORMED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class UrgencyLevel(StrEnum):
    """Allowed values for UrgencyLevel."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SeasonalityStatus(StrEnum):
    """Allowed values for SeasonalityStatus."""

    IN_SEASON = "IN_SEASON"
    POST_SEASON = "POST_SEASON"
    PRE_SEASON = "PRE_SEASON"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNKNOWN = "UNKNOWN"


class RegistryStatus(StrEnum):
    """Allowed values for RegistryStatus."""

    ACTIVE = "ACTIVE"
    STALE = "STALE"
    EXPIRED = "EXPIRED"
    SUSPENDED = "SUSPENDED"
    UNVERIFIED = "UNVERIFIED"


class DemandStatus(StrEnum):
    """Allowed values for DemandStatus."""

    ACTIVE = "ACTIVE"
    ZERO = "ZERO"
    STALE = "STALE"
    EXPIRED = "EXPIRED"
    UNKNOWN = "UNKNOWN"


class MatchStatus(StrEnum):
    """Allowed values for MatchStatus."""

    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class ApprovalStatus(StrEnum):
    """Allowed values for ApprovalStatus."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    ADJUSTED = "ADJUSTED"
    REJECTED = "REJECTED"


class SolverStatus(StrEnum):
    """Allowed values for SolverStatus."""

    OPTIMAL = "OPTIMAL"
    FEASIBLE = "FEASIBLE"
    INFEASIBLE = "INFEASIBLE"
    MODEL_INVALID = "MODEL_INVALID"
    UNKNOWN = "UNKNOWN"
    FALLBACK_USED = "FALLBACK_USED"


class UnitCode(StrEnum):
    """Allowed values for UnitCode."""

    UNIT = "UNIT"
    PIECE = "PIECE"
    PACK = "PACK"
    SACHET = "SACHET"
    BOTTLE = "BOTTLE"
    CAN = "CAN"
    CUP = "CUP"
    BOX = "BOX"
    TRAY = "TRAY"
    KG = "KG"
    GRAM = "GRAM"
    LITER = "LITER"
    ML = "ML"
    OTHER = "OTHER"


class BusinessType(StrEnum):
    """Allowed values for BusinessType."""

    SMALL_RETAIL = "SMALL_RETAIL"
    MEDIUM_RETAIL = "MEDIUM_RETAIL"
    SMALL_FNB = "SMALL_FNB"
    MEDIUM_FNB = "MEDIUM_FNB"
    MEDIUM_WHOLESALER = "MEDIUM_WHOLESALER"


class ProductCategory(StrEnum):
    """Allowed values for ProductCategory."""

    PACKAGED_FOOD = "PACKAGED_FOOD"
    PACKAGED_BEVERAGE = "PACKAGED_BEVERAGE"
    BAKERY = "BAKERY"
    READY_TO_EAT_MEAL = "READY_TO_EAT_MEAL"
    FROZEN_PREPARED_FOOD = "FROZEN_PREPARED_FOOD"
    CHILLED_DAIRY = "CHILLED_DAIRY"
    FRESH_PRODUCE = "FRESH_PRODUCE"
    HOUSEHOLD_CLEANING = "HOUSEHOLD_CLEANING"
    PERSONAL_CARE = "PERSONAL_CARE"
    CONDIMENT = "CONDIMENT"
    BABY_CARE = "BABY_CARE"
    CHOCOLATE = "CHOCOLATE"
    OTHER_SUPPORTED = "OTHER_SUPPORTED"


class SourceType(StrEnum):
    """Allowed values for SourceType."""

    SYNTHETIC_GENERATED = "SYNTHETIC_GENERATED"
    EVALUATION_FIXTURE = "EVALUATION_FIXTURE"
    USER_INPUT = "USER_INPUT"
    STATIC_REGISTRY = "STATIC_REGISTRY"
    STATIC_POLICY = "STATIC_POLICY"


class IntegrityStatus(StrEnum):
    """Allowed values for IntegrityStatus."""

    INTACT = "INTACT"
    COMPROMISED = "COMPROMISED"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


__all__ = [
    "ValidationStatus",
    "InventoryStatus",
    "SurplusSource",
    "TriageConfidenceStatus",
    "VerificationStatus",
    "CoverageStatus",
    "SafetyStatus",
    "FeasibilityStatus",
    "ModelScoringStatus",
    "OptimizationObjective",
    "ActionType",
    "StorageType",
    "StorageRequirementMode",
    "StorageHistoryStatus",
    "ProductCondition",
    "PackagingCondition",
    "DefectSeverity",
    "QualityInspectionStatus",
    "UrgencyLevel",
    "SeasonalityStatus",
    "RegistryStatus",
    "DemandStatus",
    "MatchStatus",
    "ApprovalStatus",
    "SolverStatus",
    "UnitCode",
    "BusinessType",
    "ProductCategory",
    "SourceType",
    "IntegrityStatus",
]
