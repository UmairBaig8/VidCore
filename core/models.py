from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Event:
    timestamp: str
    event_type: str
    description: str
    confidence: float = 0.0
    metadata: Optional[Dict] = None


@dataclass
class AnalysisResult:
    timeline: List[Event] = field(default_factory=list)
    summary: str = ""
    report_path: str = ""

    @property
    def event_count(self):
        return len(self.timeline)
