# 页间 · PDF 阅读器

一个使用 PySide6（Qt Widgets 和 Qt PDF）的 Linux 桌面应用。

## 启动

需要 Python 3.10 或以上。PySide6 包含运行所需的 Qt 库与 Qt PDF 模块。

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./launch.sh
```

也可在启动时传入一个或多个 PDF 路径，例如 `./launch.sh a.pdf b.pdf`。Ubuntu 的 X11 会话如果提示缺少 `libxcb-cursor.so.0`，可以安装系统软件包 `libxcb-cursor0`。

## 阅读与标注

- 点击「导入 PDF」批量选择文件，也可以把文件拖入窗口。左栏从文档库切换文件，通过页面缩略图跳页。
- 在「选文」模式下拖选文字，高亮、翻译或右键复制。按 Ctrl+H 高亮，按 Ctrl+T 翻译。
- 「画笔」可在页面上手绘。「橡皮擦」可点击或拖过笔迹，一次擦除接触到的整笔。「批注」可在任意位置插入文字，也可以右键批注圆点删除。
- 左栏「标注」汇总当前文档的高亮、画笔和批注。单击跳页，双击编辑。按 Ctrl 或 Shift 多选，或点「全选」，再点击「删除」或按 Delete 批量删除。
- PDF 保留在导入前的位置。文档库、阅读页码、标注及对话保存在本地数据库，标注显示在阅读器中。默认数据库路径为 `~/.local/share/PDFReader/library.sqlite3`。
- 选文功能依赖 PDF 的文字层。纯扫描件可阅读、画笔标记和添加批注，文字选取需要先对原件做 OCR。

## AI 配置

在「AI 设置」中填写 OpenAI 兼容的 API 地址、模型 ID 和 API Key，可测试连接并选择翻译目标语言。本机和远程地址均支持 HTTP 和 HTTPS。无需鉴权的接口可留空 API Key。

- 填写 Base URL，例如 `http://my-server:8000/v1`，并选择「Chat Completions」或「Completions」。
- 填写以 `/chat/completions` 或 `/completions` 结尾的完整地址时，可选择「自动识别」。使用 Base URL 时，「自动识别」默认选择 Chat Completions。

API Key 默认仅保存在进程内，也可通过 `PDFREADER_API_KEY` 环境变量提供。勾选保存时，密钥以明文写入当前用户的本地数据库。

发送问题时，勾选「附上当前页」会把当前页可提取的文字随问题发送。翻译只发送选中的原文及目标语言，接口由你的配置决定。

阅读助手的回复以 Markdown 渲染，支持标题、粗体、列表、表格和代码块，可点击「复制」复制回复文本。
