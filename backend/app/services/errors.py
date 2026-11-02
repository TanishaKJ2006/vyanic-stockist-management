"""Domain errors shared by the API services."""


class ServiceError(Exception):
    """Base class for expected service-layer failures."""


class DuplicateSkuError(ServiceError):
    pass


class DuplicatePincodeError(ServiceError):
    pass


class ResourceNotFoundError(ServiceError):
    pass


class AuditWriteError(ServiceError):
    pass


class AuditReadError(ServiceError):
    pass


class DatabaseReadError(ServiceError):
    pass


class DatabaseWriteError(ServiceError):
    pass
