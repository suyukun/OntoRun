来源: https://palantir.com/docs/zh/foundry/transforms-python/pyspark-strings/

# 字符串

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 字符串

字符串指的是文本数据。

## 转换大小写

- F.initcap(col)
- F.lower(col)
- F.upper(col)
## 连接与分割

- F.concat(*cols)
- F.concat_ws(sep, *cols)
- F.split(str, pattern)
## 子字符串

- F.instr(str, substr)
- F.locate(substr, str, pos=1)
- F.substring(str, pos, len)
- F.substring_index(str, delim, count)
## 修剪与填充

- F.lpad(col, len, pad)
- F.ltrim(col)
- F.rpad(col, len, pad)
- F.rtrim(col)
- F.trim(col)
## 正则表达式

- F.regexp_extract(str, pattern, idx)
- F.regexp_replace(str, pattern, replacement)
## 其他

- F.ascii(col)
- F.base64(col)
- F.bin(col)
- F.conv(col, fromBase, toBase)
- F.decode(col, charset)
- F.encode(col, charset)
- F.format_number(col, d)
- F.format_string(format, *cols)
- F.hex(col)
- F.length(col)
- F.levenshtein(left, right)
- F.repeat(col, n)
- F.reverse(col)
- F.translate(srcCol, matching, replace)
- F.unbase64(col)
- F.unhex(col)