class CatnipError(Exception):
    """Base error for all catnip-agent layers."""


class QueueError(CatnipError):
    """Error from the Queue layer."""


class WorkerError(CatnipError):
    """Error from the Worker layer."""


class GatewayError(CatnipError):
    """Error from the Gateway layer."""


class HarnessError(CatnipError):
    """Error from the Harness layer."""
