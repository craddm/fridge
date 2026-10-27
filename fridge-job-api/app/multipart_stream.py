from collections.abc import AsyncIterator
from fastapi import HTTPException, Request
from python_multipart.exceptions import FormParserError
from python_multipart.multipart import MultipartParser, parse_options_header


class MultipartFileStream:
    """
    Reads one file field from a multipart/form-data request body as it arrives, rather than
    spooling the whole body to disk first as FastAPI's UploadFile does. This lets the file be
    sent on to S3 while the client is still uploading it.
    """

    def __init__(self, request: Request, field_name: str = "file"):
        content_type = request.headers.get("content-type", "")
        mime_type, params = parse_options_header(content_type)
        if mime_type != b"multipart/form-data" or b"boundary" not in params:
            raise HTTPException(
                status_code=422, detail="Request body must be multipart/form-data."
            )

        self.field_name = field_name
        self.filename: str | None = None
        self.content_type: str | None = None

        self._stream = request.stream()
        self._parser = MultipartParser(
            params[b"boundary"],
            callbacks={
                "on_part_begin": self._on_part_begin,
                "on_header_field": self._on_header_field,
                "on_header_value": self._on_header_value,
                "on_header_end": self._on_header_end,
                "on_headers_finished": self._on_headers_finished,
                "on_part_data": self._on_part_data,
                "on_part_end": self._on_part_end,
            },
        )
        self._headers: dict[bytes, bytes] = {}
        self._header_field = b""
        self._header_value = b""
        self._in_file = False
        self._file_done = False
        self._pending: list[bytes] = []

    async def open(self) -> None:
        """Read the body up to the start of the file field, so its name and type are known."""
        while self.filename is None:
            if not await self._feed():
                raise HTTPException(
                    status_code=422,
                    detail=f"Missing file field '{self.field_name}'.",
                )

    async def chunks(self) -> AsyncIterator[bytes]:
        """Yield the file's contents as they arrive, then read the rest of the body."""
        while True:
            if self._pending:
                data = b"".join(self._pending)
                self._pending.clear()
                yield data
            if self._file_done:
                break
            if not await self._feed():
                raise HTTPException(
                    status_code=400, detail="Request body ended mid-file."
                )
        # Any fields after the file are ignored, but the body is still read and checked
        while await self._feed():
            pass

    async def _feed(self) -> bool:
        """Pass the next piece of the body to the parser. Returns False at the end of the body."""
        try:
            chunk = await anext(self._stream)
        except StopAsyncIteration:
            chunk = None
        try:
            if chunk is None:
                self._parser.finalize()
                return False
            self._parser.write(chunk)
            return True
        except FormParserError:
            raise HTTPException(status_code=400, detail="Invalid multipart data.")

    def _on_part_begin(self) -> None:
        self._headers = {}

    def _on_header_field(self, data: bytes, start: int, end: int) -> None:
        self._header_field += data[start:end]

    def _on_header_value(self, data: bytes, start: int, end: int) -> None:
        self._header_value += data[start:end]

    def _on_header_end(self) -> None:
        self._headers[self._header_field.lower()] = self._header_value
        self._header_field = b""
        self._header_value = b""

    def _on_headers_finished(self) -> None:
        _, disposition = parse_options_header(self._headers.get(b"content-disposition"))
        # Only the first file in the named field is read
        if (
            self.filename is None
            and disposition.get(b"name") == self.field_name.encode()
            and b"filename" in disposition
        ):
            self.filename = disposition[b"filename"].decode()
            content_type = self._headers.get(b"content-type")
            self.content_type = content_type.decode() if content_type else None
            self._in_file = True

    def _on_part_data(self, data: bytes, start: int, end: int) -> None:
        if self._in_file:
            self._pending.append(data[start:end])

    def _on_part_end(self) -> None:
        if self._in_file:
            self._in_file = False
            self._file_done = True
