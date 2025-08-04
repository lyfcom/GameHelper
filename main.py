from control_panel import ControlPanel

def main():
    """
    应用程序的主入口点。
    """
    try:
        app = ControlPanel()
        app.mainloop()
    except Exception as e:
        # 在这里可以添加一个更友好的错误弹窗
        print(f"应用程序遇到严重错误: {e}")

if __name__ == "__main__":
    main()
