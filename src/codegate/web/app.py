#!/usr/bin/env python3
"""
CodeGate Web Interface - Flask Application
A modern, responsive web interface for CodeGate security auditor.
"""

# Import eventlet first but don't patch threading or asyncio
# to allow Google API to work correctly
import eventlet
# Only patch socket-related operations, not thread or asyncio
eventlet.monkey_patch(socket=True, select=True, time=True)

import os
import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit

# CodeGate imports
from ..core.preprocessor import CodePreprocessor
from ..core.gemini_analyzer import GeminiSecurityAnalyzer
from ..core.static_analyzer import analyze_code_static
from ..core.risk_engine import RiskEngine
from ..utils.history import history_manager
from ..utils.config import config_manager

# Configure eventlet for async support (already monkey patched above)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'codegate-web-secret-key-change-me')

# Initialize SocketIO for real-time updates
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Global storage for active scans
active_scans: Dict[str, Dict[str, Any]] = {}

class WebAnalyzer:
    """Web-specific analyzer that provides real-time feedback"""
    
    def __init__(self, scan_id: str):
        self.scan_id = scan_id
        self.progress = 0
        
    def emit_progress(self, stage: str, progress: int, message: str = ""):
        """Emit progress update to web client"""
        socketio.emit('scan_progress', {
            'scan_id': self.scan_id,
            'stage': stage,
            'progress': progress,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
    async def analyze_code(self, code: str, file_path: str = None) -> Dict[str, Any]:
        """Analyze code with real-time progress updates"""
        try:
            # Stage 1: Preprocessing
            self.emit_progress("preprocessing", 10, "Preparing code for analysis...")
            
            try:
                preprocessor = CodePreprocessor()
                processed_data = await preprocessor.preprocess_code(code, file_path)
                
                if not processed_data["success"]:
                    raise ValueError(f"Preprocessing failed: {processed_data['error']}")
            except Exception as e:
                error_msg = f"Preprocessing error: {str(e)}"
                print(f"❌ {error_msg}")
                raise ValueError(error_msg)
            
            # Stage 2: Static Analysis
            self.emit_progress("static_analysis", 30, "Running static code analysis...")
            
            try:
                static_issues = analyze_code_static(code)
                print(f"✅ Static analysis found {len(static_issues)} issues")
            except Exception as e:
                error_msg = f"Static analysis error: {str(e)}"
                print(f"❌ {error_msg}")
                raise ValueError(error_msg)
            
            # Stage 3: Gemini Analysis
            self.emit_progress("gemini_analysis", 50, "Analyzing security vulnerabilities with Gemini...")
            
            try:
                print(f"🤖 Starting Gemini analysis...")
                gemini_analyzer = GeminiSecurityAnalyzer()
                
                # Use asyncio.wait_for with timeout to prevent hanging
                gemini_result = await asyncio.wait_for(
                    gemini_analyzer.analyze(processed_data["content"]),
                    timeout=60.0  # 60 second timeout
                )
                print(f"✅ Gemini analysis completed")
            except asyncio.TimeoutError:
                error_msg = "Gemini analysis timed out after 60 seconds"
                print(f"❌ {error_msg}")
                raise ValueError(error_msg)
            except Exception as e:
                error_msg = f"Gemini analysis error: {str(e)}"
                print(f"❌ {error_msg}")
                raise ValueError(error_msg)
            
            # Stage 4: Risk Assessment
            self.emit_progress("risk_assessment", 80, "Calculating risk scores...")
            
            try:
                risk_engine = RiskEngine(
                    gemini_findings=gemini_result or {}, 
                    total_lines=len(code.split('\n')),
                    static_findings=static_issues
                )
                
                # Generate final report
                report = risk_engine.create_report(
                    language="python",
                    file_path=file_path,
                    scan_duration=0  # Will be calculated by caller
                )
                print(f"✅ Risk assessment completed with score: {report.risk_score}")
            except Exception as e:
                error_msg = f"Risk assessment error: {str(e)}"
                print(f"❌ {error_msg}")
                raise ValueError(error_msg)
            
            # Stage 5: Complete
            self.emit_progress("complete", 100, "Analysis complete!")
            
            return {
                'success': True,
                'report': report,
                'gemini_result': gemini_result,
                'static_issues': static_issues,
                'processed_data': processed_data
            }
            
        except Exception as e:
            self.emit_progress("error", 100, f"Analysis failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

@app.route('/')
def index():
    """Main dashboard page"""
    # Get recent scans for dashboard
    recent_scans = history_manager.get_recent_scans(5)
    stats = history_manager.get_statistics()
    
    return render_template('index.html', 
                         recent_scans=recent_scans, 
                         stats=stats)

@app.route('/scan')
def scan_page():
    """Code scanning interface"""
    return render_template('scan.html')

@app.route('/history')
def history_page():
    """Scan history page"""
    limit = request.args.get('limit', 20, type=int)
    recent_scans = history_manager.get_recent_scans(limit)
    stats = history_manager.get_statistics()
    
    return render_template('history.html', 
                         scans=recent_scans, 
                         stats=stats,
                         limit=limit)

@app.route('/history/<scan_id>')
def scan_details(scan_id):
    """Detailed view of a specific scan"""
    detailed_entry = history_manager.get_scan_details(scan_id)
    
    if not detailed_entry:
        return render_template('error.html', 
                             error_message=f"Scan with ID '{scan_id}' not found"), 404
    
    return render_template('scan_details.html', 
                         entry=detailed_entry.entry,
                         report_data=detailed_entry.full_report)

@app.route('/api/scan', methods=['POST'])
def api_scan():
    """API endpoint to start a new scan"""
    try:
        data = request.get_json()
        code = data.get('code', '').strip()
        file_name = data.get('file_name', 'web_upload.py')
        
        if not code:
            return jsonify({'error': 'No code provided'}), 400
        
        # Generate unique scan ID
        scan_id = str(uuid.uuid4())
        
        # Store scan info
        active_scans[scan_id] = {
            'start_time': datetime.now(),
            'status': 'running',
            'file_name': file_name
        }
        
        # Start analysis asynchronously
        def run_analysis():
            print(f"🔍 Starting analysis for scan_id: {scan_id}")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                print(f"📊 Creating WebAnalyzer...")
                analyzer = WebAnalyzer(scan_id)
                start_time = datetime.now()
                
                print(f"🚀 Running analysis...")
                result = loop.run_until_complete(
                    analyzer.analyze_code(code, file_name)
                )
                
                print(f"✅ Analysis completed in {(datetime.now() - start_time).total_seconds()}s")
                
                scan_duration = (datetime.now() - start_time).total_seconds()
                
                if result['success']:
                    # Save to history
                    report = result['report']
                    report_data = {
                        'file_path': file_name,
                        'language': report.language,
                        'risk_score': report.risk_score,
                        'vulnerabilities': [
                            {
                                'type': v.vulnerability_type,
                                'severity': v.severity,
                                'line_number': v.line_number,
                                'code_snippet': v.code_snippet,
                                'description': v.description,
                                'impact': v.impact,
                                'remediation': v.remediation,
                                'cwe_id': v.cwe_id,
                                'tool': v.tool,
                                'issue_type': v.issue_type,
                                'category': v.category,
                                'metric_value': v.metric_value
                            } for v in report.vulnerabilities
                        ],
                        'summary': report.summary,
                        'scan_duration': scan_duration,
                        'analysis_timestamp': report.analysis_timestamp.isoformat(),
                        'dependencies_analysis': report.dependencies_analysis,
                        'total_lines': report.total_lines,
                        'static_analysis_summary': report.static_analysis_summary
                    }
                    
                    saved_scan_id = history_manager.save_scan(report_data)
                    
                    # Update active scan status
                    active_scans[scan_id].update({
                        'status': 'completed',
                        'result': result,
                        'scan_duration': scan_duration,
                        'saved_scan_id': saved_scan_id
                    })
                    
                    # Emit completion
                    socketio.emit('scan_complete', {
                        'scan_id': scan_id,
                        'saved_scan_id': saved_scan_id,
                        'report': {
                            'risk_score': report.risk_score,
                            'vulnerabilities_count': len(report.vulnerabilities),
                            'summary': report.summary,
                            'scan_duration': scan_duration
                        }
                    })
                else:
                    active_scans[scan_id].update({
                        'status': 'failed',
                        'error': result['error']
                    })
                    
                    socketio.emit('scan_error', {
                        'scan_id': scan_id,
                        'error': result['error']
                    })
                    
            except Exception as e:
                print(f"❌ Analysis exception: {e}")
                import traceback
                traceback.print_exc()
                
                active_scans[scan_id].update({
                    'status': 'failed',
                    'error': str(e)
                })
                
                socketio.emit('scan_error', {
                    'scan_id': scan_id,
                    'error': str(e)
                })
            finally:
                print(f"🔚 Closing event loop for scan_id: {scan_id}")
                loop.close()
        
        # Start analysis in background
        eventlet.spawn(run_analysis)
        
        return jsonify({
            'scan_id': scan_id,
            'status': 'started',
            'message': 'Code analysis started'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan/<scan_id>/status')
def api_scan_status(scan_id):
    """Get status of a running scan"""
    scan_info = active_scans.get(scan_id)
    
    if not scan_info:
        return jsonify({'error': 'Scan not found'}), 404
    
    return jsonify({
        'scan_id': scan_id,
        'status': scan_info['status'],
        'start_time': scan_info['start_time'].isoformat(),
        'file_name': scan_info.get('file_name'),
        'error': scan_info.get('error'),
        'saved_scan_id': scan_info.get('saved_scan_id')
    })

@app.route('/api/history')
def api_history():
    """API endpoint for scan history"""
    limit = request.args.get('limit', 20, type=int)
    recent_scans = history_manager.get_recent_scans(limit)
    
    # Convert to serializable format
    scans_data = []
    for scan in recent_scans:
        scans_data.append({
            'scan_id': scan.scan_id,
            'timestamp': scan.timestamp,
            'file_path': scan.file_path,
            'language': scan.language,
            'risk_score': scan.risk_score,
            'vulnerabilities_count': scan.vulnerabilities_count,
            'scan_duration': scan.scan_duration,
            'analysis_summary': scan.analysis_summary
        })
    
    return jsonify({
        'scans': scans_data,
        'total': len(scans_data)
    })

@app.route('/api/history/stats')
def api_history_stats():
    """API endpoint for history statistics"""
    stats = history_manager.get_statistics()
    return jsonify(stats)

@app.route('/api/history/<scan_id>')
def api_scan_details(scan_id):
    """API endpoint for detailed scan information"""
    detailed_entry = history_manager.get_scan_details(scan_id)
    
    if not detailed_entry:
        return jsonify({'error': 'Scan not found'}), 404
    
    return jsonify({
        'entry': {
            'scan_id': detailed_entry.entry.scan_id,
            'timestamp': detailed_entry.entry.timestamp,
            'file_path': detailed_entry.entry.file_path,
            'language': detailed_entry.entry.language,
            'risk_score': detailed_entry.entry.risk_score,
            'vulnerabilities_count': detailed_entry.entry.vulnerabilities_count,
            'scan_duration': detailed_entry.entry.scan_duration,
            'analysis_summary': detailed_entry.entry.analysis_summary
        },
        'full_report': detailed_entry.full_report
    })

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'message': 'Connected to CodeGate WebSocket'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

def create_app():
    """Application factory"""
    return app

if __name__ == '__main__':
    # Run the development server
    print("Starting CodeGate Web Interface...")
    print("Access the application at: http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
