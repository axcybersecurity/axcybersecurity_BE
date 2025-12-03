# from fastapi import APIRouter, Depends, HTTPException, status, Query
# from dependencies.auth_deps import get_current_user
# from services.filestation_service import FileStationService
# from models.schemas import FileListResponse

# router = APIRouter(prefix="/files", tags=["파일 관리"])

# @router.get("/list", response_model=FileListResponse)
# async def list_files(
#     folder_path: str = Query("/", description="조회할 폴더 경로"),
#     current_user: dict = Depends(get_current_user)
# ):
#     async with FileStationService() as fs_service:
#         return await fs_service.list_files(folder_path)
