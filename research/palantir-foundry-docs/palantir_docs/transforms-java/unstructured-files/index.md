来源: https://palantir.com/docs/zh/foundry/transforms-java/unstructured-files/

# 读取和写入非结构化文件

注意：以下翻译的准确性尚未经过验证。这是使用AIP ↗从原始英文文本进行的机器翻译。

# 读取和写入非结构化文件

这里的示例包含更高级的内容。在阅读本节之前，请确保先阅读定义变换的部分。

本页面包含使用 Java 变换进行数据变换的各种示例：

- 使用 Spark 进行并行处理解压数据集文件并写入输出文件系统解压数据集文件并写入输出数据框
- 解压数据集文件并写入输出文件系统
- 解压数据集文件并写入输出数据框
- 合并数据集文件
这里的示例是以文件形式表达的数据变换。如果您想在变换中访问文件，必须定义低级别的Transform。这是因为底层数据集文件是通过FoundryInput和FoundryOutput对象暴露的。低级别变换与高级别变换不同，期望计算函数的输入和输出分别为FoundryInput和FoundryOutput类型。所包含的示例也是用于手动注册的低级别变换。

## 使用 Spark 进行并行处理

### 解压数据集文件并写入输出文件系统

此示例将.zip文件作为输入。它解压文件，然后将文件写入输出文件系统——由于.zip文件不可分割，因此这项工作是使用 Spark 按每个.zip文件并行完成的。如果您想在单个压缩文件内并行解压，请使用可分割的文件格式，如.bz2。

```
Copied!1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
/*
 * (c) Copyright 2018 Palantir Technologies Inc. All rights reserved.
 */
package com.palantir.transforms.java.examples;

import com.google.common.io.ByteStreams;
import com.palantir.transforms.lang.java.api.Compute;
import com.palantir.transforms.lang.java.api.FoundryInput;
import com.palantir.transforms.lang.java.api.FoundryOutput;
import com.palantir.transforms.lang.java.api.ReadOnlyLogicalFileSystem;
import com.palantir.transforms.lang.java.api.WriteOnlyLogicalFileSystem;
import com.palantir.util.syntacticpath.Paths;
import java.io.IOException;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/**
 * This is an example of unzipping files in parallel using Spark.
 * <p>
 * 这是一个使用 Spark 并行解压文件的示例。
 * The work is distributed to executors.
 * 任务被分配给执行器。
 */
public final class UnzipWithSpark {

    @Compute
    public void compute(FoundryInput zipFiles, FoundryOutput output) throws IOException {
        ReadOnlyLogicalFileSystem inputFileSystem = zipFiles.asFiles().getFileSystem();
        WriteOnlyLogicalFileSystem outputFileSystem = output.getFileSystem();

        // 对输入文件系统中的每个文件进行处理
        inputFileSystem.filesAsDataset().foreach(portableFile -> {
            // "processWith" 用于获取给定输入文件的 InputStream。
            portableFile.processWithThenClose(stream -> {
                try (ZipInputStream zis = new ZipInputStream(stream)) {
                    ZipEntry entry;
                    // 对于 .zip 文件中的每个文件，将其写入到输出文件系统中。
                    while ((entry = zis.getNextEntry()) != null) {
                        outputFileSystem.writeTo(
                                Paths.get(entry.getName()),
                                outputStream -> ByteStreams.copy(zis, outputStream));
                    }
                    return null;
                } catch (IOException e) {
                    // 如果发生 IOException，抛出运行时异常。
                    throw new RuntimeException(e);
                }
            });
        });
    }
}
```

### 解压数据集文件并写入输出DataFrame

此示例以.csv、.gz和.zip文件作为输入。它解压这些文件，然后将文件写入输出DataFrame——此工作是使用Spark并行完成的。

```
Copied!1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
100
101
102
103
104
105
106
107
108
109
110
111
112
113
114
115
116
117
118
119
120
121
122
123
124
125
126
127
128
129
130
131
132
133
134
135
136
137
/*
 * (c) Copyright 2018 Palantir Technologies Inc. All rights reserved.
 */

package com.palantir.transforms.java.examples;

import com.google.common.collect.AbstractIterator;
import com.google.common.io.CharSource;
import com.google.common.io.Closeables;
import com.palantir.spark.binarystream.data.PortableFile;
import com.palantir.transforms.lang.java.api.Compute;
import com.palantir.transforms.lang.java.api.FoundryInput;
import com.palantir.transforms.lang.java.api.FoundryOutput;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.util.Iterator;
import java.util.zip.GZIPInputStream;
import java.util.zip.ZipInputStream;
import org.apache.spark.TaskContext;
import org.apache.spark.api.java.function.FlatMapFunction;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Encoders;
import org.apache.spark.sql.Row;
import org.apache.spark.util.TaskCompletionListener;

/**
 * 这个示例期望输入为.csv/.gz/.zip文件。
 * <p>
 * 它在Spark上并行执行以下操作:
 * <ol>
 *     <li>检测文件类型。</li>
 *     <li>如果文件类型是.gz或.zip，则解压文件。</li>
 *     <li>推断解压后的.csv文件的模式(schema)。</li>
 *     <li>将.csv行的数据集转换为该模式的数据集。</li>
 * </ol>
*/
public final class UnzipWithSparkToDataset {

    @Compute
    public void compute(FoundryInput input, FoundryOutput output) {
        // 获取输入文件的Spark数据集。
        Dataset<PortableFile> files = input.asFiles().getFileSystem().filesAsDataset();

        // 将输入文件的数据集转换为.csv行的数据集。
        Dataset<String> csvDataset = files.flatMap((FlatMapFunction<PortableFile, String>) portableFile ->
                // 从当前输入文件获取InputStream。
                portableFile.convertToIterator(inputStream -> {
                    String fileName = portableFile.getLogicalPath().getFileName().toString();
                    // 检测.gz和.zip文件，并从每个文件中获取行迭代器。
                    if (fileName.endsWith(".gz")) {
                        return new InputStreamCharSource(new GZIPInputStream(inputStream)).getLineIterator();
                    } else if (fileName.endsWith(".zip")) {
                        return new ZipIterator(new ZipInputStream(inputStream));
                    } else {
                        return new InputStreamCharSource(inputStream).getLineIterator();
                    }
                }), Encoders.STRING());

        // 推断模式并将.csv行的数据集转换为该模式的数据集。
        Dataset<Row> dataset = files
                .sparkSession()
                .read()
                .option("inferSchema", "true")
                .csv(csvDataset);
        output.getDataFrameWriter(dataset).write();
    }

    /*
     * 这个ZipIterator假设归档中的所有文件都是具有相同模式的.csv，并属于同一个数据集。
     */
    private static final class ZipIterator extends AbstractIterator<String> {
        private Iterator<String> lineIterator;
        private ZipInputStream zis;

        ZipIterator(ZipInputStream zis) throws IOException {
            this.zis = zis;
            lineIterator = new InputStreamCharSource(zis).getLineIterator();
        }

        @Override
        protected String computeNext() {
            if (!lineIterator.hasNext()) {
                // 如果行迭代器没有下一个元素，检查是否有下一个文件。
                try {
                    // 查找下一个非空的文件。
                    while (zis.getNextEntry() != null) {
                        lineIterator = new InputStreamCharSource(zis).getLineIterator();
                        if (lineIterator.hasNext()) {
                            break;
                        }
                    }
                    return lineIterator.hasNext() ? lineIterator.next() : endOfData();
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
            } else {
                return lineIterator.next();
            }
        }
    }

    private static final class InputStreamCharSource extends CharSource {
        private final Reader inputStream;

        private InputStreamCharSource(InputStream inputStream) {
            this.inputStream = new InputStreamReader(inputStream, StandardCharsets.UTF_8);
        }

        @Override
        public Reader openStream() throws IOException {
            return inputStream;
        }

        @SuppressWarnings("MustBeClosedChecker")
        Iterator<String> getLineIterator() {
            try {
                return super.lines().iterator();
            } catch (IOException e) {
                throw new RuntimeException(e);
            } finally {
                if (TaskContext.get() != null) {
                    // 如果在Spark中运行，当任务完成时关闭流。
                    TaskContext.get().addTaskCompletionListener((TaskCompletionListener) context -> close());
                } else {
                    close();
                }
            }
        }

        private void close() {
            Closeables.closeQuietly(inputStream);
        }
    }
}
```

## 合并数据集文件

此示例以.zip文件作为输入，并将所有输入数据集文件合并为一个.zip文件。请注意，此变换中的计算不是并行化的。

```
Copied!1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
/*
 * (c) Copyright 2018 Palantir Technologies Inc. All rights reserved.
 */
package com.palantir.transforms.java.examples;

import com.google.common.io.ByteStreams;
import com.palantir.transforms.lang.java.api.Compute;
import com.palantir.transforms.lang.java.api.FoundryInput;
import com.palantir.transforms.lang.java.api.FoundryOutput;
import com.palantir.transforms.lang.java.api.ReadOnlyLogicalFileSystem;
import com.palantir.transforms.lang.java.api.WriteOnlyLogicalFileSystem;
import com.palantir.util.syntacticpath.Paths;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

/**
 * 本示例将数据集中所有文件合并为一个大的 .zip 文件。
 * <p>
 * 工作在单线程上完成，因为并行运行较为困难。
 * <p>
 * 警告：通常建议使用 {@link UnzipWithSpark} 和 {@link UnzipWithSparkToDataset} 中的 API 来利用 Spark 的优势。
 * 这是一个难以实现有效并行化的计算示例，因此仅在驱动程序上使用文件系统操作来完成。
 */
public final class ZipOnDriver {

    @Compute
    public void compute(FoundryInput zipFiles, FoundryOutput output) {
        ReadOnlyLogicalFileSystem inputFileSystem = zipFiles.asFiles().getFileSystem();
        WriteOnlyLogicalFileSystem outputFileSystem = output.getFileSystem();

        // 在输出数据集的文件系统中写入名为 "bigzip.zip" 的文件。
        outputFileSystem.writeTo(Paths.get("bigzip.zip"), outputStream -> {
            // 将 OutputStream 包装在 ZipOutputStream 中，以便将每个文件写入同一个 .zip 文件中。
            try (ZipOutputStream zipOutputStream = new ZipOutputStream(outputStream)) {
                // 对于输入数据集的文件系统中的每个文件，读取它，在 "bigzip.zip" 中标记一个新条目，然后复制字节。
                inputFileSystem.listAllFiles().forEach(inputPath -> {
                    inputFileSystem.readFrom(inputPath, inputStream -> {
                        zipOutputStream.putNextEntry(new ZipEntry(inputPath.toString()));
                        ByteStreams.copy(inputStream, zipOutputStream);
                        return null;
                    });
                });
            }
        });
    }
}
```
