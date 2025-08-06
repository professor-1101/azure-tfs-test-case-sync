import asyncio
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.core.logging import get_logger
from app.services.test_case_service import TestCaseService
from app.schemas.responses import ImportResponse, AsyncImportStatusResponse

logger = get_logger(__name__)

class BackgroundTaskManager:
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self._cleanup_task = None
    
    async def _run_with_progress_update(self, task_id: str, func, *args, progress, log_msg: str):
        """Helper to run a function and update progress, preventing blocking"""
        if progress is not None:
            self.update_task_status(task_id, 'running', progress, log=log_msg)
        # Use asyncio.to_thread to prevent blocking the event loop
        result = await asyncio.to_thread(func, *args)
        return result
    
    async def start_cleanup_task(self):
        """Start background cleanup task"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_old_tasks())
    
    async def _cleanup_old_tasks(self):
        """Clean up old completed tasks"""
        while True:
            try:
                current_time = datetime.now()
                tasks_to_remove = []
                
                for task_id, task_info in self.tasks.items():
                    # Remove tasks older than 1 hour
                    if task_info.get('created_at') and \
                       current_time - task_info['created_at'] > timedelta(hours=1):
                        tasks_to_remove.append(task_id)
                
                for task_id in tasks_to_remove:
                    del self.tasks[task_id]
                    logger.info(f"Cleaned up old task: {task_id}")
                
                await asyncio.sleep(300)  # Clean up every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(60)
    
    def create_task(self, task_type: str, **kwargs) -> str:
        """Create a new background task"""
        task_id = str(uuid.uuid4())
        
        self.tasks[task_id] = {
            'id': task_id,
            'type': task_type,
            'status': 'pending',
            'progress': 0,
            'created_at': datetime.now(),
            'kwargs': kwargs,
            'result': None,
            'error': None,
            'logs': []
        }
        
        logger.info(f"Created background task: {task_id} ({task_type})")
        return task_id
    
    def update_task_status(self, task_id: str, status: str, progress: Optional[int] = None, 
                          result: Optional[ImportResponse] = None, error: Optional[str] = None,
                          log: Optional[str] = None):
        """Update task status"""
        if task_id not in self.tasks:
            logger.warning(f"Task not found: {task_id}")
            return
        
        self.tasks[task_id]['status'] = status
        if progress is not None:
            self.tasks[task_id]['progress'] = progress
        if result is not None:
            self.tasks[task_id]['result'] = result
        if error is not None:
            self.tasks[task_id]['error'] = error
        if log is not None:
            self.tasks[task_id]['logs'].append(f"[{datetime.now().strftime('%H:%M:%S')}] {log}")
        
        logger.info(f"Updated task {task_id}: {status} (progress: {progress}%)")
    
    def get_task_status(self, task_id: str) -> Optional[AsyncImportStatusResponse]:
        """Get task status"""
        if task_id not in self.tasks:
            return None
        
        task_info = self.tasks[task_id]
        return AsyncImportStatusResponse(
            task_id=task_id,
            status=task_info['status'],
            progress=task_info.get('progress'),
            result=task_info.get('result'),
            error=task_info.get('error'),
            logs=task_info.get('logs', [])
        )
    
    async def run_import_task(self, task_id: str, import_service: TestCaseService, 
                             json_data: Dict[str, Any], project_name: str, version: str):
        """Run import task in background"""
        try:
            # Start immediately with more detailed status
            self.update_task_status(task_id, 'running', 1, log="Background task execution started")
            
            # Small delay to ensure status is available immediately
            await asyncio.sleep(0.05)
            
            # Run the import (async to prevent blocking)
            result = await self._run_with_progress_update(
                task_id, import_service.import_test_cases, json_data, project_name, version,
                progress=None, log_msg="Importing test cases..."
            )
            
            self.update_task_status(task_id, 'completed', 100, result=result, 
                                  log=f"Import completed successfully. Created {result.created} test cases.")
            
        except Exception as e:
            logger.error(f"Error in background import task {task_id}: {e}")
            self.update_task_status(task_id, 'failed', error=str(e), 
                                  log=f"Import failed: {str(e)}")

# Global task manager instance
task_manager = BackgroundTaskManager() 