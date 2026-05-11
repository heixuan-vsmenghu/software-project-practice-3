package com.example.composeaidemo

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            ComposeAiDemoApp()
        }
    }
}

data class AiRecognitionState(
    val modelName: String = "MobileNet",
    val result: String = "Waiting",
    val confidence: String? = null,
    val inferenceTimeMs: Int? = null,
    val inputSource: String = "等待输入",
)

data class PracticeItem(
    val title: String,
    val summary: String,
    val detail: String = "通过按钮控制状态变化，Compose 会根据状态自动更新界面。",
)

private enum class DemoScreen(val label: String) {
    Practice("布局练习"),
    AiDemo("AI Demo"),
}

private val AppColors = lightColorScheme(
    primary = Color(0xFF2563EB),
    secondary = Color(0xFF0F766E),
    background = Color(0xFFF8FAFC),
    surface = Color.White,
    onPrimary = Color.White,
    onSurface = Color(0xFF0F172A),
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ComposeAiDemoApp(modifier: Modifier = Modifier) {
    var selectedScreen by remember { mutableStateOf(DemoScreen.Practice) }
    val screens = listOf(DemoScreen.Practice, DemoScreen.AiDemo)

    MaterialTheme(colorScheme = AppColors) {
        Scaffold(
            modifier = modifier.fillMaxSize(),
            // 顶部栏：AI 页面显示 LiteRT AI Demo，练习页面显示实验主题。
            topBar = {
                TopAppBar(
                    title = {
                        Text(
                            text = when (selectedScreen) {
                                DemoScreen.Practice -> "Compose 布局实验"
                                DemoScreen.AiDemo -> "LiteRT AI Demo"
                            },
                            fontWeight = FontWeight.SemiBold,
                        )
                    },
                    actions = {
                        TextButton(onClick = { selectedScreen = DemoScreen.AiDemo }) {
                            Text("说明")
                        }
                    },
                    colors = TopAppBarDefaults.topAppBarColors(
                        containerColor = MaterialTheme.colorScheme.surface,
                        titleContentColor = MaterialTheme.colorScheme.onSurface,
                    ),
                )
            },
            containerColor = MaterialTheme.colorScheme.background,
        ) { innerPadding ->
            Column(
                modifier = Modifier
                    .padding(innerPadding)
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState())
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp),
            ) {
                ScreenSwitcher(
                    screens = screens,
                    selectedScreen = selectedScreen,
                    onSelect = { selectedScreen = it },
                )

                when (selectedScreen) {
                    DemoScreen.Practice -> LayoutPracticeScreen()
                    DemoScreen.AiDemo -> AiDemoScreen()
                }
            }
        }
    }
}

@Composable
private fun ScreenSwitcher(
    screens: List<DemoScreen>,
    selectedScreen: DemoScreen,
    onSelect: (DemoScreen) -> Unit,
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        screens.forEach { screen ->
            val buttonModifier = Modifier.weight(1f)
            if (screen == selectedScreen) {
                Button(
                    modifier = buttonModifier,
                    onClick = { onSelect(screen) },
                    shape = RoundedCornerShape(8.dp),
                ) {
                    Text(screen.label)
                }
            } else {
                OutlinedButton(
                    modifier = buttonModifier,
                    onClick = { onSelect(screen) },
                    shape = RoundedCornerShape(8.dp),
                ) {
                    Text(screen.label)
                }
            }
        }
    }
}

@Composable
fun LayoutPracticeScreen(modifier: Modifier = Modifier) {
    var showGuide by remember { mutableStateOf(false) }
    val practiceItems = listOf(
        PracticeItem(
            title = "Hello World",
            summary = "Column 中放入第一张 Card，练习 Text 与 Button 的组合。",
        ),
        PracticeItem(
            title = "Hello Compose",
            summary = "Row 和 Card 一起展示信息，按钮点击后展开更多说明。",
        ),
    )

    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text(
            text = "Compose 布局练习",
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
        )

        practiceItems.forEach { item ->
            PracticeCard(item = item)
        }

        // Box 区域：用于展示后续图片、相机画面或模型输出的预览占位。
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(150.dp)
                .clip(RoundedCornerShape(8.dp))
                .background(Color(0xFFE2E8F0)),
            contentAlignment = Alignment.Center,
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Box(
                    modifier = Modifier
                        .size(42.dp)
                        .clip(CircleShape)
                        .background(Color(0xFF2563EB)),
                )
                Spacer(modifier = Modifier.height(10.dp))
                Text(
                    text = "Box 预览占位区",
                    fontWeight = FontWeight.SemiBold,
                    color = Color(0xFF334155),
                )
            }
        }

        Button(
            onClick = { showGuide = !showGuide },
            shape = RoundedCornerShape(8.dp),
        ) {
            Text(if (showGuide) "隐藏布局说明" else "显示布局说明")
        }

        if (showGuide) {
            Card(
                colors = CardDefaults.cardColors(containerColor = Color(0xFFEFF6FF)),
                shape = RoundedCornerShape(8.dp),
            ) {
                Text(
                    modifier = Modifier.padding(14.dp),
                    text = "本页面把 Column、Row、Box、Text、Button、Card 放在同一张练习页中。" +
                        "按钮状态由 remember + mutableStateOf 保存，点击后界面自动重组。",
                    color = Color(0xFF1E3A8A),
                )
            }
        }
    }
}

@Composable
fun PracticeCard(item: PracticeItem, modifier: Modifier = Modifier) {
    var expanded by remember { mutableStateOf(false) }

    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        shape = RoundedCornerShape(8.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
    ) {
        Column(
            modifier = Modifier.padding(14.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(item.title, fontWeight = FontWeight.Bold)
                    Text(item.summary, style = MaterialTheme.typography.bodyMedium)
                }
                TextButton(onClick = { expanded = !expanded }) {
                    Text(if (expanded) "Show less" else "Show more")
                }
            }
            if (expanded) {
                HorizontalDivider()
                Text(
                    text = item.detail,
                    color = Color(0xFF475569),
                )
            }
        }
    }
}

@Composable
fun AiDemoScreen(modifier: Modifier = Modifier) {
    var state by remember { mutableStateOf(AiRecognitionState()) }
    val modelNames = listOf("MobileNet", "EfficientNet", "LiteRT Demo Model")

    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text(
            text = "面向 AI 应用的 Compose 布局",
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold,
        )

        // 预览区：当前使用 Box 占位，后续可替换为 CameraX PreviewView。
        PreviewBox(inputSource = state.inputSource)

        // 结果卡片：状态对象驱动 UI，空安全用于显示默认占位符。
        ResultCard(state = state)

        // 按钮区：每个 Lambda 都会更新 state，从而触发 Compose 重组。
        ActionButtons(
            onPhoto = {
                state = AiRecognitionState(
                    modelName = "MobileNet",
                    result = "Cat",
                    confidence = "96.2%",
                    inferenceTimeMs = 28,
                    inputSource = "来自相机模拟输入",
                )
            },
            onAlbum = {
                state = AiRecognitionState(
                    modelName = "EfficientNet",
                    result = "Dog",
                    confidence = "91.4%",
                    inferenceTimeMs = 35,
                    inputSource = "来自相册模拟输入",
                )
            },
            onSwitchModel = {
                val nextModel = when (state.modelName) {
                    modelNames[0] -> modelNames[1]
                    modelNames[1] -> modelNames[2]
                    else -> modelNames[0]
                }
                state = state.copy(modelName = nextModel)
            },
            onClear = {
                state = AiRecognitionState()
            },
        )
    }
}

@Composable
fun PreviewBox(inputSource: String, modifier: Modifier = Modifier) {
    Box(
        modifier = modifier
            .fillMaxWidth()
            .height(210.dp)
            .clip(RoundedCornerShape(8.dp))
            .background(Color(0xFFCBD5E1)),
        contentAlignment = Alignment.Center,
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(
                text = "Image / Camera Preview",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = Color(0xFF0F172A),
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = inputSource,
                color = Color(0xFF334155),
            )
        }
    }
}

@Composable
fun ResultCard(state: AiRecognitionState, modifier: Modifier = Modifier) {
    val confidenceText = state.confidence ?: "--"
    val timeText = state.inferenceTimeMs?.let { "$it ms" } ?: "--"
    val rows = listOf(
        "Model" to state.modelName,
        "Result" to state.result,
        "Confidence" to confidenceText,
        "Time" to timeText,
    )

    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        shape = RoundedCornerShape(8.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Text(
                text = "AI Recognition Result",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
            )
            rows.forEach { (label, value) ->
                InfoRow(label = label, value = value)
            }
        }
    }
}

@Composable
fun InfoRow(label: String, value: String, modifier: Modifier = Modifier) {
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            text = "$label:",
            color = Color(0xFF475569),
            modifier = Modifier.weight(1f),
        )
        Text(
            text = value,
            fontWeight = FontWeight.SemiBold,
            textAlign = TextAlign.End,
            modifier = Modifier.weight(1f),
        )
    }
}

@Composable
fun ActionButtons(
    onPhoto: () -> Unit,
    onAlbum: () -> Unit,
    onSwitchModel: () -> Unit,
    onClear: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Button(
                modifier = Modifier.weight(1f),
                onClick = onPhoto,
                shape = RoundedCornerShape(8.dp),
            ) {
                Text("拍照识别")
            }
            Button(
                modifier = Modifier.weight(1f),
                onClick = onAlbum,
                shape = RoundedCornerShape(8.dp),
            ) {
                Text("相册导入")
            }
        }
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            OutlinedButton(
                modifier = Modifier.weight(1f),
                onClick = onSwitchModel,
                shape = RoundedCornerShape(8.dp),
            ) {
                Text("切换模型")
            }
            OutlinedButton(
                modifier = Modifier.weight(1f),
                onClick = onClear,
                shape = RoundedCornerShape(8.dp),
            ) {
                Text("清空结果")
            }
        }
    }
}

@Preview(showBackground = true, widthDp = 390, heightDp = 820)
@Composable
fun ComposeAiDemoAppPreview() {
    ComposeAiDemoApp()
}

@Preview(showBackground = true, widthDp = 390, heightDp = 820)
@Composable
fun AiDemoScreenPreview() {
    MaterialTheme(colorScheme = AppColors) {
        Surface(color = MaterialTheme.colorScheme.background) {
            AiDemoScreen(modifier = Modifier.padding(16.dp))
        }
    }
}
