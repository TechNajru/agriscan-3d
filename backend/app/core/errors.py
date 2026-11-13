"""One error type for the whole pipeline. `code` is an i18n key under errors.*"""


class PipelineError(Exception):
    def __init__(self, code: str, status: int = 422, params: dict | None = None, metrics: dict | None = None):
        super().__init__(code)
        self.code, self.status, self.params, self.metrics = code, status, params or {}, metrics or {}

    def detail(self) -> dict:
        return {"code": self.code, "params": self.params, "metrics": self.metrics}
