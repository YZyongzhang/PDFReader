from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLabel,
    QLineEdit, QVBoxLayout,
)

from .ai import AIConfig, resolve_endpoint


class SettingsDialog(QDialog):
    def __init__(self, config, remember, client, parent):
        super().__init__(parent)
        self.setWindowTitle("AI 设置")
        self.setMinimumWidth(550)
        self.client = client
        self.reply = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        title = QLabel("连接你的 AI 模型")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)
        intro = QLabel("支持 OpenAI 兼容接口。提问时可发送当前页文字，翻译时发送选中的文字。")
        intro.setWordWrap(True)
        intro.setObjectName("muted")
        layout.addWidget(intro)

        form = QFormLayout()
        self.base = QLineEdit(config.base)
        self.base.setPlaceholderText("https://api.openai.com/v1")
        self.api_mode = QComboBox()
        for title, mode in [
            ("自动识别（Base URL 默认 Chat Completions）", "auto"),
            ("Chat Completions", "chat"),
            ("Completions", "text"),
        ]:
            self.api_mode.addItem(title, mode)
        self.api_mode.setCurrentIndex(max(0, self.api_mode.findData(config.api_mode)))
        self.model = QLineEdit(config.model)
        self.model.setPlaceholderText("输入服务商提供的模型 ID")
        self.key = QLineEdit(config.key)
        self.key.setEchoMode(QLineEdit.EchoMode.Password)
        self.key.setPlaceholderText("没有鉴权要求时可留空")
        self.remember = QCheckBox("将 API Key 保存在本地数据库（明文）")
        self.remember.setChecked(remember)
        self.language = QComboBox()
        self.language.setEditable(True)
        self.language.addItems(["简体中文", "繁體中文", "English", "日本語", "한국어", "Français", "Deutsch", "Español"])
        self.language.setCurrentText(config.language)
        form.addRow("API 地址", self.base)
        form.addRow("接口类型", self.api_mode)
        form.addRow("模型", self.model)
        form.addRow("API Key", self.key)
        form.addRow("", self.remember)
        form.addRow("翻译目标语言", self.language)
        layout.addLayout(form)

        self.status = QLabel()
        self.status.setObjectName("muted")
        self.status.setTextFormat(Qt.TextFormat.PlainText)
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        buttons = QDialogButtonBox()
        self.test = buttons.addButton("测试连接", QDialogButtonBox.ButtonRole.ActionRole)
        self.test.clicked.connect(self.test_connection)
        save = buttons.addButton("保存", QDialogButtonBox.ButtonRole.AcceptRole)
        save.setObjectName("primary")
        buttons.addButton("取消", QDialogButtonBox.ButtonRole.RejectRole)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def config(self):
        return AIConfig(
            self.base.text().strip(), self.model.text().strip(), self.key.text().strip(),
            self.language.currentText().strip() or "简体中文",
            self.api_mode.currentData(),
        )

    def validate(self, require_model):
        config = self.config()
        try:
            resolve_endpoint(config.base, config.api_mode)
        except ValueError as error:
            self.status.setText(str(error))
            return False
        if require_model and not config.model:
            self.status.setText("请输入模型 ID。")
            return False
        return True

    def save(self):
        if self.validate(False):
            self.accept()

    def test_connection(self):
        if not self.validate(True):
            return
        self.test.setEnabled(False)
        self.status.setText("正在测试连接…")

        def done(answer, error):
            self.reply = None
            self.status.setText(error or "连接成功，模型已返回文本。")
            self.test.setEnabled(True)

        self.reply = self.client.complete(
            self.config(), [{"role": "user", "content": "Reply with OK."}], done,
        )

    def done(self, result):
        if self.reply is not None:
            self.reply.abort()
        super().done(result)
