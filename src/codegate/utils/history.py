import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from .config import config_manager


@dataclass
class HistoryEntry:
    """Represents a single scan history entry."""
    timestamp: str
    file_path: Optional[str]
    language: str
    risk_score: int
    vulnerabilities_count: int
    scan_duration: float
    analysis_summary: str
    scan_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HistoryEntry':
        """Create HistoryEntry from dictionary."""
        return cls(**data)


@dataclass 
class DetailedHistoryEntry:
    """Represents a detailed scan history entry with full report."""
    entry: HistoryEntry
    full_report: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'entry': self.entry.to_dict(),
            'full_report': self.full_report
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DetailedHistoryEntry':
        """Create DetailedHistoryEntry from dictionary."""
        return cls(
            entry=HistoryEntry.from_dict(data['entry']),
            full_report=data['full_report']
        )


class HistoryManager:
    """Manages scan history storage and retrieval."""
    
    def __init__(self):
        self.history_path = self._get_history_path()
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _get_history_path(self) -> Path:
        """Get the history file path from config."""
        history_path_str = config_manager.get("settings.history_path", "~/.codegate/history.json")
        return Path(os.path.expanduser(history_path_str))
    
    def is_enabled(self) -> bool:
        """Check if history saving is enabled."""
        return config_manager.get("settings.save_history", True)
    
    def save_scan(self, report_data: Dict[str, Any]) -> Optional[str]:
        """
        Save a scan result to history.
        
        Args:
            report_data: Complete report data including SecurityReport object as dict
            
        Returns:
            scan_id if saved successfully, None otherwise
        """
        if not self.is_enabled():
            return None
        
        try:
            # Generate unique scan ID
            scan_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            
            # Create history entry
            entry = HistoryEntry(
                timestamp=datetime.now().isoformat(),
                file_path=report_data.get('file_path'),
                language=report_data.get('language', 'unknown'),
                risk_score=report_data.get('risk_score', 0),
                vulnerabilities_count=len(report_data.get('vulnerabilities', [])),
                scan_duration=report_data.get('scan_duration', 0.0),
                analysis_summary=report_data.get('summary', 'No summary available'),
                scan_id=scan_id
            )
            
            # Create detailed entry
            detailed_entry = DetailedHistoryEntry(
                entry=entry,
                full_report=report_data
            )
            
            # Load existing history
            history_data = self._load_history_data()
            
            # Add new entry
            history_data['entries'].append(detailed_entry.to_dict())
            
            # Keep only the last 100 entries to prevent file from getting too large
            if len(history_data['entries']) > 100:
                history_data['entries'] = history_data['entries'][-100:]
            
            # Save updated history
            self._save_history_data(history_data)
            
            return scan_id
            
        except Exception as e:
            print(f"Failed to save scan history: {e}")
            return None
    
    def get_recent_scans(self, limit: int = 20) -> List[HistoryEntry]:
        """Get recent scan entries."""
        try:
            history_data = self._load_history_data()
            entries = []
            
            for entry_data in reversed(history_data['entries'][-limit:]):
                entries.append(HistoryEntry.from_dict(entry_data['entry']))
            
            return entries
            
        except Exception as e:
            print(f"Failed to load scan history: {e}")
            return []
    
    def get_scan_details(self, scan_id: str) -> Optional[DetailedHistoryEntry]:
        """Get detailed scan information by scan ID."""
        try:
            history_data = self._load_history_data()
            
            for entry_data in history_data['entries']:
                if entry_data['entry']['scan_id'] == scan_id:
                    return DetailedHistoryEntry.from_dict(entry_data)
            
            return None
            
        except Exception as e:
            print(f"Failed to load scan details: {e}")
            return None
    
    def clear_history(self) -> bool:
        """Clear all scan history."""
        try:
            self._save_history_data({'entries': []})
            return True
        except Exception as e:
            print(f"Failed to clear history: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get history statistics."""
        try:
            history_data = self._load_history_data()
            entries = [HistoryEntry.from_dict(entry['entry']) for entry in history_data['entries']]
            
            if not entries:
                return {'total_scans': 0}
            
            total_scans = len(entries)
            total_vulnerabilities = sum(entry.vulnerabilities_count for entry in entries)
            avg_risk_score = sum(entry.risk_score for entry in entries) / total_scans
            
            # Risk distribution
            risk_distribution = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
            for entry in entries:
                if entry.risk_score < 25:
                    risk_distribution['low'] += 1
                elif entry.risk_score < 50:
                    risk_distribution['medium'] += 1
                elif entry.risk_score < 75:
                    risk_distribution['high'] += 1
                else:
                    risk_distribution['critical'] += 1
            
            return {
                'total_scans': total_scans,
                'total_vulnerabilities': total_vulnerabilities,
                'average_risk_score': round(avg_risk_score, 1),
                'risk_distribution': risk_distribution
            }
            
        except Exception as e:
            print(f"Failed to get statistics: {e}")
            return {'total_scans': 0}
    
    def _load_history_data(self) -> Dict[str, Any]:
        """Load history data from file."""
        if not self.history_path.exists():
            return {'entries': []}
        
        try:
            with open(self.history_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {'entries': []}
    
    def _save_history_data(self, data: Dict[str, Any]) -> None:
        """Save history data to file."""
        with open(self.history_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)


# Global history manager instance
history_manager = HistoryManager()
