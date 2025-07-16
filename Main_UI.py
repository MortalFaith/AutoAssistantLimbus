import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.properties import NumericProperty, StringProperty

# 导入 Kivy 的核心 Builder 和 Factory
from kivy.lang import Builder
from kivy.core.text import LabelBase # 用于注册字体

import time

import os
from paddleocr import PaddleOCR
from OCR_main import rec_enkephalin, extract_from_json

# from utils import ex

# 设置 Kivy 最小版本
kivy.require('2.0.0')

# --- 字体注册部分 ---
# 替换为你的字体文件路径
# 如果字体文件在你的脚本同目录下，直接写文件名即可
FONT_PATH = 'ChineseFont.ttf' # <--- 请将此替换为你实际的字体文件路径

# 注册一个自定义字体
# 'my_font' 是你将会在 Label 或其他 Text 控件中使用的字体名称
LabelBase.register(name='my_font', fn_regular=FONT_PATH)

# 全局设置 Kivy 的默认字体为你的自定义字体
# 这会影响所有没有明确指定字体的 Label、Button 等文本控件
# 也可以只对特定控件设置字体
Builder.load_string("""
<Label>:
    font_name: 'my_font'
<Button>:
    font_name: 'my_font'
<TextInput>:
    font_name: 'my_font'
# 如果有其他显示文本的控件，也在这里设置
""")

# --- Kivy 界面模板代码 ---

# --- 右侧功能界面的定义 ---
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = 'home'
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text="欢迎来到AAL！", font_size='24sp', size_hint_y=0.2))
        layout.add_widget(Label(text="请在左侧选择一个功能。", font_size='18sp'))
        self.add_widget(layout)


class Function1Screen(Screen):
    current_enkephalin = NumericProperty(0)
    time_to_full = StringProperty("请点击下方按钮更新体力信息")

    # __init__ 方法中不再需要任何创建控件的代码，所以可以完全省略它！
    # Kivy 会自动调用父类的 __init__。

    def update_status(self):
        """
        通过 App 对象获取共享的 OCR 引擎实例。
        """
        try:
            # 获取当前正在运行的 App 实例
            app = App.get_running_app()

            # 检查引擎是否已初始化
            if app.ocr_engine is None:
                print("错误：OCR引擎尚未初始化！")
                self.time_to_full = "引擎错误"
                return

            # 使用 App 实例的 ocr_engine 属性
            enkephalin_data = rec_enkephalin(app.ocr_engine)

            json_file_path = os.path.join(enkephalin_data, "screenshot_cropped_res.json")
            recognized_texts = extract_from_json(json_file_path, "rec_texts")

            # 从返回结果中获取 "16/123" 这样的字符串
            # 这里假设它在返回数据的第3个位置 (索引为2)
            status_string = recognized_texts[2]

            parts = status_string.split('/')

            print(parts)

            # 更新 Kivy 属性，界面会自动响应
            cur_enkephalin_num = int(parts[0])
            full_enkephalin_num = int(parts[1])

            self.current_enkephalin = cur_enkephalin_num

            if cur_enkephalin_num >= full_enkephalin_num:
                self.time_to_full = "已回满"
            else:
                remaining_minutes = (full_enkephalin_num - cur_enkephalin_num) * 6
                hours = remaining_minutes // 60
                minutes = remaining_minutes % 60
                self.time_to_full = f"{hours}小时 {minutes}分钟"

            print(f"属性已更新: 体力={self.current_enkephalin}, 时间={self.time_to_full}")

        except Exception as e:
            print(f"执行OCR或处理数据时出错: {e}")
            self.time_to_full = "识别失败，请重试"

class Function2Screen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'function2'
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text="这是功能二的详细界面", font_size='24sp', size_hint_y=0.2))
        layout.add_widget(Label(text="这里将展示功能二的内容。", font_size='18sp'))
        scroll_content = Label(text="""
        这是很长一段文本，用于演示在 ScrollView 中的内容。
        你可以在这里放置任何你想要的功能，例如：
        - 输入框 (TextInput)
        - 下拉列表 (Spinner)
        - 图片 (Image)
        - 进度条 (ProgressBar)
        等等...

        Kivy 的布局系统非常灵活，允许你构建复杂的界面。
        Function2 的内容比 Function1 多一点，以便更好地展示滚动功能。
        """, font_size='16sp', size_hint_y=None, halign='left', valign='top',
           text_size=(self.width - 40, None)) # 注意：text_size 的宽度应为 ScrollView 的宽度减去 padding

        scroll_content.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))

        scroll_view = ScrollView(size_hint=(1, 0.7), do_scroll_x=False)
        scroll_view.add_widget(scroll_content)
        layout.add_widget(scroll_view)

        self.add_widget(layout)

class Function3Screen(Screen):
    display_text = StringProperty("默认显示文本")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'function3'
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text="这是功能三的界面", font_size='24sp', size_hint_y=0.2))
        layout.add_widget(Label(text="这是一个可以更新内容的示例：", font_size='18sp'))

        self.display_label = Label(text=self.display_text, font_size='20sp', color=(0.2, 0.6, 0.8, 1))
        layout.add_widget(self.display_label)

        update_button = Button(text="点击更新文本", size_hint_y=0.1)
        update_button.bind(on_release=self.update_display_text)
        layout.add_widget(update_button)

        self.add_widget(layout)

    def update_display_text(self, instance):
        import datetime
        self.display_text = f"文本已更新于：{datetime.datetime.now().strftime('%H:%M:%S')}"
        self.display_label.text = self.display_text

# --- 主应用布局 ---
class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = 10
        self.padding = 10

        self.left_panel = BoxLayout(orientation='vertical', size_hint_x=0.25, spacing=5)

        scroll_view = ScrollView(do_scroll_x=False)
        buttons_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        buttons_layout.bind(minimum_height=buttons_layout.setter('height'))

        functions = {
            "主页": "home",
            "体力提醒/计算": "function1",
            "功能二": "function2",
            "功能三": "function3",
            "更多功能": "more_features"
        }

        for func_name, screen_name in functions.items():
            btn = Button(text=func_name, size_hint_y=None, height=40)
            btn.bind(on_release=lambda instance, name=screen_name: self.switch_screen(name))
            buttons_layout.add_widget(btn)

        scroll_view.add_widget(buttons_layout)
        self.left_panel.add_widget(scroll_view)
        self.add_widget(self.left_panel)

        self.screen_manager = ScreenManager(size_hint_x=0.75)
        self.add_widget(self.screen_manager)

        self.screen_manager.add_widget(HomeScreen(name='home'))
        self.screen_manager.add_widget(Function1Screen(name='function1'))
        self.screen_manager.add_widget(Function2Screen(name='function2'))
        self.screen_manager.add_widget(Function3Screen(name='function3'))

        class NotImplementedScreen(Screen):
            def __init__(self, feature_name, **kwargs):
                super().__init__(**kwargs)
                self.name = feature_name
                layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
                layout.add_widget(Label(text=f"功能 '{feature_name}' 尚未实现。", font_size='24sp', color=(1, 0, 0, 1)))
                layout.add_widget(Label(text="请选择其他功能或等待更新。", font_size='18sp'))
                self.add_widget(layout)

        self.screen_manager.add_widget(NotImplementedScreen(name='more_features', feature_name='更多功能'))

        self.screen_manager.current = 'home'

    def switch_screen(self, screen_name):
        print(f"切换到屏幕: {screen_name}")
        self.screen_manager.current = screen_name

# --- Kivy 应用类 ---
class MyApp(App):
    # 在这里添加 ocr_engine 属性
    ocr_engine = None

    def build(self):
        self.title = "Auto Assistant of Limbus"
        self.icon = 'icon/main_icon.webp'
        return MainLayout()

    def on_start(self):
        """
        这个方法在 build() 完成后，应用启动时被调用。
        是进行重量级初始化操作的理想位置。
        """
        print("应用启动，开始初始化OCR引擎...")

        user_home = os.path.expanduser('~')
        model_path = os.path.join(user_home, '.paddleocr_models')
        if not os.path.exists(model_path):
            os.makedirs(model_path)
        os.environ['PADDLE_HOME'] = model_path

        # 将引擎实例保存到 App 的属性中
        self.ocr_engine = PaddleOCR(
            text_detection_model_name="PP-OCRv5_mobile_det",
            text_recognition_model_name="PP-OCRv5_mobile_rec",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False
        )
        print("OCR引擎初始化完成。")

if __name__ == '__main__':
    MyApp().run()