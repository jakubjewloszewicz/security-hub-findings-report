from dataclasses import dataclass
from typing import Dict

@dataclass
class ControlStats:
    """Statistics for control compliance status."""
    passed: int
    failed: int
    no_data: int
    unknown: int
    disabled: int
    total: int
    
    @property
    def security_score(self) -> int:
        """Calculate security score percentage."""
        return int((self.passed / self.total * 100)) if self.total > 0 else 0


@dataclass
class SeverityCounts:
    """Counts by severity level."""
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0


@dataclass
class FailedControl:
    """Failed control with metadata."""
    control_id: str
    severity: str
    title: str
    doc_url: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convert FailedControl to dictionary."""
        return {
            'control_id': self.control_id,
            'severity': self.severity,
            'title': self.title,
            'doc_url': self.doc_url
        }