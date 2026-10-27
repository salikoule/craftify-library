from ._anvil_designer import FileDropTemplate
from anvil import BlobMedia


def _to_media(js_file):
    if js_file is None:
        return None
    try:
        from anvil.js import to_media
        media = to_media(js_file)
        if media is not None:
            return media
    except Exception:
        pass
    return BlobMedia(
        getattr(js_file, "type", None) or "application/octet-stream",
        js_file,
        name=getattr(js_file, "name", None) or "upload",
    )


class FileDrop(FileDropTemplate):
    """Full-width drop zone: drag a file in or click to browse."""

    def __init__(self, **properties):
        title = properties.pop("title", "Drop file here")
        hint = properties.pop("hint", "or click to browse")
        file_types = properties.pop("file_types", "")
        self._file = None
        self._bound = False
        self.init_components(**properties)
        self.title = title
        self.hint = hint
        self.file_types = file_types
        self._bind()
        self._render()

    def form_show(self, **event_args):
        self._bind()
        self._render()

    def _node(self, name):
        nodes = getattr(self, "dom_nodes", None)
        if not nodes:
            return None
        try:
            return nodes[name]
        except Exception:
            return None

    def _bind(self):
        if self._bound:
            return
        root = self._node("root")
        picker = self._node("input")
        clear = self._node("clear")
        if root is None or picker is None:
            return
        picker.addEventListener("change", self._on_pick)
        picker.addEventListener("dragenter", self._on_drag)
        picker.addEventListener("dragover", self._on_drag)
        picker.addEventListener("dragleave", self._on_leave)
        picker.addEventListener("drop", self._on_drop)
        if clear is not None:
            clear.addEventListener("click", self._on_clear)
        self._bound = True

    def _on_drag(self, event):
        event.preventDefault()
        root = self._node("root")
        if root is not None:
            root.classList.add("is-over")

    def _on_leave(self, event):
        event.preventDefault()
        root = self._node("root")
        if root is not None:
            root.classList.remove("is-over")

    def _on_drop(self, event):
        event.preventDefault()
        root = self._node("root")
        if root is not None:
            root.classList.remove("is-over")

    def _on_pick(self, *_args):
        picker = self._node("input")
        files = getattr(picker, "files", None) if picker is not None else None
        js_file = files[0] if files and len(files) else None
        self._file = _to_media(js_file)
        self._render()
        self.raise_event("change")

    def _on_clear(self, event):
        if event is not None:
            event.preventDefault()
            event.stopPropagation()
        picker = self._node("input")
        if picker is not None:
            picker.value = ""
        self._file = None
        self._render()
        self.raise_event("change")

    def _render(self):
        root = self._node("root")
        name = self._node("filename")
        ready = self._file is not None
        if root is not None:
            root.classList.toggle("is-ready", ready)
        if name is not None:
            label = ""
            if ready:
                label = getattr(self._file, "name", None) or "File ready"
            name.textContent = label

    @property
    def title(self):
        node = self._node("title")
        return (node.textContent or "") if node is not None else ""

    @title.setter
    def title(self, value):
        node = self._node("title")
        if node is not None:
            node.textContent = value or "Drop file here"

    @property
    def hint(self):
        node = self._node("hint")
        return (node.textContent or "") if node is not None else ""

    @hint.setter
    def hint(self, value):
        node = self._node("hint")
        if node is not None:
            node.textContent = value or "or click to browse"

    @property
    def file_types(self):
        picker = self._node("input")
        return (picker.getAttribute("accept") or "") if picker is not None else ""

    @file_types.setter
    def file_types(self, value):
        picker = self._node("input")
        if picker is not None:
            picker.setAttribute("accept", value or "")

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, value):
        self._file = value
        self._render()
