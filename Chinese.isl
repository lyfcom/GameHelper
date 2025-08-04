;
; Inno Setup version 6.0.0 Chinese Simplified Messages
; Copyright (C) 2013-2021 Jordan Russell and many other contributors
; Copyright (C) 2002-2021 Martijn Laan
; Copyright (C) 2009-2017 Deng Fei (a contributor of LSoft.org)
; Copyright (C) 2009-2021 LSoft.org
; Copyright (C) 2021 wonder.cat
; All rights reserved.
;
; See https://jrsoftware.org/files/is-copyright.txt for copyright details.
; See https://jrsoftware.org/files/is-license.txt for license details.

[LangOptions]
LanguageName=简体中文
LanguageID=$0804
LanguageCodePage=936

[Messages]

; *** Application titles
Title255=%1 安装
TitleException=%1 错误

; *** Misc. common
ButAbort=终止(&A)
ButRetry=重试(&R)
ButIgnore=忽略(&I)
ButLimited=有限(&L)
ButOK=确定
ButCancel=取消
ButYes=是(&Y)
ButNo=否(&N)
ButFinish=完成(&F)
ButBrowse=浏览(&B)...
ButBack=< 上一步(&B)
ButNext=下一步(&N) >

; *** Setup Status Form
StatusSetup=正在准备安装...
StatusSetupComplete=安装完成
StatusInstall=正在安装...
StatusRollback=正在撤销更改...
StatusUninstall=正在卸载...
StatusUninstallComplete=卸载完成
StatusPleaseWait=请稍候...

; *** Error messages
ConfirmUninstall=您确定要完全删除 %1 以及其所有组件吗？
ConfirmUninstallDLL=您确定要删除 %1 吗？其他程序如果正在使用该文件，删除后可能会无法正常运行。
ErrorFileCorrupt=安装文件已损坏。请获取一个新的文件副本。
ErrorFileCorruptOrWrongVer=安装文件已损坏，或与此版本的安装程序不兼容。请更正错误或获取一个新的文件副本。
ErrorFileOpen=打开文件“%1”时出错。
ErrorFileRead=读取文件“%1”时出错。
ErrorFileWrite=写入文件“%1”时出错。
ErrorFileNotFound=找不到文件“%1”。
ErrorInvalidOpcode=安装文件已损坏：无效的操作代码 %1。
ErrorNeedsRestart=此安装程序必须重新启动计算机。
ErrorNotEnoughDiskSpace=您的驱动器上没有足够的可用磁盘空间来完成安装。

; *** Strings used by Setup Wizard
WizardWelcome=欢迎使用 %1 安装向导
WelcomeLabel1=此向导将引导您完成 %1 %2 的安装过程。
WelcomeLabel2=在开始安装前，我们建议您关闭其他所有应用程序。
WizardSelectDir=选择目标位置
SelectDirLabel=您想将 %1 安装在何处？
SelectDirDesc=安装向导将把 %1 安装到以下文件夹中。
DiskSpaceRequired=所需磁盘空间：%1
WizardSelectComponents=选择组件
SelectComponentsLabel=选择您想要安装的组件
SelectComponentsDesc=选择您想要安装的组件；清除您不想安装的组件。单击“下一步”继续。
WizardSelectProgramGroup=选择开始菜单文件夹
SelectStartMenuFolderLabel=您想将程序的快捷方式放在何处？
SelectStartMenuFolderDesc=安装向导将在下列开始菜单文件夹中创建快捷方式。
WizardSelectTasks=选择附加任务
SelectTasksLabel=选择附加任务
SelectTasksDesc=选择在安装 %1 时需要执行的附加任务。
WizardReady=准备安装
ReadyLabel1=安装向导已准备好开始安装 %1。
ReadyLabel2=单击“安装”继续此安装程序。如果您想回顾或修改设置，请单击“上一步”。
ReadyMemo=目标位置：
ReadyMemoComponents=选择的组件：
ReadyMemoGroup=开始菜单文件夹：
ReadyMemoTasks=附加任务：
WizardInstalling=正在安装
InstallingLabel=安装向导正在您的计算机中安装 %1，请稍候。
WizardFinished=完成 %1 安装向导
FinishedLabel=安装向导已在您的计算机中完成 %1 的安装。
FinishedLabel_Checked=应用程序已安装成功。单击“完成”退出此向导。
FinishedLabel_Unchecked=单击“完成”退出此向导。
FinishedLink=访问 %1 网站(&V)
ClickFinish=单击“完成”退出安装程序。
FinishedRestart=要完成 %1 的安装，安装程序必须重新启动您的计算机。
FinishedRestartMessage=您想现在重新启动吗？
FinishedRestartMessageSys=要完成 %1 的安装，安装程序必须重新启动您的计算机。建议您现在重新启动。

; *** Used by Uninstall Wizard
ConfirmUninstall=您确定要完全删除 %1 以及其所有组件吗？
UninstallStatusScreen=卸载状态
UninstallStatusLabel=正在从您的计算机中卸载 %1，请稍候。
UninstallFinishedScreen=卸载完成
UninstallFinishedLabel=已成功地从您的计算机中删除 %1。
UninstallError=卸载错误
UninstallOpenError=无法打开 %1 进行卸载。
UninstallResError=无法加载或找到卸载程序资源。

; *** Other messages
Information=信息
Error=错误
Warning=警告
PrivilegesRequired=此安装需要管理员权限。
PrivilegesRequiredOverride=此安装需要管理员权限。是否以管理员身份重试？
SetupAppRunning=安装程序检测到 %1 正在运行。
SetupAppRunningMessage=请在继续前关闭所有 %1 的实例。
ExitSetupTitle=退出安装程序
ExitSetupMessage=安装尚未完成。如果您现在退出，程序将不会被安装。
ExitSetupMessage2=您可以以后重新运行安装程序以完成安装。
ExitSetupMessage3=要继续安装，请单击“恢复”。要退出安装程序，请单击“是”。
AboutSetup=关于安装程序
AboutSetupTitle=关于安装程序
AboutSetupMessage=%1 版本 %2
AboutSetupMessage2=由 %1 创建
AboutSetupMessage3=有关 %1 的更多信息，请访问：
AboutSetupMessage4=由 Inno Setup 创建。

[CustomMessages]
NameAndVersion=%1 版本 %2
AdditionalIcons=附加图标：
CreateDesktopIcon=创建桌面快捷方式(&D)
LaunchProgram=运行 %1
And=和
Comma=,
Space= 
Dot=
TheAboveKeysWereNotFound=未找到以上注册表键值。
InWhatLanguage=请选择安装期间要使用的语言：
Language=语言
Languages=语言
English=英语
Chinese=中文
French=法语
German=德语
Italian=意大利语
Japanese=日语
Korean=韩语
Portuguese=葡萄牙语
Russian=俄语
Spanish=西班牙语

; *** Used by setup command line processor
HelpText=用法：
HelpText1= /? | /HELP
HelpText2= [/SILENT | /VERYSILENT] [/SUPPRESSMSGBOXES] [/LOG] [/LOG="filename"] [/DIR="x:\dirname"] [/GROUP="folder name"] [/NOICONS] [/COMPONENTS="comma separated list of component names"] [/TASKS="comma separated list of task names"]
HelpText3=/?  /HELP                   显示此帮助信息。
HelpText4=/SILENT, /VERYSILENT     静默安装（不显示对话框）。
HelpText5=/SUPPRESSMSGBOXES        禁止显示消息框。仅在与 /SILENT 或 /VERYSILENT 一起使用时有效。
HelpText6=/LOG                      在用户的 TEMP 目录中创建日志文件。
HelpText7=/LOG="filename"           在指定的文件中创建日志文件。
HelpText8=/DIR="x:\dirname"         覆盖默认的安装目录。
HelpText9=/GROUP="folder name"      覆盖默认的开始菜单文件夹名称。
HelpText10=/NOICONS                 禁止创建开始菜单快捷方式。
HelpText11=/COMPONENTS=...          仅安装指定的组件。
HelpText12=/TASKS=...               仅执行指定的任务。
HelpText13=/SAVEINF="filename"      将安装设置保存到指定文件。
HelpText14=/LOADINF="filename"      从指定文件加载安装设置。
HelpText15=/LANG=language           指定安装语言。
HelpText16=/PASSWORD=password       指定安装密码。
HelpText17=/TYPE=type name          指定安装类型。
HelpText18=/NORESTART               禁止在安装完成后重新启动计算机。
HelpText19=/RESTARTEXITCODE=exitcode 在需要重新启动时返回此退出代码。
HelpText20=/FONT=name               指定主窗口字体名称。
HelpText21=/SIZE=width,height       指定主窗口宽度和高度。
HelpText22=/TITLE=title             指定主窗口标题。
HelpText23=/USEDRIVER=driver name   指定驱动程序名称。

; *** Used by uninstall command line processor
UninstallHelpText=用法：
UninstallHelpText1= /? | /HELP
UninstallHelpText2= [/SILENT | /VERYSILENT] [/SUPPRESSMSGBOXES] [/LOG] [/LOG="filename"]
UninstallHelpText3=/?  /HELP                   显示此帮助信息。
UninstallHelpText4=/SILENT, /VERYSILENT     静默卸载。
UninstallHelpText5=/SUPPRESSMSGBOXES        禁止显示消息框。仅在与 /SILENT 或 /VERYSILENT 一起使用时有效。
UninstallHelpText6=/LOG                      在用户的 TEMP 目录中创建日志文件。
UninstallHelpText7=/LOG="filename"           在指定的文件中创建日志文件。
UninstallHelpText8=/NORESTART               禁止在卸载完成后重新启动计算机。
