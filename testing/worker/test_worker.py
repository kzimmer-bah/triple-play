from collections import deque
import pytest
import json 

import logging

import aioredis
import asyncio
import aiohttp

from worker.worker import Worker

#from common.message_types import message_dumps, message_loads, NodeStatusMessage, WorkflowStatusMessage, StatusEnum, JSONPatch, JSONPatchOps
from common.config import config
from common.helpers import connect_to_redis_pool
from common.workflow_types import workflow_load, Node, Action, Condition, Transform, Trigger, ParameterVariant, Workflow, workflow_dumps, workflow_loads, workflow_dump, ConditionException

from contextlib import asynccontextmanager

import birdisle.aioredis

logging.basicConfig(level=logging.INFO, format="{asctime} - {name} - {levelname}:{message}", style='{')
logger = logging.getLogger("TEST WORKER")

#####################
##### FIXTURES ######
#####################
@pytest.fixture
@asynccontextmanager
async def server():
    server = birdisle.Server()
    try:
        yield server
    finally:
        server.close()


@pytest.fixture
@asynccontextmanager
async def redis(server):
    redis = await birdisle.aioredis.create_redis(server)
    with open("testing/util/workflow.json") as fp:
        wf_json = json.load(fp)
        await redis.lpush(config["REDIS"]["workflow_q"], json.dumps(wf_json))
    try:
        yield redis
    finally:
        redis.close()
        await redis.wait_closed()
        logger.info("Birdisle redis connection closed.")


@pytest.fixture
@asynccontextmanager
async def session():
    session = aiohttp.ClientSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def worker(session, redis):
    with open("testing/util/workflow.json") as fp2:
        wf = workflow_load(fp2)
    worker = Worker(redis = redis, workflow = wf, session = session)
    return worker


#####################
#### ASYNC TESTS ####
#####################

def test_init(worker, redis, session):
    with open("testing/util/workflow.json") as fp2:
            wf = workflow_load(fp2)
    assert worker.redis == redis
    assert worker.workflow == wf
    assert worker.session == session
    assert worker.start_action == worker.workflow.start
    assert worker.start_action == wf.start
    assert worker.in_process == {}
    assert worker.accumulator == {}


#get_workflow test - DONE
@pytest.mark.asyncio
async def test_get_workflow(redis, worker):
    with open("testing/util/workflow.json") as fp:
        wf_json = json.load(fp)
        x = json.dumps(wf_json)

    #check initial redis queue contents
    assert (await redis.lpop("workflow-queue")).decode("utf-8") == x
    await redis.lpush("workflow-queue", x)
    assert await redis.lpop("workflows-in-process") == None

    try:
        async for i in worker.get_workflow(redis):
            #check for workflow movement in redis (workflow-queue -> workflows-in-process)
            assert await redis.lpop("workflow-queue") == None
            assert (await redis.lpop("workflows-in-process")).decode("utf-8") == x
    except SystemExit:
        assert True
    except:
        assert False


#test schedule_node for action nodes exclusively
@pytest.mark.asyncio
async def test_schedule_action_node(redis, worker):
    visited = {worker.start_action}
    queue = deque([worker.start_action])
    tasks = set()

    while queue:
        node = queue.pop()
        parents = {n.id_: n for n in worker.workflow.predecessors(node)} if node is not worker.start_action else {}
        parent_nodes =  {n: n for n in worker.workflow.predecessors(node)} if node is not worker.start_action else {} 
        children = {n.id_: n for n in worker.workflow.successors(node)}
        worker.in_process[node.id_] = node
        
        logger.info(worker.accumulator)

        if isinstance(node, Action):
            node.execution_id = worker.workflow.execution_id 
            for parent in parent_nodes:
                worker.accumulator[parent.id_] = parent

        elif isinstance(node, Trigger):
            raise NotImplementedError

        try:
            if isinstance(node, Action):
                assert node.id_ in worker.in_process
                await worker.schedule_node(node, parents, children)
                tasks.add(asyncio.create_task(worker.schedule_node(node, parents, children)))
            
        except:
            logger.exception(f"UH OH {node.app_name}")
            logger.info(node)

        #check if action node correct
        if isinstance(node, Action):
            assert node.id_ in worker.in_process
            assert (await redis.lpop(f"{node.app_name}-{node.priority}")).decode("utf-8") == workflow_dumps(node)

        for child in sorted(children.values(), reverse=True):
            if child not in visited:
                queue.appendleft(child)
                visited.add(child)

    # check every node visited
    assert worker.start_action in visited
    for subnode in worker.workflow.successors(worker.start_action):
        assert subnode in visited

#test schedule_node for transform node exclusively
@pytest.mark.asyncio
async def test_schedule_transform_node_get_value_at_index(redis, worker):
    visited = {worker.start_action}
    queue = deque([worker.start_action])
    tasks = set()

    while queue:
        node = queue.pop()
        parents = {n.id_: n for n in worker.workflow.predecessors(node)} if node is not worker.start_action else {}
        parent_nodes = {n: n for n in worker.workflow.predecessors(node)} if node is not worker.start_action else {}
        children = {n.id_: n for n in worker.workflow.successors(node)}
        worker.in_process[node.id_] = node
        

        for parent in parent_nodes:
            worker.accumulator[parent.id_] = [1,2,3,4,5]

        try:
            if isinstance(node, Transform) and node.id_ == "3e9e6d9f-736e-437a-a5b0-138783c67fbb":
                assert node.id_ in worker.in_process
                await worker.schedule_node(node, parents, children)
        
        except:
            logger.exception(f"UH OH {node.app_name}")
            logger.info(node)


        if isinstance(node, Transform) and node.id_ == "3e9e6d9f-736e-437a-a5b0-138783c67fbb":
            assert node.id_ not in worker.in_process
            assert worker.accumulator[node.id_] == 3

        for child in sorted(children.values(), reverse=True):
            if child not in visited:
                queue.appendleft(child)
                visited.add(child)


@pytest.mark.asyncio
async def test_schedule_transform_node_get_value_at_key(redis, worker):
    visited = {worker.start_action}
    queue = deque([worker.start_action])
    tasks = set()

    while queue:
        node = queue.pop()
        parents = {n.id_: n for n in worker.workflow.predecessors(node)} if node is not worker.start_action else {}
        parent_nodes = {n: n for n in worker.workflow.predecessors(node)} if node is not worker.start_action else {}
        children = {n.id_: n for n in worker.workflow.successors(node)}
        worker.in_process[node.id_] = node
        

        for parent in parent_nodes:
            #worker.accumulator[parent.id_] = {"hey":"hi", "hey2": "hi2"}
            worker.accumulator[parent.id_] = {"spam": "tester_data"}
        try:
            if isinstance(node, Transform) and node.id_ == "53a68b00-979f-46c3-ab9c-cc08108ce97c":
                assert node.id_ in worker.in_process
                await worker.schedule_node(node, parents, children)
        
        except:
            logger.exception(f"UH OH {node.app_name}")
            logger.info(node)


        if isinstance(node, Transform) and node.id_ == "53a68b00-979f-46c3-ab9c-cc08108ce97c":
            assert node.id_ not in worker.in_process
            assert worker.accumulator[node.id_] == "tester_data"

        for child in sorted(children.values(), reverse=True):
            if child not in visited:
                queue.appendleft(child)
                visited.add(child)


#test schedule_node for condition node
@pytest.mark.asyncio
async def test_schedule_condition_node(redis, worker):
    visited = {worker.start_action}
    queue = deque([worker.start_action])
    tasks = set()

    while queue:
        node = queue.pop()
        parents = {n.id_: n for n in worker.workflow.predecessors(node)} if node is not worker.start_action else {}
        children = {n.id_: n for n in worker.workflow.successors(node)}
        worker.in_process[node.id_] = node
        
        logger.info(f" ACCUMULATOR: {worker.accumulator}")

        for parent in parents.values():
            worker.accumulator[parent.id_] = "Temporary Data"

        try:
            if isinstance(node, Condition):
                assert node.id_ in worker.in_process
                await worker.schedule_node(node, parents, children)
                #tasks.add(asyncio.create_task(worker.schedule_node(node, parents, children)))
        except:
            logger.exception(f"UH OH {node.app_name}")
            logger.info(node)

        logger.info(f" IN PROCESS: {worker.in_process}")
        
        #check if in_process is correct
        if isinstance(node, Condition):
            assert node.id_ not in worker.in_process

        for child in sorted(children.values(), reverse=True):
            if child not in visited:
                queue.appendleft(child)
                visited.add(child)


@pytest.mark.asyncio
async def test_action_results(redis, worker):
    visited = {worker.start_action}
    queue = deque([worker.start_action])

    while queue:
        node = queue.pop()
        parents = {n.id_: n for n in worker.workflow.predecessors(node)} if node is not worker.start_action else {}
        children = {n.id_: n for n in worker.workflow.successors(node)}
        worker.in_process[node.id_] = node

        for parent in parents.values():
            worker.accumulator[parent.id_] = "Temporary Data"

        if isinstance(node, Action):
            if node.id_ == "55876340-50b1-d9a4-7f22-150a6f4be4c6":
                node.execution_id = worker.workflow.execution_id  # the app needs this as a key for the redis queue
                await worker.schedule_node(node, parents, children)
                redis.lpush(worker.workflow.execution_id, node)

        elif isinstance(node, Trigger):
            raise NotImplementedError

        for child in sorted(children.values(), reverse=True):
            if child not in visited:
                queue.appendleft(child)
                visited.add(child)

    await worker.get_action_results()


#shutdown test
@pytest.mark.asyncio
async def test_shutdown(redis, worker):
    # push some tasks
    visited = {worker.start_action}
    queue = deque([worker.start_action])
    while queue:
        node = queue.pop()
        parents = {n.id_: n for n in worker.workflow.predecessors(node)} if node is not worker.start_action else {}
        children = {n.id_: n for n in worker.workflow.successors(node)}
        worker.in_process[node.id_] = node
        

        for parent in parents.values():
            worker.accumulator[parent.id_] = "Temporary Data"


        if isinstance(node, Action):
            node.execution_id = worker.workflow.execution_id 
            asyncio.create_task(worker.schedule_node(node, parents, children))

        for child in sorted(children.values(), reverse=True):
            if child not in visited:
                queue.appendleft(child)
                visited.add(child)


    # ensure that they are there
    for t in asyncio.all_tasks():
        if t is not asyncio.current_task():
            assert (not t.cancelled())

    # shutdown and ensure they have been removed
    await worker.shutdown()
    for t in asyncio.all_tasks():
        if t is not asyncio.current_task():
            assert t.cancelled()

# test cancel_subgraph
# @pytest.mark.asyncio
# async def test_cancel_subgraph(redis, worker):
#     visited = {worker.start_action}
#     queue = deque([worker.start_action])

#     while queue:
#         node = queue.pop()
#         parents = {n.id_: n for n in worker.workflow.predecessors(node)} if node is not worker.start_action else {}
#         children = {n.id_: n for n in worker.workflow.successors(node)}
#         worker.in_process[node.id_] = node

#         if isinstance(node, Action):
#             node.execution_id = worker.workflow.execution_id  # the app needs this as a key for the redis queue

#         elif isinstance(node, Trigger):
#             raise NotImplementedError

#         asyncio.create_task(worker.schedule_node(node, parents, children))

#         for child in sorted(children.values(), reverse=True):
#             if child not in visited:
#                 queue.appendleft(child)
#                 visited.add(child)


#     await worker.cancel_subgraph(worker.start_action)
    
#     for t in asyncio.all_tasks():
#         if t is not asyncio.current_task():
#             assert t.cancelled() == "hi"