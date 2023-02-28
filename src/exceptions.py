class TimeLimitExceededException(Exception):
    def __init__(self, message="Time limit has exceeded"):
        super().__init__(message)


class MaxAttemptExceededException(Exception):
    def __init__(self, message="Reached max number of attempts."):
        super().__init__(message)
