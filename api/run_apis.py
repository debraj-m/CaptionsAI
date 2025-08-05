"""
Script to run both CaptionsAI APIs (Caption and Hashtag)
"""

import subprocess
import sys
import time
import os
from multiprocessing import Process
import uvicorn
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


def run_caption_api():
    """Run the Caption API server"""
    # Change to the api directory
    os.chdir(Path(__file__).parent)
    uvicorn.run(
        "caption_api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )


def run_hashtag_api():
    """Run the Hashtag API server"""
    # Change to the api directory  
    os.chdir(Path(__file__).parent)
    uvicorn.run(
        "hashtag_api:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    print("Starting CaptionsAI APIs...")
    print("Caption API will run on: http://localhost:8000")
    print("Hashtag API will run on: http://localhost:8001")
    print("Press Ctrl+C to stop both servers")
    
    # Start both APIs as separate processes
    try:
        caption_process = Process(target=run_caption_api)
        hashtag_process = Process(target=run_hashtag_api)
        
        caption_process.start()
        time.sleep(2)  # Give first server time to start
        hashtag_process.start()
        
        # Wait for both processes
        caption_process.join()
        hashtag_process.join()
        
    except KeyboardInterrupt:
        print("\nStopping servers...")
        caption_process.terminate()
        hashtag_process.terminate()
        caption_process.join()
        hashtag_process.join()
        print("Servers stopped.")
