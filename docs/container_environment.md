## 容器環境開發注意事項

### UI 元件可見性

在設計 UI 元件時，如果功能在容器環境中無法正常工作，應該使用 `util.should_show_open_folder_buttons()` 來控制可見性：

```python
button = gr.Button(
    value="Open Folder",
    visible=util.should_show_open_folder_buttons()
)
```

### 容器檢測

使用 `util.is_linux_container()` 來檢測當前是否運行在容器環境中。
