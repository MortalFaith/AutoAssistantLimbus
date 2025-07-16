import os
import cv2
import json
import pygetwindow as gw
import win32api, win32con, win32gui
import pyautogui
from paddleocr import PaddleOCR

# --- 全局设置 ---
# 将模型路径设置在用户目录下，这样通常不需要管理员权限
# os.path.expanduser('~') 会获取用户主目录 (如 C:\Users\YourUser)
# 默认的PP-OCRv5_mobile_det与PP-OCRv5_mobile_rec模型大小总和约为20 MB
# 可前往https://paddlepaddle.github.io/PaddleOCR/latest/version3.x/pipeline_usage/OCR.html#1-ocr选用您喜欢的模型
user_home = os.path.expanduser('~')
model_path = os.path.join(user_home, '.paddleocr_models')  # 模型将下载到这里

# 检查并创建模型目录
if not os.path.exists(model_path):
	os.makedirs(model_path)

# 在导入 paddleocr 之前设置 PADDLE_HOME 环境变量
# 注意：此行代码必须在 `from paddleocr import PaddleOCR` 之前
os.environ['PADDLE_HOME'] = model_path


def run_ocr_on_cropped_image(source_image_path: str, crop_coords: dict, ocr_engine: PaddleOCR,
                             output_dir: str = "output") -> str:
	"""
    对指定图片进行裁剪、执行OCR识别，并将结果保存为JSON。

    Args:
        source_image_path (str): 原始图片文件的路径。
        crop_coords (dict): 包含裁剪区域相对坐标的字典。
                            键应为 'x_start', 'y_start', 'x_end', 'y_end'，
                            值为0到1之间的浮点数（百分比）。
        ocr_engine (PaddleOCR): 已经初始化好的 PaddleOCR 引擎实例。
        output_dir (str, optional): 存放裁剪后图片和JSON结果的目录。默认为 "output"。

    Returns:
        str: 成功保存JSON文件的目录路径。如果失败则返回 None。
    """
	# 1. --- 参数校验和准备 ---
	if not os.path.exists(source_image_path):
		print(f"错误：源文件 '{source_image_path}' 不存在。")
		return None

	# 确保输出目录存在
	os.makedirs(output_dir, exist_ok=True)

	try:
		# 2. --- 图像加载和裁剪 ---
		img = cv2.imread(source_image_path)
		if img is None:
			print(f"错误：无法使用OpenCV读取图片 '{source_image_path}'。")
			return None

		height, width, _ = img.shape

		# 根据相对坐标计算绝对像素位置
		x_start = int(width * crop_coords['x_start'])
		x_end = int(width * crop_coords['x_end'])
		y_start = int(height * crop_coords['y_start'])
		y_end = int(height * crop_coords['y_end'])

		cropped_image = img[y_start:y_end, x_start:x_end]

		# 为裁剪后的图片生成一个唯一的文件名
		base_name = os.path.basename(source_image_path)
		file_name, file_ext = os.path.splitext(base_name)
		cropped_image_name = f"{file_name}_cropped.jpg"
		cropped_image_path = os.path.join(output_dir, cropped_image_name)

		cv2.imwrite(cropped_image_path, cropped_image)
		print(f"图片已裁剪并保存到: {cropped_image_path}")

		# 3. --- 执行OCR识别 ---
		print("正在执行OCR识别...")
		# 使用 ocr.predict 更底层，与您原始代码保持一致
		result = ocr_engine.predict(input=cropped_image_path)
		print("识别完成。")

		# 4. --- 保存结果到JSON ---
		# result 是一个列表，对应处理的每张图片。我们只处理了一张。
		if result and result[0]:
			# save_to_json 的参数是目录，它会自动生成文件名
			result[0].save_to_json(output_dir)
			print(f"识别结果已保存到目录: {output_dir}")
			return output_dir
		else:
			print("警告：OCR未能识别出任何内容。")
			return None

	except KeyError as e:
		print(f"错误: `crop_coords` 字典中缺少键: {e}。请确保包含 'x_start', 'y_start', 'x_end', 'y_end'。")
		return None
	except Exception as e:
		print(f"在处理图片或执行OCR时发生未知错误: {e}")
		return None


# --- 您原始代码中的辅助函数，保持不变 ---
def get_window_pos(name):
	handle = win32gui.FindWindow(0, name)
	if handle == 0:
		return None
	else:
		return win32gui.GetWindowRect(handle), handle


def get_Image(image_path, window_name='LimbusCompany'):
	window_info = get_window_pos(window_name)
	if window_info is None:
		print(f"错误：未找到标题为 '{window_name}' 的窗口。")
		return False
	try:
		(left, top, right, bottom), handle = window_info
		win32gui.SendMessage(handle, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
		win32gui.SetForegroundWindow(handle)
		window_width = right - left
		window_height = bottom - top
		screenshot = pyautogui.screenshot(region=(left, top, window_width, window_height))

		# 确保截图目录存在
		os.makedirs(os.path.dirname(image_path), exist_ok=True)
		screenshot.save(image_path)
		print(f"截图已保存到 {image_path}")
		return True
	except Exception as e:
		print(f"处理窗口或截图时发生错误： {e}")
		return False


def extract_from_json(file_path, index):
	if not os.path.exists(file_path):
		print(f"错误：文件 '{file_path}' 不存在。")
		return None
	try:
		with open(file_path, 'r', encoding='utf-8') as f:
			data = json.load(f)
		return data.get(index, None)
	except Exception as e:
		print(f"读取或处理JSON文件时发生错误: {e}")
		return None


def rec_enkephalin(ocr_engine: PaddleOCR):
	screenshot_save_path = "current/screenshot.png"
	results_directory = "ocr_results/enkephalin"
	enkephalin_coords = {
		'x_start': 0.2857,
		'y_start': 0.8571,
		'x_end': 0.375,
		'y_end': 0.9524
	}

	try:
		get_Image(screenshot_save_path)
	except Exception as e:
		print(f"Screenshot no update: {e}")

	json_dir = run_ocr_on_cropped_image(
		source_image_path=screenshot_save_path,
		crop_coords=enkephalin_coords,
		ocr_engine=ocr_engine,
		output_dir=results_directory
	)

	return json_dir


# ==============================================================================
# --- 主程序入口和调用示例 ---
# ==============================================================================
if __name__ == '__main__':

	# --- 步骤 1: 初始化OCR引擎 ---
	# 这是重量级操作（？），只需执行一次。
	print(f"正在从 '{model_path}' 加载或下载PaddleOCR模型...")
	# 您可以根据需要调整这里的参数
	ocr_engine_instance = PaddleOCR(
		    text_detection_model_name="PP-OCRv5_mobile_det",
		    text_recognition_model_name="PP-OCRv5_mobile_rec",
		    use_doc_orientation_classify=False,
		    use_doc_unwarping=False,
		    use_textline_orientation=False
	)
	print("OCR引擎初始化完成。")

	# --- 步骤 2: 准备函数参数 ---

	# 定义截图保存位置
	screenshot_save_path = "current/screenshot.png"

	# (可选) 调用 get_Image 获取最新截图
	# print("\n正在获取窗口截图...")
	# if not get_Image(screenshot_save_path):
	#    # 如果截图失败，则退出程序
	#    exit()

	# 定义要裁剪的区域 (使用百分比 * 长/宽)
	# 这对应您原始代码中的硬编码值
	test_coords = {
		'x_start': 0.2857,
		'y_start': 0.8571,
		'x_end': 0.375,
		'y_end': 0.9524
	}

	# 定义输出目录
	results_directory = "ocr_results/test"

	# --- 步骤 3: 调用封装好的函数 ---
	print("\n--- 开始执行OCR任务 ---")
	json_dir = run_ocr_on_cropped_image(
		source_image_path=screenshot_save_path,
		crop_coords=test_coords,
		ocr_engine=ocr_engine_instance,
		output_dir=results_directory
	)

	# --- 步骤 4: 处理返回结果 ---
	if json_dir:
		print(f"\n任务成功！结果已存放在: {json_dir}")
		# 我们可以尝试读取刚刚生成的json文件来验证
		# 文件名是根据裁剪后的图片名自动生成的
		json_file_path = os.path.join(json_dir, "screenshot_cropped_res.json")

		print(f"尝试从 {json_file_path} 中提取文本...")
		recognized_texts = extract_from_json(json_file_path, "rec_texts")

		if recognized_texts:
			print("成功提取到文本内容:", recognized_texts)
		else:
			print("未在JSON文件中找到'rec_texts'字段或文件无法读取。")
	else:
		print("\nOCR任务失败。")
