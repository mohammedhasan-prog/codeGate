#!/usr/bin/env python3
"""
CodeGate Web Launcher
Starts the Flask web interface for CodeGate
"""

import sys
import os
import click
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from codegate.web.app import app, socketio
    from codegate.utils.config import config_manager
except ImportError as e:
    print(f"Error importing CodeGate modules: {e}")
    print("Make sure CodeGate is properly installed.")
    sys.exit(1)

@click.command()
@click.option('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
@click.option('--port', default=5000, help='Port to bind to (default: 5000)')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--public', is_flag=True, help='Allow external connections (binds to 0.0.0.0)')
def main(host, port, debug, public):
    """Launch CodeGate Web Interface"""
    
    # Check if config exists
    try:
        api_key = config_manager.get("gemini.api_key")
        if not api_key or api_key.startswith("${"):
            print("⚠️  CodeGate configuration incomplete!")
            print("Please set your Gemini API key:")
            print("export GEMINI_API_KEY='your-api-key-here'")
            print("Or edit ~/.codegate/config.yaml")
            sys.exit(1)
    except Exception as e:
        print(f"⚠️  Configuration error: {e}")
        print("Please run 'codegate' first to set up configuration.")
        sys.exit(1)
    
    # Adjust host if public flag is set
    if public:
        host = '0.0.0.0'
        print("⚠️  Warning: Binding to all interfaces. This allows external connections.")
    
    print("🚀 Starting CodeGate Web Interface...")
    print(f"📍 URL: http://{host if host != '0.0.0.0' else 'localhost'}:{port}")
    print("💡 Use Ctrl+C to stop the server")
    
    if debug:
        print("🐛 Debug mode enabled")
    
    try:
        # Start the Flask-SocketIO server
        socketio.run(
            app,
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug
        )
    except KeyboardInterrupt:
        print("\n👋 CodeGate Web Interface stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
