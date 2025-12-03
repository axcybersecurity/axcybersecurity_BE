# import httpx

# import os
# from typing import List, Optional
# from fastapi import HTTPException, status
# from models.schemas import FileItem, FileListResponse

# class FileStationService:
#     def __init__(self):
#         self.nas_url = "https://pnu-infosec.tw4.quickconnect.to"
#         self.username = os.getenv("NAS_USERNAME", "")
#         self.password = os.getenv("NAS_PASSWORD", "")
#         self.session_id: Optional[str] = None
#         self.client = httpx.AsyncClient(verify=False, timeout=30.0, follow_redirects=True)
    
#     async def __aenter__(self):
#         return self
    
#     async def __aexit__(self, exc_type, exc_val, exc_tb):
#         await self.client.aclose()
    
#     async def get_sid(self) -> str:
#         """SID 발급받기"""
#         auth_url = f"{self.nas_url}/webapi/auth.cgi"
#         params = {
#             "api": "SYNO.API.Auth",
#             "version": "6",
#             "method": "login",
#             "account": self.username,
#             "passwd": self.password,
#             "session": "FileStation",
#             "format": "sid"
#         }
        
#         resp = await self.client.get(auth_url, params=params)
        
#         # 응답 내용 확인
#         print(f"응답 상태: {resp.status_code}")
#         print(f"응답 내용: {resp.text[:300]}")
        
#         try:
#             data = resp.json()
#         except Exception as e:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=f"JSON 파싱 실패: {str(e)} | 응답: {resp.text[:200]}"
#             )
        
#         if data.get("success"):
#             sid = data.get("data", {}).get("sid")
#             if sid:
#                 self.session_id = sid
#                 return sid
        
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="SID 발급 실패"
#         )
    
#     async def list_files(self, folder_path: str = "/") -> FileListResponse:
#         """파일 목록 조회"""
#         if not self.session_id:
#             await self.get_sid()
        
#         if folder_path == "/":
#             # 공유폴더 목록
#             url = f"{self.nas_url}/webapi/entry.cgi"
#             params = {
#                 "api": "SYNO.FileStation.List",
#                 "version": "2",
#                 "method": "list_share",
#                 "_sid": self.session_id
#             }
#         else:
#             # 특정 폴더 내부
#             url = f"{self.nas_url}/webapi/entry.cgi"
#             params = {
#                 "api": "SYNO.FileStation.List",
#                 "version": "2",
#                 "method": "list",
#                 "folder_path": folder_path,
#                 "_sid": self.session_id
#             }
        
#         resp = await self.client.get(url, params=params)
#         data = resp.json()
        
#         if not data.get("success"):
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"파일 목록 조회 실패: {data.get('error', {})}"
#             )
        
#         files_data = data.get("data", {}).get("files", [])
#         files = []
#         for item in files_data:
#             files.append(FileItem(
#                 path=item.get("path", ""),
#                 name=item.get("name", ""),
#                 isdir=item.get("isdir", False),
#                 size=item.get("additional", {}).get("size"),
#                 owner=item.get("additional", {}).get("owner", {}).get("user"),
#                 time=item.get("additional", {}).get("time", {}).get("mtime")
#             ))
        
#         return FileListResponse(
#             files=files,
#             total=len(files),
#             offset=0,
#             limit=100
#         )
