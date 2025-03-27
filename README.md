# 1. Project Overview 项目概述
SystemSafetyTools is a toolkit for system security checking and optimization. It provides multiple functions including system security check and repair, useless file deletion, GPU basic information query, system security check and repair with file deletion, Windows DISM tools, network reset, hard drive integrity check, and boot repair (if Windows fails to boot) ...

SystemSafetyTools 是一个用于系统安全检查和优化的工具集。它提供了多种功能，包括系统安全检查与修复、无用文件删除、GPU基本信息查询、系统安全检查和修复及文件删除、Windows DISM工具、网络重置、硬盘完整性检查以及启动修复（如果Windows无法启动）......。

# 2. Project Structure 项目结构

## 2.1 System Requirements 系统要求
-  **windows 10 64bit** 
-  **windows 11 64bit**
-  **Windows language preferably in Chinese or English** | **windows 的语言最好为中文或英文**

## 2.2 Running 运行
Run SystemSafetyTools-amd64.exe in the project's dist folder | SystemSafetyTools-amd64.exe

# 3. Compilation and Running 编译与运行
If you only want to use the tool, please go to **2. Using SystemSafetyTools**. If you want to compile it yourself, please follow these steps | 如果只想使用工具请转至2. 使用 SystemSafetyTools即可。如果想自己编译请看以下步骤：

## 3.1 Environment Requirements | 环境要求
- Python 3.x
- Windows Operating System | **windows 操作系统**

## 3.2 Build Steps 构建步骤
- Clone or download this project to your local directory. | 克隆或下载本项目到本地目录。

- Open terminal or command prompt in the project root directory. | 在项目根目录下打开终端或命令提示符。

Run the following command to install dependencies (if needed) | 运行以下命令安装依赖项（如果需要）：
   ```bash
    pip install -r requirements.txt
   ```
Use Python to run the script, enter in command line | 使用python运行脚本，在命令行输入：
   ```bash
    python3 system-safety-tools.py
   ```
If needed, you can also use pyinstaller to package the script into a standalone executable | 如果需要也可以使用pyinstaller将脚本打包成独立可执行文件：
   ```bash
    pyinstaller --onefile system-safety-tools.py
   ```
This will generate an executable named SystemSafetyTools.exe (in the dist directory). | 这将生成一个名为SystemSafetyTools.exe的可执行文件（在dist目录下）。

## 3.3 Other Options 其他选项
If needed, you can customize pyinstaller options to meet specific requirements. For example | 如果需要，您还可以自定义pyinstaller的选项来满足特定需求。例如：
   ```bash
    pyinstaller --onefile --name NewName system-safety-tools.py
   ```
Where NewName is your desired exe filename | 其中，NewName是您希望生成的exe文件名称。

If you want to include an icon in the generated exe file, you can use | 如果您希望在生成的exe文件中包含图标，可以使用以下命令：
   ```bash
    pyinstaller --onefile --icon=System-Safety-Tools.ico system-safety-tools.py
   ```
You can also combine them | 您也可以同时添加：
   ```bash
    pyinstaller --onefile --name NewName system-safety-tools.py -i System-Safety-Tools.ico
   ```

## 3.4 Running the Program 运行程序
Double-click the generated SystemSafetyTools.exe file to run the program. | 双击生成的SystemSafetyTools.exe文件即可运行程序。

## Project Structure 项目结构
```
📦 SystemSafetyTools
┣ 📂 config
┃ ┣ 📜 config.py
┃ ┗ 📜 settings_manager.py
┣ 📂 languages
┃ ┗ 📜 language_config.py
┣ 📂 logs
┃ ┗ 📜 system_safety_tools_[timestamp].log
┣ 📜 system-safety-tools.py
┣ 📜 tools.py
┣ 📜 delete_useless_file.py
┣ 📜 log_utils.py
┣ 📜 requirements.txt
┗ 📜 README.md
```

# 6. Notes 注意事项
Before using any system repair or deletion functions, please ensure important data is backed up.
 | 在使用任何系统修复或删除功能之前，请确保已备份重要数据。

This tool is only compatible with Windows operating systems. | 本工具仅适用于Windows操作系统。

# 7. Contact Us 联系我们
If you encounter any issues or have any suggestions during use, please contact us through | 如果您在使用过程中遇到任何问题或有任何建议，请通过以下方式联系我们：

Email: 961521953@qq.com

GitHub Issues: https://github.com/Crs10259/System-Safety-Tools/issues

# 8. License 许可
[MIT License](LICENSE)

## Author 作者

Created by Chen Runsen 