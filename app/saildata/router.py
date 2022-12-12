import enum
import os
import aiofiles
from fastapi import APIRouter, File, Form, UploadFile, Depends, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.saildata.schemas import SailDataUpload, SailDataDB, SailDataUpdate
from app.saildata.models import SailData
from app.core.db import get_session
from app.users.models import User
from app.users.schemas import UserDisplay
from app.auth.jwt import get_current_user

from app.utils.roles import allow_add_news, allow_update, allow_create_admins
from app.utils.uploads import generate_path, generate_filename


class SailBoat(str, enum.Enum):
    c470 = '470'
    c420 = '420'
    laser = 'laser'


sail_router = APIRouter()


@sail_router.post('/upload', response_model=SailDataDB)
async def upload_file(
        sail_boat: SailBoat = Form(),
        wind: str | None = Form(),
        description: str | None = Form(),
        notes: str | None = Form(),
        file: UploadFile = File(...),
        db_session: AsyncSession = Depends(get_session),
        current_user: UserDisplay = Depends(get_current_user)
):
    path = generate_path(current_user.username)
    if not os.path.exists(path):
        os.makedirs(path, mode=0o666)
    name = generate_filename(file.filename)
    path = os.path.join(path, name)
    async with aiofiles.open(path, 'wb+') as f:
        content = await file.read()
        await f.write(content)
    size = os.path.getsize(path)

    sail_data = SailDataUpload(sail_boat=sail_boat,
                               wind_speed=wind,
                               description=description,
                               notes=notes,
                               file_path=path,
                               file_size=size,
                               user_id=current_user.id)
    result = await SailData.create(db_session, sail_data)
    return result


@sail_router.get('/download/my/{data_id}', response_class=FileResponse)
async def download_my_file(data_id: int,
                           session: AsyncSession = Depends(get_session),
                           current_user: UserDisplay = Depends(get_current_user)):
    file = await SailData.get_user_file(session, current_user.id, data_id)
    if not file:
        raise HTTPException(status_code=404, detail=f"File {data_id} not found")
    filename = file.file_path.split('/')[-1]
    return FileResponse(path=file.file_path, media_type='application/octet-stream', filename=filename)


@sail_router.get('/download/{data_id}', response_class=FileResponse, dependencies=[Depends(allow_update)])
async def download_file(data_id: int,
                        session: AsyncSession = Depends(get_session)):
    file = await SailData.get_by_id(session, data_id)
    if not file:
        raise HTTPException(status_code=404, detail=f"File {data_id} not found.")
    filename = file.file_path.split('/')[-1]
    return FileResponse(path=file.file_path, media_type='application/octet-stream', filename=filename)


@sail_router.get('/all', response_model=list[SailDataDB], dependencies=[Depends(allow_add_news)])
async def get_file_models(session: AsyncSession = Depends(get_session)):
    data = await SailData.get_all(session)
    return data


@sail_router.get('/my', response_model=list[SailDataDB])
async def get_my_file_models(session: AsyncSession = Depends(get_session),
                             current_user: UserDisplay = Depends(get_current_user)):
    data = await SailData.get_by_user(session, current_user.id)
    return data


@sail_router.get('/{data_id}', response_model=SailDataDB)
async def get_file_model(data_id: int, session: AsyncSession = Depends(get_session)):
    data = await SailData.get_by_id(session, data_id)
    if not data:
        raise HTTPException(status_code=404, detail="File not found")
    return data


@sail_router.get('/file/{file_id}', response_class=FileResponse, dependencies=[Depends(allow_update)])
async def get_file(file_id: int, session: AsyncSession = Depends(get_session)):
    file = await SailData.get_by_id(session, file_id)
    if not file:
        raise HTTPException(status_code=404, detail=f"File {file_id} not found.")
    return FileResponse(path=file.file_path)


@sail_router.get('/filestream/{file_id}', response_class=StreamingResponse, dependencies=[Depends(allow_update)])
async def get_file(file_id: int, session: AsyncSession = Depends(get_session)):
    file = await SailData.get_by_id(session, file_id)
    CHUNK_SIZE = 1024 * 1024
    if not file:
        raise HTTPException(status_code=404, detail=f"File {file_id} not found.")

    async def iterfile():
        async with aiofiles.open(file.file_path, 'rb') as f:
            while chunk := await f.read(CHUNK_SIZE):
                yield chunk

    filename = file.file_path.split('/')[-1]
    headers = {'Content-Disposition': f'attachment; filename="{filename}"'}
    return StreamingResponse(iterfile(), headers=headers)


@sail_router.delete('/delete/{file_id}', response_class=JSONResponse, dependencies=[Depends(allow_update)])
async def delete_file(file_id: int, session: AsyncSession = Depends(get_session)):
    data = await SailData.delete_by_id(session, file_id)

    if not data:
        return HTTPException(status_code=404, detail="File not found")
    try:
        os.remove(data)
        path = data.split('/')[:-1]
        path = '/'.join(path)
        try:
            os.rmdir(path)
        except FileNotFoundError:
            pass
        return JSONResponse(content={
            "success": True
        }, status_code=200)
    except FileNotFoundError:
        return JSONResponse(content={
            "success": False,
            "msg": "DB data delete successfull",
            "error": "File not found"
        }, status_code=200)


@sail_router.put('/update/{data_id}', response_model=SailDataDB)
async def update_data(data: SailDataUpdate,
                      session: AsyncSession = Depends(get_session),
                      current_user: UserDisplay = Depends(get_current_user)):
    sail_data = await SailData.get_by_id(session, data.id)
    if not sail_data:
        raise HTTPException(status_code=404, detail="File not found")
    if sail_data.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Permission denied! It is not your file.")

    await SailData.update(session, data)
    return await SailData.get_by_id(session, data.id)

