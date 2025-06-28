import grpc
import warnings
from ai_project_helper.proto import helper_pb2 as helper__pb2

GRPC_GENERATED_VERSION = '1.73.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in helper_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class AIProjectHelperStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.RunPlan = channel.unary_stream(
                '/ai_project_helper.AIProjectHelper/RunPlan',
                request_serializer=helper__pb2.PlanExecuteRequest.SerializeToString,
                response_deserializer=helper__pb2.ActionFeedback.FromString,
                _registered_method=True)
        self.GetPlan = channel.unary_stream(
                '/ai_project_helper.AIProjectHelper/GetPlan',
                request_serializer=helper__pb2.PlanGetRequest.SerializeToString,
                response_deserializer=helper__pb2.ActionFeedback.FromString,
                _registered_method=True)
        self.GetPlanThenRun = channel.unary_stream(
                '/ai_project_helper.AIProjectHelper/GetPlanThenRun',
                request_serializer=helper__pb2.PlanThenExecuteRequest.SerializeToString,
                response_deserializer=helper__pb2.ActionFeedback.FromString,
                _registered_method=True)


class AIProjectHelperServicer(object):
    """Missing associated documentation comment in .proto file."""

    def RunPlan(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetPlan(self, request, context):
        """新增方法
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetPlanThenRun(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_AIProjectHelperServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'RunPlan': grpc.unary_stream_rpc_method_handler(
                    servicer.RunPlan,
                    request_deserializer=helper__pb2.PlanExecuteRequest.FromString,
                    response_serializer=helper__pb2.ActionFeedback.SerializeToString,
            ),
            'GetPlan': grpc.unary_stream_rpc_method_handler(
                    servicer.GetPlan,
                    request_deserializer=helper__pb2.PlanGetRequest.FromString,
                    response_serializer=helper__pb2.ActionFeedback.SerializeToString,
            ),
            'GetPlanThenRun': grpc.unary_stream_rpc_method_handler(
                    servicer.GetPlanThenRun,
                    request_deserializer=helper__pb2.PlanThenExecuteRequest.FromString,
                    response_serializer=helper__pb2.ActionFeedback.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'ai_project_helper.AIProjectHelper', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('ai_project_helper.AIProjectHelper', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class AIProjectHelper(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def RunPlan(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/ai_project_helper.AIProjectHelper/RunPlan',
            helper__pb2.PlanExecuteRequest.SerializeToString,
            helper__pb2.ActionFeedback.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetPlan(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/ai_project_helper.AIProjectHelper/GetPlan',
            helper__pb2.PlanGetRequest.SerializeToString,
            helper__pb2.ActionFeedback.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetPlanThenRun(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/ai_project_helper.AIProjectHelper/GetPlanThenRun',
            helper__pb2.PlanThenExecuteRequest.SerializeToString,
            helper__pb2.ActionFeedback.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
