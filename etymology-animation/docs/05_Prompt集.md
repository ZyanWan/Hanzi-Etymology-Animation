# Prompt 集

## 通用构造公式

为任何新字写 Prompt，按以下公式填空：

```
【中文版（通用）】

一张白底黑字的[朝代]时期"[字]"字拓片，
字形像[用 5-10 个字描述甲骨文的形状]，
笔画缓慢变形，过渡为[朝代]风格的"[字]"字，
[描述目标字形的变化特点]，
保持字形完整不变形，
书法风格，画面稳定，平滑过渡，[时长]秒

【英文版（Sora/Runway）】

A close-up of the Chinese character "[字]" on white paper.
Starting as a [朝代] [字形类型] inscription showing [形状描述],
the black strokes smoothly morph into [朝代] [字形风格] style,
[描述变化过程].
Calligraphy aesthetic, stable camera, smooth transition, [时长] seconds.
```

---

## 可灵 (Kling) Prompt

### 通用模板（首尾帧模式）

```
白底黑字的[朝代]字形，平滑变形过渡为[朝代]字形，
保持字形完整不变形，笔画自然过渡，
书法风格，画面稳定，无抖动，2秒
```

### 通用模板（无首尾帧）

```
一张白底黑字的[朝代]时期"[字]"字拓片，
字形[描述形状]，
笔画缓慢变形，过渡为[朝代]风格的"[字]"字，
[描述目标字形特点]，
保持字形完整不变形，
书法风格，画面稳定，平滑过渡，2秒
```

### "取"字逐段

**甲骨文 → 金文：**
```
一张白底黑字的商朝甲骨文"取"字拓片，
字形像左边一只耳朵、右边一只手，
笔画缓慢变形，过渡为西周青铜器铭文风格的"取"字，
字形变得更规整，笔画从尖锐变为圆润厚重，
保持"耳"和"又"两个部件的结构不变，
画面稳定，平滑过渡，2秒
```

**金文 → 小篆：**
```
一张白底黑字的西周金文"取"字，
笔画缓慢变形，过渡为秦朝小篆风格的"取"字，
线条从粗犷变为均匀圆润，结构从宽扁变为修长，
保持字形完整不变形，
篆书风格，画面稳定，平滑过渡，2秒
```

**小篆 → 楷书：**
```
一张白底黑字的秦朝小篆"取"字，
笔画缓慢变形，过渡为现代楷书"取"字，
线条从圆润变为方折，转折处从弧形变为直角，
保持字形完整不变形，
楷书风格，画面稳定，平滑过渡，2秒
```

### "采"字逐段

**甲骨文 → 金文：**
```
一张白底黑字的商朝甲骨文"采"字拓片，
字形像上面一只手（爪）、下面一棵树（木），
手在树上摘果子的样子，
笔画缓慢变形，过渡为西周金文风格的"采"字，
手和树的形状变得更规整，
保持上下结构不变，
画面稳定，平滑过渡，2秒
```

**金文 → 楷书：**
```
一张白底黑字的西周金文"采"字，
笔画缓慢变形，过渡为现代楷书"采"字，
线条从圆润变为方折，"爪"在上"木"在下，
保持字形完整不变形，
楷书风格，画面稳定，平滑过渡，2秒
```

### "休"字逐段

**甲骨文 → 金文：**
```
一张白底黑字的商朝甲骨文"休"字拓片，
字形像左边一个人（亻）、右边一棵树（木），
人靠在树旁休息的样子，
笔画缓慢变形，过渡为西周金文风格的"休"字，
人和树的形状变得更规整，
保持左右结构不变，
画面稳定，平滑过渡，2秒
```

**金文 → 楷书：**
```
一张白底黑字的西周金文"休"字，
笔画缓慢变形，过渡为现代楷书"休"字，
线条从圆润变为方折，"亻"在左"木"在右，
保持字形完整不变形，
楷书风格，画面稳定，平滑过渡，2秒
```

### 象形字（一段完成）

**"日"字：**
```
一张白底黑字的商朝甲骨文"日"字拓片，
字形像一个圆圈中间有一个点，代表太阳，
笔画缓慢变形，圆圈逐渐变为方形，
中间的点逐渐变为一横，
最终过渡为现代楷书"日"字，
保持字形完整不变形，
书法风格，画面稳定，平滑过渡，3秒
```

**"山"字：**
```
一张白底黑字的商朝甲骨文"山"字拓片，
字形像三座尖尖的山峰，中间最高，
笔画缓慢变形，山峰的尖角逐渐变平，
三条竖线逐渐规整，
最终过渡为现代楷书"山"字，
保持字形完整不变形，
书法风格，画面稳定，平滑过渡，3秒
```

**"水"字：**
```
一张白底黑字的商朝甲骨文"水"字拓片，
字形像一条弯曲流动的河流，两边有水花飞溅，
笔画缓慢变形，曲线逐渐变直，
水花逐渐变为点和提，
最终过渡为现代楷书"水"字，
保持字形完整不变形，
书法风格，画面稳定，平滑过渡，3秒
```

**"明"字：**
```
一张白底黑字的商朝甲骨文"明"字拓片，
字形像左边一个太阳（日）、右边一个月亮（月），
日月并列，代表光明，
笔画缓慢变形，太阳和月亮的形状逐渐简化，
最终过渡为现代楷书"明"字，"日"在左"月"在右，
保持字形完整不变形，
书法风格，画面稳定，平滑过渡，3秒
```

**"男"字：**
```
一张白底黑字的商朝甲骨文"男"字拓片，
字形像上面一块田、下面一个农具（力），
在田里用力干活的人，
笔画缓慢变形，田和力的形状逐渐简化，
最终过渡为现代楷书"男"字，"田"在上"力"在下，
保持字形完整不变形，
书法风格，画面稳定，平滑过渡，3秒
```

**"木"字：**
```
一张白底黑字的商朝甲骨文"木"字拓片，
字形像一棵树，上面有树枝，下面有树根，
笔画缓慢变形，树枝和树根逐渐简化，
最终过渡为现代楷书"木"字，
保持字形完整不变形，
书法风格，画面稳定，平滑过渡，3秒
```

**"人"字：**
```
一张白底黑字的商朝甲骨文"人"字拓片，
字形像一个人侧身弯腰站立，
笔画缓慢变形，身体逐渐简化为两笔，
最终过渡为现代楷书"人"字，
保持字形完整不变形，
书法风格，画面稳定，平滑过渡，3秒
```

---

## Sora / Runway Prompt

### 通用模板（分段）

```
A close-up of the Chinese character "[字]" on white paper.
Starting as a [朝代] [字形类型] inscription showing [形状描述],
the black strokes smoothly morph into [朝代] [字形风格] style,
[描述变化过程].
Calligraphy aesthetic, stable camera, smooth transition, 2 seconds.
```

### 通用模板（完整演变）

```
A close-up of the Chinese character "[字]" transforming through Chinese history.
Starting as a Shang dynasty Oracle Bone Script carving showing [形状描述],
the form smoothly morphs into Western Zhou Bronze Script inscription style,
then transforms into Qin dynasty Seal Script with rounded uniform strokes,
finally settling into modern Regular Script "[字]".
Black ink on white paper, calligraphy museum aesthetic,
stable camera, smooth transition, 5 seconds.
```

### 完整演变示例

**"取"字：**
```
A close-up of the Chinese character "取" transforming through Chinese history.
Starting as a Shang dynasty Oracle Bone Script carving showing a hand grabbing an ear,
the form smoothly morphs into Western Zhou Bronze Script inscription style with thicker strokes,
then transforms into Qin dynasty Seal Script with rounded uniform strokes,
finally settling into modern Regular Script "取" with squared strokes.
Black ink on white paper, calligraphy museum aesthetic,
stable camera, cinematic lighting, smooth transition, 5 seconds.
```

**"采"字：**
```
A close-up of the Chinese character "采" transforming through Chinese history.
Starting as a Shang dynasty Oracle Bone Script carving showing a hand reaching into a tree to pick fruit,
the form smoothly morphs into Western Zhou Bronze Script inscription style,
then transforms into Qin dynasty Seal Script with rounded strokes,
finally settling into modern Regular Script "采".
Black ink on white paper, calligraphy museum aesthetic,
stable camera, smooth transition, 5 seconds.
```

**"休"字：**
```
A close-up of the Chinese character "休" transforming through Chinese history.
Starting as a Shang dynasty Oracle Bone Script carving showing a person leaning against a tree to rest,
the form smoothly morphs into Western Zhou Bronze Script inscription style,
then transforms into Qin dynasty Seal Script with rounded strokes,
finally settling into modern Regular Script "休".
Black ink on white paper, calligraphy museum aesthetic,
stable camera, smooth transition, 5 seconds.
```
