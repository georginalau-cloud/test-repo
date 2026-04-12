name: bazi_detailed_analyzer 

description: 八字精批分析。当用户请求八字分析、命盘分析、五行分析、运势预测、大运分析、流年预测、妻财子禄寿分析、结构化八字精批时，必须调用此技能。

八字精批分析技能

⚠️ 最重要的规则

必须通过 bin/bazi 入口脚本调用，禁止直接运行底层 Python 模块。

调用的正确方式：

python3 skill/suanming/bin/bazi --year <年> --month <月> --day <日> --hour <时> --minute <分> --gender <male|female> --city <城市> --level full

注意：

入口脚本是 bin/bazi
不要直接调用 lib/ 或 reference/ 里的底层文件
最终输出应由 src/analyzer_generator.py 统一生成
触发条件

当用户说以下内容时，立即调用 exec 工具：

算八字 / 帮我算八字 / 精批八字
八字分析 / 八字精批
命盘分析 / 命盘
五行分析
运势预测 / 看运势
大运分析 / 流年预测
妻财子禄寿分析
任何提供出生年月日时分并请求命理分析的情况
调用方法

使用 exec 工具，workdir 设为项目根目录：

{ "command": "python3 skill/suanming/bin/bazi --year <年> --month <月> --day <日> --hour <时> --minute <分> --gender <male|female> --city <城市> --level full", "workdir": ".", "timeout": 600 }

参数说明

参数      | 必填 | 说明 

--year   | ✅   | 出生年（4位数字，如 1990） 

--month  | ✅   | 出生月（1-12） 

--day    | ✅   | 出生日（1-31） 
--hour   | ✅   | 出生小时（24小时制，如 15 表示下午3点） 
--minute | ✅   | 出生分钟（0-59，必须写，用户说"15:45"就要写 --minute 45） 
--gender | ✅   | male 或 female 
--city   | ✅   | 出生城市（用于真太阳时计算，如"西安""北京"） 
--level  | ✅   | 必须写 full

调用示例

用户说： "1990年1月8日下午3点45分 女 西安"

--year 1990 --month 1 --day 8 --hour 15 --minute 45 --gender female --city 西安 --level full

用户说： "请帮我分析 1990年8月20日 早上10点 女命，出生地杭州"

--year 1990 --month 8 --day 20 --hour 10 --minute 0 --gender female --city 杭州 --level full

用户说： "帮我看看 1990年1月15日 男 西安 8点"

--year 1990 --month 1 --day 15 --hour 8 --minute 0 --gender male --city 西安 --level full

输出层级说明

此技能的输出分为四层：

第一层：排盘
输出：
基本信息
真太阳时换算结果
阴历换算结果
八字原局
原局排盘细节
8 个大运及每运干支十神


第二层：分析
输出：
技术分析
实战分析（妻财子禄寿）
支持的分析层级包括：
原局
--原局 + 大运
--原局 + 大运 + 流年
--原局 + 大运 + 流年 + 流月
--原局 + 大运 + 流年 + 流月 + 流日


第三层：结构化整合
输出：
排盘信息
身强弱
格局
喜用忌
全局精批（妻财子禄寿）
当前大运精批（妻财子禄寿）
当前大运 + 流年精批（妻财子禄寿）


第四层：最终输出
不追问时，直接输出结构化结果
用户继续追问时，按第三层内容继续深挖，可 zoom in 到任意流年、流月、流日


重要规则

必须通过 bin/bazi 入口，禁止直接调用 lib/ 或 reference/ 里的文件
必须传 --minute 参数，分钟不能省略
必须传 --city，真太阳时计算需要
脚本输出应为结构化结果，优先返回最终摘要和 full_report
如果脚本执行失败，读取错误输出，分析原因并修复；无法修复时告知用户并建议重试
reference/books/ 用于典籍引用
reference/examples/ 用于格局案例引用
reference/tools/ 用于底层命理工具与数据支持

