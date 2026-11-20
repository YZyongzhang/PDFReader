import json
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

from PySide6.QtCore import QByteArray, QObject, QUrl
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest


DEFAULT_BASE = "https://api.openai.com/v1"
API_PATHS = {"chat": "/chat/completions", "text": "/completions"}


def resolve_endpoint(base, api_mode="auto"):
    url = urlsplit(base.strip())
    if (url.scheme not in ("http", "https") or not url.hostname
            or url.username or url.password or url.query or url.fragment):
        raise ValueError("请输入有效的 HTTP 或 HTTPS API 地址。")
    # Accessing port validates the format and range.
    _ = url.port
    path = url.path.rstrip("/")
    # Check the longer suffix first because both endpoints end in /completions.
    explicit = next((mode for mode, suffix in API_PATHS.items() if path.endswith(suffix)), None)
    if explicit and api_mode not in ("auto", explicit):
        raise ValueError("API 地址与接口类型不一致。请选「自动识别」或填写 Base URL。")
    mode = explicit or ("chat" if api_mode == "auto" else api_mode)
    if not explicit:
        path += API_PATHS[mode]
    return urlunsplit((url.scheme, url.netloc, path, "", "")), mode


@dataclass(frozen=True)
class AIConfig:
    base: str
    model: str
    key: str
    language: str
    api_mode: str = "auto"


class AIClient(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.network = QNetworkAccessManager(self)

    def complete(self, config, messages, callback):
        endpoint, mode = resolve_endpoint(config.base, config.api_mode)
        request = QNetworkRequest(QUrl(endpoint))
        request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
        request.setAttribute(
            QNetworkRequest.Attribute.RedirectPolicyAttribute,
            QNetworkRequest.RedirectPolicy.ManualRedirectPolicy,
        )
        request.setTransferTimeout(90_000)
        if config.key:
            request.setRawHeader(b"Authorization", ("Bearer " + config.key).encode())
        body = {"model": config.model, "stream": False}
        if mode == "chat":
            body["messages"] = messages
        else:
            turns = [f"{message['role'].capitalize()}:\n{message['content']}" for message in messages]
            body["prompt"] = "\n\n".join([*turns, "Assistant:\n"])
            body["max_tokens"] = 1024
        data = json.dumps(body)
        reply = self.network.post(request, QByteArray(data.encode()))

        def finished():
            raw = bytes(reply.readAll())
            status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
            network_error = reply.error()
            error_text = reply.errorString()
            reply.deleteLater()
            try:
                payload = json.loads(raw)
            except (ValueError, UnicodeError):
                payload = None
            if status and not 200 <= status < 300:
                error = payload.get("error", "") if isinstance(payload, dict) else ""
                detail = error.get("message", "") if isinstance(error, dict) else str(error)
                if config.key:
                    detail = detail.replace(config.key, "••••")
                callback(None, f"HTTP {status}" + (f" · {detail[:500]}" if detail else ""))
                return
            if network_error != QNetworkReply.NetworkError.NoError:
                callback(None, error_text)
                return
            try:
                choice = payload["choices"][0]
                answer = (choice["message"]["content"] if mode == "chat" else choice["text"]).strip()
                if not answer:
                    raise ValueError()
            except (AttributeError, IndexError, KeyError, TypeError, ValueError):
                callback(None, "API 未返回可显示的文本，请检查接口与模型。")
                return
            callback(answer, None)

        reply.finished.connect(finished)
        return reply
