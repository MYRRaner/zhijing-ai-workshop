import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_service.app import app
from ai_service.config import AI_SERVICE_HOST, AI_SERVICE_PORT

if __name__ == '__main__':
    app.run(host=AI_SERVICE_HOST, port=AI_SERVICE_PORT, debug=False)
