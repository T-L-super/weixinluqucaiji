# API 路由模块初始化文件
# 完成时间：2026-03-18 23:30 UTC

from .records import router as records_router
from .tasks import router as tasks_router
from .stats import router as stats_router

__all__ = ["records_router", "tasks_router", "stats_router"]
