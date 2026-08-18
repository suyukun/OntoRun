来源: https://palantir.com/docs/zh/foundry/pb-functions-expression/polygonToH3V1/

# 获取覆盖几何图形的H3索引

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 获取覆盖几何图形的H3索引

> 支持于: 批处理, 流式

支持于: 批处理, 流式

将几何图形转换为特定分辨率的H3索引。分辨率必须在0到15之间（含）。对于多边形，支持三种转换：a) 完全覆盖多边形的H3索引，b) 完全包含于多边形内的H3索引，c) 其重心包含在多边形内的H3索引。当预期的H3索引数量超过700万时，返回null。

表达式类别: 地理空间

## 声明的参数

- 覆盖类型- 指定多边形的H3覆盖类型。枚举<Centroid, Inner, Outer>
- 几何图形- GeoJSON类型的多边形、线或点。表达式<Geometry>
- 分辨率- H3网格分辨率在0到15之间（含）。表达式<Byte | Integer | Long | Short>
输出类型:数组<H3 索引>

## 示例

### 示例 1: 基本情况

参数值:

- 覆盖类型:CENTROID
- 几何图形:polygon
- 分辨率: 5
| 多边形 | 输出 |
| --- | --- |
| {"type":"Polygon","coordinates":[[[-121.91508032705622,37.2713558667319],[-121.86222328902491,37.353... | [ 85283473fffffff ] |
| null | null |
| {"type":"Polygon","coordinates":[[]]} | [  ] |
| {"type":"Polygon","coordinates":[]} | null |
| {"type":"MultiPolygon","coordinates":[[]]} | null |
| {"type":"MultiPolygon","coordinates":[[[],[]]]} | [  ] |
| {"type":"MultiPolygon","coordinates":[]} | [  ] |

### 示例 2: 基本情况

参数值:

- 覆盖类型:CENTROID
- 几何图形:polygon
- 分辨率: 6
| 多边形 | 输出 |
| --- | --- |
| {"type":"Polygon","coordinates":[[[-121.91508032705622,37.2713558667319],[-121.86222328902491,37.353... | [ 862834707ffffff, 86283470fffffff, 862834717ffffff, 86283471fffffff, 862834727ffffff, 86283472fffffff, 862834737ffffff ] |
| {"type":"Polygon","coordinates":[[[-121.91508032705622,37.2713558667319],[-121.86222328902491,37.353... | [ 862834707ffffff, 86283470fffffff, 862834717ffffff, 86283471fffffff, 862834727ffffff, 86283472fffffff, 862834737ffffff, 8628347a7ffffff ] |

### 示例 3: 基本情况

参数值:

- 覆盖类型:INNER
- 几何图形:polygon
- 分辨率: 6
| 多边形 | 输出 |
| --- | --- |
| {"type":"Polygon","coordinates":[[[-121.91508032705622,37.2713558667319],[-121.86222328902491,37.353... | [ 862834707ffffff ] |
| {"type":"Polygon","coordinates":[[[-121.91508032705622,37.2713558667319],[-121.86222328902491,37.353... | [ 862834707ffffff, 862834717ffffff ] |

### 示例 4: 基本情况

参数值:

- 覆盖类型:OUTER
- 几何图形:polygon
- 分辨率: 6
| 多边形 | 输出 |
| --- | --- |
| {"type":"Polygon","coordinates":[[[-121.91508032705622,37.2713558667319],[-121.86222328902491,37.353... | [ 86283408fffffff, 86283409fffffff, 8628340d7ffffff, 8628340dfffffff, 86283444fffffff, 86283446fffff... |
| {"type":"Polygon","coordinates":[[[-121.91508032705622,37.2713558667319],[-121.86222328902491,37.353... | [ 86283408fffffff, 86283409fffffff, 8628340d7ffffff, 8628340dfffffff, 86283444fffffff, 86283445fffff... |

### 示例 5: 基本情况

参数值:

- 覆盖类型:OUTER
- 几何图形:polygon
- 分辨率: 2
| 多边形 | 输出 |
| --- | --- |
| {"coordinates":[[[-112.94377956164206,34.81725414459382],[-112.94377956164206,33.006795384733323], [... | [ 82264ffffffffff, 82265ffffffffff, 8226c7fffffffff, 8226cffffffffff, 8226d7fffffffff, 8226dffffffff... |

### 示例 6: 基本情况

参数值:

- 覆盖类型:INNER
- 几何图形:polygon
- 分辨率: 5
| 多边形 | 输出 |
| --- | --- |
| {"type":"Polygon","coordinates":[[[-121.91508032705622,37.2713558667319],[-121.86222328902491,37.353... | [ 85283473fffffff ] |
| null | null |
| {"type":"Polygon","coordinates":[[]]} | [  ] |
| {"type":"Polygon","coordinates":[]} | null |
| {"type":"MultiPolygon","coordinates":[[]]} | null |
| {"type":"MultiPolygon","coordinates":[[[],[]]]} | [  ] |
| {"type":"MultiPolygon","coordinates":[]} | [  ] |

### 示例 7: 基本情况

参数值:

- 覆盖类型:CENTROID
- 几何图形:polygon
- 分辨率: 4
| 多边形 | 输出 |
| --- | --- |
| {"type":"Polygon","coordinates":[[[-121.91508032705622,37.2713558667319],[-121.86222328902491,37.353... | [  ] |
| {"type":"Polygon","coordinates":[[[-121.91508032705622,37.2713558667319],[-121.86222328902491,37.353... | [  ] |

### 示例 8: 基本情况

参数值:

- 覆盖类型:INNER
- 几何图形:polygon
- 分辨率: 4
| 多边形 | 输出 |
| --- | --- |
| {"type":"Polygon","coordinates":[[[-121.91508032705622,37.2713558667319],[-121.86222328902491,37.353... | [  ] |
| {"type":"Polygon","coordinates":[[[-121.91508032705622,37.2713558667319],[-121.86222328902491,37.353... | [  ] |

### 示例 9: 基本情况

参数值:

- 覆盖类型:OUTER
- 几何图形:polygon
- 分辨率: 4
| 多边形 | 输出 |
| --- | --- |
| {"type":"Polygon","coordinates":[[[-121.91508032705622,37.2713558667319],[-121.86222328902491,37.353... | [ 8428341ffffffff, 8428345ffffffff, 8428347ffffffff ] |
| {"type":"Polygon","coordinates":[[[-121.91508032705622,37.2713558667319],[-121.86222328902491,37.353... | [ 8428341ffffffff, 8428345ffffffff, 8428347ffffffff ] |

### 示例 10: 基本情况

参数值:

- 覆盖类型:OUTER
- 几何图形:polygon
- 分辨率: 5
| 多边形 | 输出 |
| --- | --- |
| null | null |
| {"type":"Polygon","coordinates":[[]]} | [  ] |
| {"type":"Polygon","coordinates":[]} | null |
| {"type":"MultiPolygon","coordinates":[[]]} | null |
| {"type":"MultiPolygon","coordinates":[[[],[]]]} | [  ] |
| {"type":"MultiPolygon","coordinates":[]} | [  ] |
| {"type":"Polygon","coordinates":[[[-121.91508032705622,37.2713558667319],[-121.86222328902491,37.353... | [ 8528340bfffffff, 8528340ffffffff, 85283447fffffff, 85283463fffffff, 85283473fffffff, 85283477fffffff, 8528347bfffffff ] |

### 示例 11: 基本情况

参数值:

- 覆盖类型:CENTROID
- 几何图形:polygon
- 分辨率: 3
| 多边形 | 输出 |
| --- | --- |
| {"type":"MultiLineString","coordinates":[[[0,0],[15,15],[30,-15],[45,15],[60,0]],[[15,30],[-15,-15]]]} | [ 833f80fffffffff, 833f82fffffffff, 833f85fffffffff, 833f91fffffffff, 833f93fffffffff, 833faefffffff... |

### 示例 12: 基本情况

参数值:

- 覆盖类型:CENTROID
- 几何图形:polygon
- 分辨率: 4
| 多边形 | 输出 |
| --- | --- |
| {"type":"MultiPoint","coordinates":[[60,60],[60,58],[58,58],[58,60]]} | [ 8410c03ffffffff, 8410c47ffffffff, 8410ee7ffffffff, 8410eedffffffff ] |

### 示例 13: 基本情况

参数值:

- 覆盖类型:OUTER
- 几何图形:polygon
- 分辨率: 10
| 多边形 | 输出 |
| --- | --- |
| {"type":"Polygon","coordinates":[[[-122.02869363438222,37.26184847647239],[-122.02805421389088,37.26... | [ 8a283408b2c7fff, 8a283408b2cffff, 8a283408b2dffff, 8a283408b2effff, 8a28340d6597fff, 8a28340d65b7fff, 8a2834725967fff ] |

### 示例 14: 基本情况

参数值:

- 覆盖类型:CENTROID
- 几何图形:polygon
- 分辨率: 4
| 多边形 | 输出 |
| --- | --- |
| {"coordinates":[[[[60,60],[60,58],[58,58],[58,60],[60,60]],[[59.5,59.7],[59.8,58.1],[58.1,58.2],[58.2,59.4],[59.5,59.7]]], [[[55,56],[55.5,55.7],[55.7,55.7],[55,57],[55,56]]]],"type":"MultiPolygon"} | [ 8410c01ffffffff, 8410c47ffffffff, 8410c57ffffffff, 8410e33ffffffff, 8410ee5ffffffff, 8410ee7ffffffff, 8410f23ffffffff ] |

### 示例 15: 基本情况

参数值:

- 覆盖类型:INNER
- 几何图形:polygon
- 分辨率: 4
| 多边形 | 输出 |
| --- | --- |
| {"coordinates":[[[[60,60],[60,58],[58,58],[58,60],[60,60]],[[59.5,59.7],[59.8,58.1],[58.1,58.2],[58.2,59.4],[59.5,59.7]]], [[[55,56],[55.5,55.7],[55.7,55.7],[55,57],[55,56]]]],"type":"MultiPolygon"} | [  ] |

### 示例 16: 基本情况

参数值:

- 覆盖类型:OUTER
- 几何图形:polygon
- 分辨率: 4
| 多边形 | 输出 |
| --- | --- |
| {"coordinates":[[[[60,60],[60,58],[58,58],[58,60],[60,60]],[[59.5,59.7],[59.8,58.1],[58.1,58.2],[58.2,59.4],[59.5,59.7]]], [[[55,56],[55.5,55.7],[55.7,55.7],[55,57],[55,56]]]],"type":"MultiPolygon"} | [ 8410c01ffffffff, 8410c03ffffffff, 8410c09ffffffff, 8410c0bffffffff, 8410c0dffffffff, 8410c1dffffff... |

### 示例 17: 基本情况

参数值:

- 覆盖类型:OUTER
- 几何图形:polygon
- 分辨率: 3
| 多边形 | 输出 |
| --- | --- |
| {"coordinates":[[[60.0,60.0],[50.0,60.0],[50.0,50.0],[60.0,50.0],[60.0,60.0]],[[57.0,57.0],[55.0,52.0],[52.0,52.0],[50.0,57.0],[57.0,57.0]]],"type":"Polygon"} | [ 83100afffffffff, 831018fffffffff, 831019fffffffff, 83101afffffffff, 83101bfffffffff, 83101dfffffff... |

### 示例 18: 基本情况

参数值:

- 覆盖类型:CENTROID
- 几何图形:polygon
- 分辨率: 4
| 多边形 | 输出 |
| --- | --- |
| {"type":"MultiLineString","coordinates":[[[60,60],[60,58],[58,58],[58,60]],[[59.8,58.1],[58.1,58.2],[58.2,59.4],[59.5,59.7]],[[55,56],[55.5,55.7],[55.7,55.7],[55,57]]]} | [ 8410c01ffffffff, 8410c03ffffffff, 8410c09ffffffff, 8410c0bffffffff, 8410c0dffffffff, 8410c1dffffff... |

### 示例 19: 基本情况

参数值:

- 覆盖类型:OUTER
- 几何图形:polygon
- 分辨率: 9
| 多边形 | 输出 |
| --- | --- |
| {"coordinates":[[[-110, 38], [-110,82],[-170,82],[-170,38],[-110, 38]]],"type":"Polygon"} | null |
