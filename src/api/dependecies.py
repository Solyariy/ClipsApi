from fastapi import Request


def get_speach_semaphore(request: Request):
    return request.app.state.speach_semaphore


def get_httpx_client(request: Request):
    return request.app.state.httpx_client


def get_gcs_bucket(request: Request):
    return request.app.state.gcs_bucket
