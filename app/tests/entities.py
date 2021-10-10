from typing import Optional, List


class FakeResponse:
    def __init__(
        self, response: Optional[dict] = None, status_code: Optional[int] = None
    ) -> None:
        self._response = response
        self.status_code = status_code
        self.text = "Internal Server Error"

    def json(self):
        return self._response


class FakeRequestClient:
    def __init__(self, responses: List[FakeResponse] = None) -> None:
        self._responses = responses
        self.url = None
        self.data = None
        self.called = 0

    def get(self, url: str, data: Optional[dict] = None) -> FakeResponse:
        self.url = url
        self.data = data
        self.called += 1

        response = (
            self._responses.pop(0) if len(self._responses) > 1 else self._responses[0]
        )

        return response
