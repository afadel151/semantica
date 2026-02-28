from fastapi import  File, UploadFile
from fastapi import APIRouter
from sqlmodel import select, delete, func, col
from typing import Any, List

router = APIRouter(prefix="/rdf", tags=["rdf"])
# request and response models will be available at app/models/rdf.py

# global statistics 
@router.get('/stats')
def get_stats():
    return 

# get list of uploaded graph files
@router.get('/files')
def get_files():
    return


# get a specific graph file
@router.get('/{file_id}')
def get_file():
    return

# get a file's statistics
@router.get('/{file_id}/stats')
def get_file_stats():
    return

# delete graph file from storage and db
@router.delete('/{file_id}')
def delete_file():
    return