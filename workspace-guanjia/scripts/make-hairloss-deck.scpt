#!/usr/bin/env osascript
tell application "Keynote"
    activate
    
    set doc to make new document with properties {name:"脱发的成因"}
    
    ---------------------------------------------------------------
    -- SLIDE 1: 封面
    ---------------------------------------------------------------
    tell slide 1 of doc
        set background color to {245, 245, 245}
        
        -- 主标题
        make new text item with properties {text:"脱发的成因", font size:72, font color:{30, 30, 30}} at bottom of it
        -- 副标题
        make new text item with properties {text:"中医 vs 现代医学 · 关系图", font size:28, font color:{100, 100, 100}} at bottom of it
    end tell
    
    ---------------------------------------------------------------
    -- SLIDE 2: 中医视角 - 脂溢性脱发
    ---------------------------------------------------------------
    set slide2 to make new slide with properties {layout:blank} of doc
    tell slide2
        set background color to {248, 250, 245}
        
        -- 顶部标题条
        make new shape with properties {fill color:{86, 139, 89}, width:1024, height:80, position:{0, 0}}
        make new text item with properties {text:"中医视角：脂溢性脱发", font size:32, font color:{255,255,255}, position:{30, 20}} at it
        
        -- 左栏：病因病机
        make new text item with properties {text:"病因病机", font size:22, font color:{46, 125, 50}, bold:true, position:{40, 110}} at it
        
        -- 经络关系框
        make new shape with properties {fill color:{230, 255, 232}, width:260, height:90, position:{40, 145}}
        make new text item with properties {text:"经络关系", font size:14, font color:{46, 125, 50}, bold:true, position:{50, 155}} at it
        make new text item with properties {text:"头皮毛囊归属经络\n气血运行不畅", font size:13, font color:{60, 60, 60}, position:{50, 178}} at it
        
        -- 脏腑关系框
        make new shape with properties {fill color:{230, 255, 232}, width:260, height:90, position:{320, 145}}
        make new text item with properties {text:"脏腑关系", font size:14, font color:{46, 125, 50}, bold:true, position:{330, 155}} at it
        make new text item with properties {text:"肾虚为根本\n肝郁、湿热为标", font size:13, font color:{60, 60, 60}, position:{330, 178}} at it
        
        -- 体质关系框
        make new shape with properties {fill color:{230, 255, 232}, width:260, height:90, position:{600, 145}}
        make new text item with properties {text:"体质关系", font size:14, font color:{46, 125, 50}, bold:true, position:{610, 155}} at it
        make new text item with properties {text:"痰湿质↑、阴虚质↑\n平和质↓（研究结论）", font size:13, font color:{60, 60, 60}, position:{610, 178}} at it
        
        -- 向下箭头
        make new shape with properties {fill color:{86, 139, 89}, width:4, height:30, position:{512, 245}} at it
        
        -- 中间：核心病机
        make new shape with properties {fill color:{129, 199, 132}, width:700, height:70, position:{162, 280}}
        make new text item with properties {text:"肾虚为本 · 湿热/血瘀/肝郁为标 → 脂溢性脱发", font size:20, font color:{255,255,255}, bold:true, position:{190, 298}} at it
        
        -- 向下箭头
        make new shape with properties {fill color:{86, 139, 89}, width:4, height:30, position:{512, 360}} at it
        
        -- 底部：危险因素
        make new text item with properties {text:"危险因素", font size:22, font color:{46, 125, 50}, bold:true, position:{40, 405}} at it
        
        -- 三个危险因素框
        make new shape with properties {fill color:{255, 243, 224}, width:280, height:80, position:{40, 438}}
        make new text item with properties {text:"痰湿质", font size:16, font color:{239, 83, 80}, bold:true, position:{50, 448}} at it
        make new text item with properties {text:"油腻、甜食、熬夜\n增大发病风险", font size:13, font color:{60, 60, 60}, position:{50, 470}} at it
        
        make new shape with properties {fill color:{255, 243, 224}, width:280, height:80, position:{370, 438}}
        make new text item with properties {text:"阴虚质", font size:16, font color:{239, 83, 80}, bold:true, position:{380, 448}} at it
        make new text item with properties {text:"津液不足\n头皮失养", font size:13, font color:{60, 60, 60}, position:{380, 470}} at it
        
        make new shape with properties {fill color:{255, 243, 224}, width:280, height:80, position:{700, 438}}
        make new text item with properties {text:"家族遗传史", font size:16, font color:{239, 83, 80}, bold:true, position:{710, 448}} at it
        make new text item with properties {text:"有家族史者\n发病风险增加", font size:13, font color:{60, 60, 60}, position:{710, 470}} at it
        
        -- 数据来源标注
        make new text item with properties {text:"来源：张月月, 2019, 北中医《脂溢性脱发的危险因素及其中医体质关系》", font size:10, font color:{150,150,150}, position:{30, 680}} at it
    end tell
    
    ---------------------------------------------------------------
    -- SLIDE 3: 现代医学视角
    ---------------------------------------------------------------
    set slide3 to make new slide with properties {layout:blank} of doc
    tell slide3
        set background color to {250, 250, 255}
        
        -- 顶部标题条
        make new shape with properties {fill color:{49, 87, 158}, width:1024, height:80, position:{0, 0}}
        make new text item with properties {text:"现代医学视角：雄激素性脱发 (AGA)", font size:32, font color:{255,255,255}, position:{30, 20}} at it
        
        -- 左侧：核心机制
        make new text item with properties {text:"核心机制", font size:20, font color:{25, 51, 120}, bold:true, position:{40, 100}} at it
        
        make new shape with properties {fill color:{232, 240, 255}, width:300, height:120, position:{40, 130}}
        make new text item with properties {text:"二氢睾酮 (DHT)", font size:18, font color:{25, 51, 120}, bold:true, position:{55, 142}} at it
        make new text item with properties {text:"5α-还原酶将睾酮转化为DHT\nDHT与雄激素受体(AR)结合\n启动级联反应→毛囊萎缩", font size:13, font color:{60, 60, 60}, position:{55, 168}} at it
        
        make new shape with properties {fill color:{255, 240, 230}, width:300, height:120, position:{370, 130}}
        make new text item with properties {text:"遗传因素", font size:18, font color:{25, 51, 120}, bold:true, position:{385, 142}} at it
        make new text item with properties {text:"X染色体AR基因\n20号染色体PAX1/FOXA2\n7号染色体HDAC9", font size:13, font color:{60, 60, 60}, position:{385, 168}} at it
        
        -- 中间：两条主线汇聚
        make new shape with properties {fill color:{25, 51, 120}, width:660, height:50, position:{40, 265}}
        make new text item with properties {text:"遗传易感 + 激素作用 → 信号通路紊乱 → 毛囊微型化", font size:18, font color:{255,255,255}, bold:true, position:{70, 278}} at it
        
        -- 信号通路
        make new text item with properties {text:"信号通路失调", font size:20, font color:{25, 51, 120}, bold:true, position:{40, 335}} at it
        
        make new shape with properties {fill color:{240, 245, 255}, width:160, height:90, position:{40, 362}}
        make new text item with properties {text:"Wnt/β-catenin ↓", font size:13, font color:{25, 51, 120}, bold:true, position:{50, 372}} at it
        make new text item with properties {text:"DHT抑制通路\n毛囊再生受阻", font size:11, font color:{80, 80, 80}, position:{50, 395}} at it
        
        make new shape with properties {fill color:{240, 245, 255}, width:160, height:90, position:{215, 362}}
        make new text item with properties {text:"Shh/Gli ↓", font size:13, font color:{25, 51, 120}, bold:true, position:{230, 372}} at it
        make new text item with properties {text:"维持毛囊\n发育受阻", font size:11, font color:{80, 80, 80}, position:{230, 395}} at it
        
        make new shape with properties {fill color:{240, 245, 255}, width:160, height:90, position:{390, 362}}
        make new text item with properties {text:"PI3K/Akt ↓", font size:13, font color:{25, 51, 120}, bold:true, position:{405, 372}} at it
        make new text item with properties {text:"干细胞互动\n毛发再生受阻", font size:11, font color:{80, 80, 80}, position:{405, 395}} at it
        
        make new shape with properties {fill color:{255, 235, 235}, width:160, height:90, position:{565, 362}}
        make new text item with properties {text:"TGF-β/BMP ↑", font size:13, font color:{200, 50, 50}, bold:true, position:{580, 372}} at it
        make new text item with properties {text:"诱导毛囊\n进入休止期", font size:11, font color:{80, 80, 80}, position:{580, 395}} at it
        
        make new shape with properties {fill color:{255, 235, 235}, width:160, height:90, position:{740, 362}}
        make new text item with properties {text:"DKK-1 ↑", font size:13, font color:{200, 50, 50}, bold:true, position:{755, 372}} at it
        make new text item with properties {text:"拮抗Wnt\n抑制毛乳头", font size:11, font color:{80, 80, 80}, position:{755, 395}} at it
        
        -- 微炎症
        make new text item with properties {text:"微炎症 & 氧化应激", font size:20, font color:{25, 51, 120}, bold:true, position:{40, 468}}
        
        make new shape with properties {fill color:{255, 250, 240}, width:920, height:65, position:{40, 495}}
        make new text item with properties {text:"慢性炎症 + 活性氧自由基 → 互促循环 → 加重毛囊损伤", font size:16, font color:{180, 80, 0}, bold:true, position:{70, 515}} at it
        
        -- 生活习惯
        make new text item with properties {text:"生活习惯诱因", font size:20, font color:{25, 51, 120}, bold:true, position:{40, 575}}
        
        make new shape with properties {fill color:{245, 245, 245}, width:145, height:70, position:{40, 603}}
        make new text item with properties {text:"吸烟 ↑", font size:14, font color:{180, 60, 60}, bold:true, position:{55, 613}} at it
        make new text item with properties {text:"尼古丁→血管收缩", font size:11, color:{80,80,80}, position:{50, 637}} at it
        
        make new shape with properties {fill color:{245, 245, 245}, width:145, height:70, position:{195, 603}}
        make new text item with properties {text:"饮酒 ↑", font size:14, font color:{180, 60, 60}, bold:true, position:{210, 613}} at it
        make new text item with properties {text:"ROS↑→微环境失调", font size:11, color:{80,80,80}, position:{200, 637}} at it
        
        make new shape with properties {fill color:{245, 245, 245}, width:145, height:70, position:{350, 603}}
        make new text item with properties {text:"高糖高脂饮食 ↑", font size:14, font color:{180, 60, 60}, bold:true, position:{360, 613}} at it
        make new text item with properties {text:"代谢→心血管风险", font size:11, color:{80,80,80}, position:{360, 637}} at it
        
        make new shape with properties {fill color:{245, 245, 245}, width:145, height:70, position:{505, 603}}
        make new text item with properties {text:"心理压力 ↑", font size:14, font color:{180, 60, 60}, bold:true, position:{515, 613}} at it
        make new text item with properties {text:"HPA轴激活→皮质醇", font size:11, color:{80,80,80}, position:{510, 637}} at it
        
        make new shape with properties {fill color:{245, 245, 245}, width:145, height:70, position:{660, 603}}
        make new text item with properties {text:"睡眠不足 ↑", font size:14, font color:{180, 60, 60}, bold:true, position:{670, 613}} at it
        make new text item with properties {text:"激素分泌紊乱", font size:11, color:{80,80,80}, position:{675, 637}} at it
        
        make new shape with properties {fill color:{245, 245, 245}, width:145, height:70, position:{815, 603}}
        make new text item with properties {text:"头皮微生物 ↑", font size:14, font color:{180, 60, 60}, bold:true, position:{820, 613}} at it
        make new text item with properties {text:"痤疮丙酸杆菌→卟啉", font size:11, color:{80,80,80}, position:{820, 637}} at it
        
        -- 来源
        make new text item with properties {text:"来源：中华整形外科杂志 2025年3月《雄激素性脱发发病机制的研究进展》李宇飞团队", font size:10, font color:{150,150,150}, position:{30, 680}} at it
    end tell
    
    ---------------------------------------------------------------
    -- SLIDE 4: 中西医对照总结
    ---------------------------------------------------------------
    set slide4 to make new slide with properties {layout:blank} of doc
    tell slide4
        set background color to {252, 252, 252}
        
        make new shape with properties {fill color:{80, 80, 80}, width:1024, height:70, position:{0, 0}}
        make new text item with properties {text:"中西医对照：脱发成因全景", font size:30, font color:{255,255,255}, position:{30, 18}} at it
        
        -- 中医列
        make new shape with properties {fill color:{86, 139, 89}, width:460, height:40, position:{32, 95}}
        make new text item with properties {text:"中医视角", font size:20, font color:{255,255,255}, bold:true, position:{220, 100}} at it
        
        make new shape with properties {fill color:{245, 250, 245}, width:460, height:440, position:{32, 140}}
        
        make new text item with properties {text:"本：", font size:16, font color:{46, 125, 50}, bold:true, position:{50, 158}} at it
        make new text item with properties {text:"肾虚", font size:15, font color:{60,60,60}, position:{85, 158}} at it
        
        make new text item with properties {text:"标：", font size:16, font color:{46, 125, 50}, bold:true, position:{50, 188}} at it
        make new text item with properties {text:"湿热 · 血瘀 · 肝郁", font size:15, font color:{60,60,60}, position:{85, 188}} at it
        
        make new text item with properties {text:"关键脏腑：", font size:16, font color:{46, 125, 50}, bold:true, position:{50, 225}} at it
        make new text item with properties {text:"肾、肝、脾", font size:15, font color:{60,60,60}, position:{155, 225}} at it
        
        make new text item with properties {text:"高风险体质：", font size:16, font color:{46, 125, 50}, bold:true, position:{50, 262}} at it
        make new text item with properties {text:"痰湿质、阴虚质", font size:15, font color:{60,60,60}, position:{175, 262}} at it
        
        make new text item with properties {text:"加重因素：", font size:16, font color:{46, 125, 50}, bold:true, position:{50, 299}} at it
        make new text item with properties {text:"油腻饮食、熬夜、情绪压力", font size:15, font color:{60,60,60}, position:{155, 299}} at it
        
        make new text item with properties {text:"治未病：", font size:16, font color:{46, 125, 50}, bold:true, position:{50, 336}} at it
        make new text item with properties {text:"体质三级预防", font size:15, font color:{60,60,60}, position:{125, 336}} at it
        
        make new text item with properties {text:"治疗思路：", font size:16, font color:{46, 125, 50}, bold:true, position:{50, 380}} at it
        make new text item with properties {text:"内治（中药）· 外治（针灸）· 内外合治", font size:14, font color:{80,80,80}, position:{145, 382}} at it
        
        make new text item with properties {text:"文献：", font size:12, color:{150,150,150}, position:{50, 540}} at it
        make new text item with properties {text:"张月月 2019，北中医", font size:12, color:{150,150,150}, position:{50, 558}} at it
        
        -- 现代医学列
        make new shape with properties {fill color:{49, 87, 158}, width:460, height:40, position:{532, 95}}
        make new text item with properties {text:"现代医学视角", font size:20, font color:{255,255,255}, bold:true, position:{650, 100}} at it
        
        make new shape with properties {fill color:{245, 248, 255}, width:460, height:440, position:{532, 140}}
        
        make new text item with properties {text:"始动：", font size:16, font color:{25, 51, 120}, bold:true, position:{550, 158}} at it
        make new text item with properties {text:"DHT + 雄激素受体(AR)", font size:15, font color:{60,60,60}, position:{605, 158}} at it
        
        make new text item with properties {text:"核心酶：", font size:16, font color:{25, 51, 120}, bold:true, position:{550, 195}} at it
        make new text item with properties {text:"Ⅱ型5α-还原酶", font size:15, font color:{60,60,60}, position:{630, 195}} at it
        
        make new text item with properties {text:"基因易感位点：", font size:16, font color:{25, 51, 120}, bold:true, position:{550, 232}} at it
        make new text item with properties {text:"X染色体(AR)、20号染色体", font size:15, font color:{60,60,60}, position:{680, 232}} at it
        
        make new text item with properties {text:"通路紊乱：", font size:16, font color:{25, 51, 120}, bold:true, position:{550, 269}} at it
        make new text item with properties {text:"Wnt↓ Shh↓ PI3K/Akt↓ TGF-β↑", font size:15, font color:{60,60,60}, position:{645, 269}} at it
        
        make new text item with properties {text:"微环境：", font size:16, font color:{25, 51, 120}, bold:true, position:{550, 306}} at it
        make new text item with properties {text:"慢性炎症 + 氧化应激", font size:15, font color:{60,60,60}, position:{630, 306}} at it
        
        make new text item with properties {text:"一线药物：", font size:16, font color:{25, 51, 120}, bold:true, position:{550, 343}} at it
        make new text item with properties {text:"非那雄胺(抑制5α-还原酶)、米诺地尔", font size:14, color:{80,80,80}, position:{640, 345}} at it
        
        make new text item with properties {text:"新兴靶点：", font size:16, font color:{25, 51, 120}, bold:true, position:{550, 385}} at it
        make new text item with properties {text:"降解雄激素受体(PROTAC)、JAK-STAT抑制剂", font size:14, color:{80,80,80}, position:{640, 387}} at it
        
        make new text item with properties {text:"文献：", font size:12, color:{150,150,150}, position:{550, 540}} at it
        make new text item with properties {text:"中华整形外科杂志 2025年3月 李宇飞团队", font size:12, color:{150,150,150}, position:{550, 558}} at it
        
    end tell
    
    save doc in POSIX file "/Users/georginalau/Desktop/脱发的成因.key"
    activate
end tell
