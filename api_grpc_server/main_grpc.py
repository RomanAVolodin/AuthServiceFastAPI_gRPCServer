import asyncio
import logging

import grpc

from core.grpc import users_pb2_grpc
from core.settings import settings
from fastapi import FastAPI, Depends

from services.grpc.users import UsersFetcher

app = FastAPI(dependencies=[Depends(UsersFetcher)])


async def serve() -> None:
    server = grpc.aio.server()

    users_pb2_grpc.add_DetailerServicer_to_server(UsersFetcher(), server)

    server.add_insecure_port(f'[::]:{settings.grpc_port}')
    logging.info('Starting server on %s', '[::]:50051')
    await server.start()
    await server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
